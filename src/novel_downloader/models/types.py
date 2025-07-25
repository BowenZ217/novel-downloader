#!/usr/bin/env python3
"""
novel_downloader.models.types
-----------------------------

"""

from typing import Literal

ModeType = Literal["browser", "session"]
SplitMode = Literal["book", "volume"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR"]
BrowserType = Literal["chromium", "firefox", "webkit"]
