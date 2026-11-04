#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""针对 issue #4 残留问题的 publish_time 提取测试"""

import unittest
from bs4 import BeautifulSoup

from wespy.main import ArticleFetcher


class TestPublishTimeExtraction(unittest.TestCase):

    def setUp(self):
        self.fetcher = ArticleFetcher()

    def test_js_decode_form(self):
        html = """
        <html><body>
        <h1 class="rich_media_title">title</h1>
        <script>var ret = {create_time: JsDecode('2024-01-02 10:30')};</script>
        </body></html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        info = self.fetcher._extract_wechat_info(soup)
        self.assertEqual(info['publish_time'], '2024-01-02 10:30')

    def test_plain_quoted_form(self):
        html = """
        <html><body>
        <h1 class="rich_media_title">title</h1>
        <script>var ret = {create_time: '2026-02-10 13:13', ori_create_time: '1770700432' * 1};</script>
        </body></html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        info = self.fetcher._extract_wechat_info(soup)
        self.assertEqual(info['publish_time'], '2026-02-10 13:13')

    def test_var_ct_fallback(self):
        html = """
        <html><body>
        <h1 class="rich_media_title">title</h1>
        <script>var ct = "1770700432";</script>
        </body></html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        info = self.fetcher._extract_wechat_info(soup)
        self.assertEqual(info['publish_time'], '2026-02-10 13:13')


if __name__ == '__main__':
    unittest.main()
