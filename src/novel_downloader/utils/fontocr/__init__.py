#!/usr/bin/env python3
"""
novel_downloader.utils.fontocr
------------------------------

Utilities for font-based OCR, primarily used to decode custom font obfuscation

Supports:
- Font rendering and perceptual hash matching
- PaddleOCR-based character recognition
- Frequency-based scoring for ambiguous results
- Debugging and font mapping persistence

Exposes the selected OCR engine version via `FontOCR`.
"""

__all__ = ["FontOCR"]
__version__ = "3.0"

# from .ocr_v1 import FontOCRV1 as FontOCR
# from .ocr_v2 import FontOCRV2 as FontOCR
from .ocr_v3 import FontOCRV3 as FontOCR
