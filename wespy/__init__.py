"""
WeSpy - Web Article Scraper
A Python tool for fetching and converting web articles to Markdown format.
"""

__version__ = "0.1.5"
__author__ = "tianchang"
__description__ = "A tool for fetching web articles and converting them to Markdown"

from .main import ArticleFetcher

__all__ = ['ArticleFetcher']