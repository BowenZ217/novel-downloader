#!/usr/bin/env python3
"""
novel_downloader.core.exporters.linovelib.epub
----------------------------------------------

Contains the logic for exporting novel content as a single `.epub` file.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from novel_downloader.core.exporters.epub_util import (
    build_epub_chapter,
    download_cover,
    finalize_export,
    inline_remote_images,
    prepare_builder,
)
from novel_downloader.utils import (
    download,
    get_cleaner,
)
from novel_downloader.utils.constants import (
    DEFAULT_HEADERS,
    DEFAULT_IMAGE_SUFFIX,
)
from novel_downloader.utils.epub import (
    Chapter,
    Volume,
)

if TYPE_CHECKING:
    from .main_exporter import LinovelibExporter

_IMG_HEADERS = DEFAULT_HEADERS.copy()
_IMG_HEADERS["Referer"] = "https://www.linovelib.com/"


def export_whole_book(
    exporter: LinovelibExporter,
    book_id: str,
) -> None:
    """
    Export a single novel (identified by `book_id`) to an EPUB file.

    This function will:
      1. Load `book_info.json` for metadata.
      2. Generate introductory HTML and optionally include the cover image.
      3. Initialize the EPUB container.
      4. Iterate through volumes and chapters in volume-batches, convert each to XHTML.
      5. Assemble the spine, TOC, CSS and write out the final `.epub`.

    :param exporter: The exporter instance, carrying config and path info.
    :param book_id: Identifier of the novel (used as subdirectory name).
    """
    TAG = "[exporter]"
    config = exporter._config

    raw_base = exporter._raw_data_dir / book_id
    img_dir = raw_base / "images"
    out_dir = exporter.output_dir

    img_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    cleaner = get_cleaner(
        enabled=config.clean_text,
        config=config.cleaner_cfg,
    )

    # --- Load book_info.json ---
    book_info = exporter._load_book_info(book_id)
    if not book_info:
        return

    book_name = book_info.get("book_name", book_id)
    book_author = book_info.get("author", "")

    exporter.logger.info(
        "%s Starting EPUB generation: %s (ID: %s)", TAG, book_name, book_id
    )

    # --- Generate intro + cover ---
    cover_path = download_cover(
        book_info.get("cover_url", ""),
        raw_base,
        config.include_cover,
        exporter.logger,
        TAG,
        headers=_IMG_HEADERS,
    )

    # --- Initialize EPUB ---
    book, main_css = prepare_builder(
        site_name=exporter.site,
        book_id=book_id,
        title=book_name,
        author=book_author,
        description=book_info.get("summary", ""),
        subject=book_info.get("subject", []),
        serial_status=book_info.get("serial_status", ""),
        word_count=book_info.get("word_count", ""),
        cover_path=cover_path,
    )

    # --- Compile chapters ---
    volumes = book_info.get("volumes", [])
    if not volumes:
        exporter.logger.warning("%s No volumes found in metadata.", TAG)

    for vol_index, vol in enumerate(volumes, start=1):
        raw_name = vol.get("volume_name", "")
        raw_name = raw_name.replace(book_name, "").strip()
        vol_name = raw_name or f"Volume {vol_index}"
        exporter.logger.info("Processing volume %d: %s", vol_index, vol_name)

        # Batch-fetch chapters for this volume
        chap_ids = [
            chap.get("chapterId")
            for chap in vol.get("chapters", [])
            if chap.get("chapterId")
        ]
        chap_map = exporter._get_chapters(book_id, chap_ids)

        vol_cover: Path | None = None
        vol_cover_url = vol.get("volume_cover", "")
        if vol_cover_url:
            vol_cover = download(
                vol_cover_url,
                img_dir,
                on_exist="skip",
                default_suffix=DEFAULT_IMAGE_SUFFIX,
                headers=_IMG_HEADERS,
            )

        curr_vol = Volume(
            id=f"vol_{vol_index}",
            title=vol_name,
            intro=cleaner.clean_content(vol.get("volume_intro", "")),
            cover=vol_cover,
        )

        for chap_meta in vol.get("chapters", []):
            chap_id = chap_meta.get("chapterId")
            if not chap_id:
                exporter.logger.warning(
                    "%s Missing chapterId, skipping: %s",
                    TAG,
                    chap_meta,
                )
                continue

            chap_title = cleaner.clean_title(chap_meta.get("title", ""))
            data = chap_map.get(chap_id)
            if not data:
                exporter.logger.info(
                    "%s Missing chapter: %s (%s), skipping.",
                    TAG,
                    chap_title,
                    chap_id,
                )
                continue

            title = cleaner.clean_title(data.get("title", chap_title)) or chap_id
            content = cleaner.clean_content(data.get("content", ""))
            content = inline_remote_images(
                book,
                content,
                img_dir,
                headers=_IMG_HEADERS,
            )

            chap_html = build_epub_chapter(
                title=title,
                paragraphs=content,
                extras={},
            )
            curr_vol.add_chapter(
                Chapter(
                    id=f"c_{chap_id}",
                    filename=f"c{chap_id}.xhtml",
                    title=title,
                    content=chap_html,
                    css=[main_css],
                )
            )

        book.add_volume(curr_vol)

    # --- 5. Finalize EPUB ---
    out_name = exporter.get_filename(
        title=book_name,
        author=book_info.get("author"),
        ext="epub",
    )
    finalize_export(
        book=book,
        out_dir=out_dir,
        filename=out_name,
        logger=exporter.logger,
        tag=TAG,
    )
    return


def export_by_volume(
    exporter: LinovelibExporter,
    book_id: str,
) -> None:
    """
    Export each volume of a novel as a separate EPUB file.

    Steps:
      1. Load metadata from `book_info.json`.
      2. For each volume:
         a. Clean the volume title and determine output filename.
         b. Batch-fetch all chapters in this volume to minimize SQLite overhead.
         c. Initialize an EPUB builder for the volume, including cover and intro.
         d. For each chapter: clean title & content, inline remote images.
         e. Finalize and write the volume EPUB.

    :param book_id: Identifier of the novel (used as subdirectory name).
    """
    TAG = "[exporter]"
    config = exporter._config

    raw_base = exporter._raw_data_dir / book_id
    img_dir = raw_base / "images"
    out_dir = exporter.output_dir

    img_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    cleaner = get_cleaner(
        enabled=config.clean_text,
        config=config.cleaner_cfg,
    )

    # --- Load book_info.json ---
    book_info = exporter._load_book_info(book_id)
    if not book_info:
        return

    book_name = book_info.get("book_name", book_id)
    book_author = book_info.get("author", "")
    book_summary = book_info.get("summary", "")

    exporter.logger.info(
        "%s Starting EPUB generation: %s (ID: %s)", TAG, book_name, book_id
    )

    # --- Compile columes ---
    volumes = book_info.get("volumes", [])
    if not volumes:
        exporter.logger.warning("%s No volumes found in metadata.", TAG)

    for vol_index, vol in enumerate(volumes, start=1):
        raw_name = vol.get("volume_name", "")
        raw_name = cleaner.clean_title(raw_name.replace(book_name, ""))
        vol_name = raw_name or f"Volume {vol_index}"

        # Batch-fetch chapters for this volume
        chap_ids = [
            chap.get("chapterId")
            for chap in vol.get("chapters", [])
            if chap.get("chapterId")
        ]
        chap_map = exporter._get_chapters(book_id, chap_ids)

        vol_cover: Path | None = None
        vol_cover_url = vol.get("volume_cover", "")
        if config.include_cover and vol_cover_url:
            vol_cover = download(
                vol_cover_url,
                img_dir,
                headers=_IMG_HEADERS,
                on_exist="skip",
                default_suffix=DEFAULT_IMAGE_SUFFIX,
            )

        book, main_css = prepare_builder(
            site_name=exporter.site,
            book_id=book_id,
            title=book_name,
            author=book_author,
            description=vol.get("volume_intro") or book_summary,
            subject=book_info.get("subject", []),
            serial_status=vol.get("serial_status", ""),
            word_count=vol.get("word_count", ""),
            cover_path=vol_cover,
        )

        for chap_meta in vol.get("chapters", []):
            chap_id = chap_meta.get("chapterId")
            if not chap_id:
                exporter.logger.warning(
                    "%s Missing chapterId, skipping: %s",
                    TAG,
                    chap_meta,
                )
                continue

            chap_title = cleaner.clean_title(chap_meta.get("title", ""))
            data = chap_map.get(chap_id)
            if not data:
                exporter.logger.info(
                    "%s Missing chapter: %s (%s), skipping.",
                    TAG,
                    chap_title,
                    chap_id,
                )
                continue

            title = cleaner.clean_title(data.get("title", chap_title)) or chap_id
            content = cleaner.clean_content(data.get("content", ""))
            content = inline_remote_images(
                book,
                content,
                img_dir,
                headers=_IMG_HEADERS,
            )
            chap_html = build_epub_chapter(
                title=title,
                paragraphs=content,
                extras={},
            )
            book.add_chapter(
                Chapter(
                    id=f"c_{chap_id}",
                    filename=f"c{chap_id}.xhtml",
                    title=title,
                    content=chap_html,
                    css=[main_css],
                )
            )

        out_name = exporter.get_filename(
            title=vol_name,
            author=book_info.get("author"),
            ext="epub",
        )
        finalize_export(
            book=book,
            out_dir=out_dir,
            filename=out_name,
            logger=exporter.logger,
            tag=TAG,
        )
    return
