#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取文章内容的脚本
支持从URL获取网页内容并转换为Markdown格式
"""

import os
import sys
import re
import requests
import urllib.parse
from bs4 import BeautifulSoup
import time
import json
import argparse
from wespy.juejin import JuejinFetcher

class WeChatAlbumFetcher:
    """微信公众号专辑文章列表获取器"""

    def __init__(self):
        self.session = requests.Session()
        # 使用微信浏览器的请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.5',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://mp.weixin.qq.com/'
        })

    def is_album_url(self, url):
        """检查是否为微信专辑URL"""
        return 'mp.weixin.qq.com/mp/appmsgalbum' in url

    def parse_album_info(self, album_url):
        """解析专辑URL获取基本信息"""
        try:
            from urllib.parse import urlparse, parse_qs
            query = parse_qs(urlparse(album_url).query)

            biz = query.get('__biz', [''])[0]
            action = query.get('action', [''])[0]
            album_id = query.get('album_id', [''])[0]

            if not biz or not action or not album_id:
                return None

            return {
                'biz': biz,
                'action': action,
                'album_id': album_id,
                'original_url': album_url
            }
        except Exception as e:
            print(f"解析专辑URL失败: {e}")
            return None

    def fetch_album_articles(self, album_url, max_articles=None):
        """
        获取专辑中的所有文章列表

        Args:
            album_url (str): 微信专辑URL
            max_articles (int, optional): 最大获取文章数量，None表示获取所有

        Returns:
            list: 文章信息列表
        """
        album_info = self.parse_album_info(album_url)
        if not album_info:
            print("无法解析专辑URL")
            return []

        print(f"正在获取专辑文章列表...")
        print(f"专辑ID: {album_info['album_id']}")

        articles = []
        begin_msgid = 0
        begin_itemidx = 0
        count = 10  # 每页获取数量

        while True:
            # 构建API请求URL
            api_url = f"https://mp.weixin.qq.com/mp/appmsgalbum"
            params = {
                'action': 'getalbum',
                '__biz': album_info['biz'],
                'album_id': album_info['album_id'],
                'count': str(count),
                'begin_msgid': str(begin_msgid),
                'begin_itemidx': str(begin_itemidx),
                'f': 'json'
            }

            try:
                response = self.session.get(api_url, params=params, timeout=30)
                response.raise_for_status()

                # 解析JSON响应
                data = response.json()

                # 检查响应状态
                if data.get('base_resp', {}).get('ret') != 0:
                    print(f"API返回错误: {data.get('base_resp', {})}")
                    break

                # 提取文章列表
                album_resp = data.get('getalbum_resp', {})
                article_list = album_resp.get('article_list', [])

                if not article_list:
                    print("没有更多文章了")
                    break

                # 处理文章信息
                for article_data in article_list:
                    article_info = {
                        'title': article_data.get('title', ''),
                        'url': article_data.get('url', ''),
                        'msgid': article_data.get('msgid', ''),
                        'create_time': article_data.get('create_time', ''),
                        'cover_img': article_data.get('cover_img_1_1', ''),
                        'itemidx': article_data.get('itemidx', ''),
                        'key': article_data.get('key', '')
                    }

                    # 移除URL中的#rd后缀（如果有）
                    if article_info['url'].endswith('#rd'):
                        article_info['url'] = article_info['url'][:-3]

                    articles.append(article_info)

                    # 检查是否达到最大文章数量限制
                    if max_articles and len(articles) >= max_articles:
                        print(f"已达到最大文章数量限制: {max_articles}")
                        return articles

                print(f"已获取 {len(articles)} 篇文章...")

                # 检查是否还有更多文章
                continue_flag = album_resp.get('continue_flag', '0')
                if continue_flag != '1':
                    print("已获取所有文章")
                    break

                # 更新下一页的起始位置
                if article_list:
                    last_article = article_list[-1]
                    begin_msgid = last_article.get('msgid', 0)
                    begin_itemidx = last_article.get('itemidx', 0)

                # 添加延迟避免请求过快
                time.sleep(0.5)

            except Exception as e:
                print(f"获取文章列表失败: {e}")
                break

        print(f"总共获取到 {len(articles)} 篇文章")
        return articles

class ArticleFetcher:
    def __init__(self):
        self.session = requests.Session()
        # 设置请求头，模拟浏览器
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        # 初始化掘金获取器
        self.juejin_fetcher = JuejinFetcher()
        # 初始化微信专辑获取器
        self.album_fetcher = WeChatAlbumFetcher()

    def fetch_album_articles(self, album_url, output_dir="articles", max_articles=None, save_html=False, save_json=False, save_markdown=True):
        """
        批量获取微信专辑中的所有文章

        Args:
            album_url (str): 微信专辑URL
            output_dir (str): 输出目录
            max_articles (int, optional): 最大获取文章数量，None表示获取所有
            save_html (bool): 是否保存HTML文件
            save_json (bool): 是否保存JSON文件
            save_markdown (bool): 是否保存Markdown文件

        Returns:
            list: 成功获取的文章信息列表
        """
        # 获取专辑文章列表
        articles = self.album_fetcher.fetch_album_articles(album_url, max_articles)

        if not articles:
            print("没有获取到任何文章")
            return []

        print(f"\n开始批量下载 {len(articles)} 篇文章...")

        successful_articles = []
        failed_articles = []

        # 创建专辑专用目录
        album_name = f"album_{int(time.time())}"
        album_output_dir = os.path.join(output_dir, album_name)

        for i, article in enumerate(articles, 1):
            print(f"\n[{i}/{len(articles)}] 正在下载: {article['title']}")

            try:
                # 下载单篇文章
                article_result = self.fetch_article(
                    article['url'],
                    album_output_dir,
                    save_html,
                    save_json,
                    save_markdown
                )

                if article_result:
                    # 合并专辑信息
                    article_result.update({
                        'album_title': article.get('title', ''),
                        'album_url': album_url,
                        'msgid': article.get('msgid', ''),
                        'create_time': article.get('create_time', ''),
                        'cover_img': article.get('cover_img', '')
                    })
                    successful_articles.append(article_result)
                    print(f"✅ 下载成功")
                else:
                    print(f"❌ 下载失败")
                    failed_articles.append(article)

                # 添加延迟避免请求过快
                time.sleep(1)

            except Exception as e:
                print(f"❌ 下载失败: {e}")
                failed_articles.append(article)

        # 保存专辑汇总信息
        self._save_album_summary(successful_articles, failed_articles, album_url, output_dir, album_name)

        print(f"\n批量下载完成!")
        print(f"成功: {len(successful_articles)} 篇")
        print(f"失败: {len(failed_articles)} 篇")
        print(f"文章保存在: {album_output_dir}")

        return successful_articles

    def _save_album_summary(self, successful_articles, failed_articles, album_url, output_dir, album_name):
        """保存专辑下载汇总信息"""
        summary = {
            'album_url': album_url,
            'download_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'statistics': {
                'total_count': len(successful_articles) + len(failed_articles),
                'successful_count': len(successful_articles),
                'failed_count': len(failed_articles)
            },
            'successful_articles': [
                {
                    'title': article.get('title', ''),
                    'author': article.get('author', ''),
                    'url': article.get('url', ''),
                    'msgid': article.get('msgid', ''),
                    'create_time': article.get('create_time', '')
                }
                for article in successful_articles
            ],
            'failed_articles': [
                {
                    'title': article.get('title', ''),
                    'url': article.get('url', ''),
                    'msgid': article.get('msgid', ''),
                    'error': '下载失败'
                }
                for article in failed_articles
            ]
        }

        summary_file = os.path.join(output_dir, f"{album_name}_summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        print(f"专辑汇总信息已保存: {summary_file}")

    def fetch_article(self, url, output_dir="articles", save_html=False, save_json=False, save_markdown=True):
        """
        获取文章内容
        
        Args:
            url (str): 文章URL
            output_dir (str): 输出目录
            save_html (bool): 是否保存HTML文件
            save_json (bool): 是否保存JSON文件
            save_markdown (bool): 是否保存Markdown文件
        
        Returns:
            dict: 包含文章信息的字典
        """
        try:
            # 特殊处理微信专辑URL
            if self.album_fetcher.is_album_url(url):
                print("检测到微信专辑URL，将批量下载专辑中的所有文章")
                return self.fetch_album_articles(url, output_dir, max_articles=10, save_html=save_html, save_json=save_json, save_markdown=save_markdown)
            # 特殊处理微信公众号链接
            elif 'mp.weixin.qq.com' in url:
                return self._fetch_wechat_article(url, output_dir, save_html, save_json, save_markdown)
            # 特殊处理掘金链接
            elif 'juejin.cn' in url:
                return self.juejin_fetcher.fetch_article(url, output_dir, save_html, save_json, save_markdown)
            else:
                return self._fetch_general_article(url, output_dir, save_html, save_json, save_markdown)
                
        except Exception as e:
            print(f"获取文章失败: {e}")
            return None
    
    def _fetch_wechat_article(self, url, output_dir, save_html=False, save_json=False, save_markdown=True):
        """获取微信公众号文章"""
        print(f"正在获取微信文章: {url}")
        
        # 设置微信特定的请求头
        headers = self.session.headers.copy()
        headers['Referer'] = 'https://mp.weixin.qq.com/'
        
        response = self.session.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取文章信息
        article_info = self._extract_wechat_info(soup)
        article_info['url'] = url
        article_info['html_content'] = response.text
        
        # 保存文章
        self._save_article(article_info, output_dir, save_html, save_json, save_markdown)
        
        return article_info
    
    def _fetch_general_article(self, url, output_dir, save_html=False, save_json=False, save_markdown=True):
        """获取普通网页文章"""
        print(f"正在获取文章: {url}")
        
        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        
        # 尝试检测编码
        if response.encoding == 'ISO-8859-1':
            response.encoding = response.apparent_encoding or 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取文章信息
        article_info = self._extract_general_info(soup)
        article_info['url'] = url
        article_info['html_content'] = response.text
        
        # 保存文章
        self._save_article(article_info, output_dir, save_html, save_json, save_markdown)
        
        return article_info
    
    def _extract_wechat_info(self, soup):
        """提取微信文章信息"""
        info = {}
        
        # 标题
        title_elem = soup.find('h1', {'class': 'rich_media_title'}) or soup.find('h1')
        info['title'] = title_elem.get_text().strip() if title_elem else "未知标题"
        
        # 作者
        author_elem = (soup.find('a', {'id': 'js_name'}) or 
                      soup.find('a', {'class': 'profile_nickname'}) or 
                      soup.find('span', {'class': 'profile_nickname'}))
        info['author'] = author_elem.get_text().strip().replace('\n', '').replace('\r', '').replace('\t', '') if author_elem else "未知作者"
        
        # 发布时间
        time_elem = soup.find('em', {'id': 'publish_time'}) or soup.find('span', {'class': 'publish_time'})
        info['publish_time'] = time_elem.get_text().strip() if time_elem else ""
        
        # 内容区域
        content_elem = soup.find('div', {'id': 'js_content'})
        if content_elem:
            info['content_html'] = str(content_elem)
            info['content_text'] = content_elem.get_text().strip()
        else:
            info['content_html'] = ""
            info['content_text'] = ""
        
        return info
    
    def _extract_general_info(self, soup):
        """提取普通网页信息"""
        info = {}
        
        # 标题 - 尝试多种方式获取
        title_elem = (soup.find('title') or 
                     soup.find('h1') or 
                     soup.find('h2') or
                     soup.find('meta', {'property': 'og:title'}))
        
        if title_elem:
            if title_elem.name == 'meta':
                info['title'] = title_elem.get('content', '').strip()
            else:
                info['title'] = title_elem.get_text().strip()
        else:
            info['title'] = "未知标题"
        
        # 作者
        author_elem = (soup.find('meta', {'name': 'author'}) or
                      soup.find('span', {'class': re.compile(r'author', re.I)}) or
                      soup.find('div', {'class': re.compile(r'author', re.I)}) or
                      soup.find('a', {'id': 'js_name'}))
        
        if author_elem:
            if author_elem.name == 'meta':
                info['author'] = author_elem.get('content', '').strip()
            else:
                info['author'] = author_elem.get_text().strip()
        else:
            info['author'] = "未知作者"
        
        # 发布时间
        time_elem = (soup.find('time') or
                    soup.find('span', {'class': re.compile(r'time|date', re.I)}) or
                    soup.find('meta', {'property': 'article:published_time'}))
        
        if time_elem:
            if time_elem.name == 'meta':
                info['publish_time'] = time_elem.get('content', '').strip()
            else:
                info['publish_time'] = time_elem.get_text().strip()
        else:
            info['publish_time'] = ""
        
        # 内容区域 - 尝试多种选择器
        content_selectors = [
            'article',
            '.article-content',
            '.content',
            '.post-content',
            '.entry-content',
            '#content',
            '.main-content',
            'main'
        ]
        
        content_elem = None
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                break
        
        if not content_elem:
            # 如果没找到特定内容区域，使用body
            content_elem = soup.find('body')
        
        if content_elem:
            info['content_html'] = str(content_elem)
            info['content_text'] = content_elem.get_text().strip()
        else:
            info['content_html'] = ""
            info['content_text'] = ""
        
        return info
    
    def _save_article(self, article_info, output_dir, save_html=False, save_json=False, save_markdown=True):
        """保存文章到文件"""
        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 生成安全的文件名
        safe_title = re.sub(r'[<>:"/\\|?*]', '_', article_info['title'])[:50]
        timestamp = int(time.time())
        
        saved_files = []
        
        # 保存HTML文件
        if save_html:
            html_filename = f"{safe_title}_{timestamp}.html"
            html_path = os.path.join(output_dir, html_filename)
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(article_info['html_content'])
            
            print(f"HTML文件已保存: {html_path}")
            saved_files.append(('HTML', html_path))
        
        # 保存文章信息为JSON
        if save_json:
            info_filename = f"{safe_title}_{timestamp}_info.json"
            info_path = os.path.join(output_dir, info_filename)
            
            info_to_save = {
                'title': article_info['title'],
                'author': article_info['author'],
                'publish_time': article_info['publish_time'],
                'url': article_info['url'],
                'html_file': f"{safe_title}_{timestamp}.html" if save_html else None,
                'fetch_time': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            with open(info_path, 'w', encoding='utf-8') as f:
                json.dump(info_to_save, f, ensure_ascii=False, indent=2)
            
            print(f"文章信息已保存: {info_path}")
            saved_files.append(('JSON', info_path))
        
        # 转换为Markdown (默认保存)
        if save_markdown:
            try:
                markdown_content = self._convert_to_markdown(article_info['content_html'])
                md_filename = f"{safe_title}_{timestamp}.md"
                md_path = os.path.join(output_dir, md_filename)
                
                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(f"# {article_info['title']}\n\n")
                    f.write(f"**作者**: {article_info['author']}\n")
                    f.write(f"**发布时间**: {article_info['publish_time']}\n")
                    f.write(f"**原文链接**: {article_info['url']}\n\n")
                    f.write("---\n\n")
                    f.write(markdown_content)
                
                print(f"Markdown文件已保存: {md_path}")
                saved_files.append(('Markdown', md_path))
                
            except Exception as e:
                print(f"转换Markdown失败: {e}")
        
        return saved_files
    
    def _convert_to_markdown(self, html_content):
        """将HTML内容转换为Markdown"""
        if not html_content:
            return ""
        
        soup = BeautifulSoup(html_content, 'html.parser')
        return self._html_to_markdown_recursive(soup)
    
    def _html_to_markdown_recursive(self, element):
        """递归转换HTML元素为Markdown"""
        markdown = ""
        
        for child in element.children:
            if child.name is None:  # 文本节点
                text = str(child).strip()
                if text:
                    markdown += text
            elif child.name == 'br':
                markdown += '\n'
            elif child.name in ['p', 'div', 'section']:
                content = self._html_to_markdown_recursive(child).strip()
                if content:
                    markdown += '\n\n' + content + '\n'
            elif child.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                level = int(child.name[1])
                content = self._html_to_markdown_recursive(child).strip()
                if content:
                    markdown += '\n' + '#' * level + ' ' + content + '\n'
            elif child.name in ['strong', 'b']:
                content = self._html_to_markdown_recursive(child).strip()
                if content:
                    markdown += '**' + content + '**'
            elif child.name in ['em', 'i']:
                content = self._html_to_markdown_recursive(child).strip()
                if content:
                    markdown += '*' + content + '*'
            elif child.name == 'img':
                src = child.get('data-src') or child.get('src', '')
                alt = child.get('alt', '')
                if src:
                    # 使用代理服务处理图片防盗链
                    proxy_src = self._get_proxy_image_url(src)
                    markdown += f'\n![{alt}]({proxy_src})\n'
            elif child.name == 'a':
                href = child.get('href', '')
                text = self._html_to_markdown_recursive(child).strip()
                if href and text:
                    markdown += f'[{text}]({href})'
                elif text:
                    markdown += text
            elif child.name in ['ul', 'ol']:
                list_content = self._convert_list_to_markdown(child)
                if list_content:
                    markdown += '\n' + list_content + '\n'
            elif child.name == 'code':
                # 处理行内代码
                code_content = child.get_text().strip()
                if code_content:
                    markdown += '`' + code_content + '`'
            elif child.name == 'pre':
                # 处理代码块
                code_content = self._extract_code_from_pre(child)
                language = self._detect_code_language(child)
                if code_content:
                    if language:
                        markdown += f'\n```{language}\n{code_content}\n```\n'
                    else:
                        markdown += f'\n```\n{code_content}\n```\n'
            else:
                # 递归处理其他元素
                content = self._html_to_markdown_recursive(child)
                markdown += content
        
        return markdown
    
    def _convert_list_to_markdown(self, list_element):
        """转换列表为Markdown"""
        markdown = ""
        items = list_element.find_all('li', recursive=False)
        
        for i, item in enumerate(items):
            content = self._html_to_markdown_recursive(item).strip()
            if content:
                if list_element.name == 'ol':
                    markdown += f"{i+1}. {content}\n"
                else:
                    markdown += f"- {content}\n"
        
        return markdown
    
    def _extract_code_from_pre(self, pre_element):
        """从pre元素中提取代码内容"""
        # 查找内部的code元素
        code_elem = pre_element.find('code')
        if code_elem:
            # 如果有code元素，提取其内容
            code_content = code_elem.get_text()
        else:
            # 如果没有code元素，直接提取pre的内容
            code_content = pre_element.get_text()
        
        # 清理代码内容
        code_content = code_content.strip()
        
        # 移除多余的空行，保持代码格式
        lines = code_content.split('\n')
        cleaned_lines = []
        for line in lines:
            if line.strip() or cleaned_lines:  # 保留非空行或已有内容时的空行
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _detect_code_language(self, pre_element):
        """检测代码语言"""
        # 检查pre元素的class
        pre_classes = pre_element.get('class', [])
        
        # 常见语言映射
        language_mapping = {
            'language-python': 'python',
            'language-javascript': 'javascript',
            'language-js': 'javascript',
            'language-typescript': 'typescript',
            'language-ts': 'typescript',
            'language-java': 'java',
            'language-cpp': 'cpp',
            'language-c++': 'cpp',
            'language-c': 'c',
            'language-csharp': 'csharp',
            'language-c#': 'csharp',
            'language-go': 'go',
            'language-rust': 'rust',
            'language-php': 'php',
            'language-ruby': 'ruby',
            'language-python3': 'python',
            'language-py': 'python',
            'language-html': 'html',
            'language-css': 'css',
            'language-scss': 'scss',
            'language-sass': 'sass',
            'language-json': 'json',
            'language-xml': 'xml',
            'language-yaml': 'yaml',
            'language-yml': 'yaml',
            'language-sql': 'sql',
            'language-bash': 'bash',
            'language-shell': 'bash',
            'language-sh': 'bash',
            'language-markdown': 'markdown',
            'language-md': 'markdown',
            'language-dockerfile': 'dockerfile',
            'language-docker': 'dockerfile',
            'language-git': 'git',
            'language-diff': 'diff',
            'language-text': 'text',
            'language-plain': 'text',
        }
        
        # 检查class中是否包含语言信息
        for class_name in pre_classes:
            if class_name in language_mapping:
                return language_mapping[class_name]
            # 也检查部分匹配
            for key, lang in language_mapping.items():
                if key in class_name:
                    return lang
        
        # 检查内部code元素的class
        code_elem = pre_element.find('code')
        if code_elem:
            code_classes = code_elem.get('class', [])
            for class_name in code_classes:
                if class_name in language_mapping:
                    return language_mapping[class_name]
                # 也检查部分匹配
                for key, lang in language_mapping.items():
                    if key in class_name:
                        return lang
        
        # 检查data-language属性
        data_lang = pre_element.get('data-language') or pre_element.get('lang')
        if data_lang:
            return data_lang.lower()
        
        # 检查内部code元素的data-language属性
        if code_elem:
            data_lang = code_elem.get('data-language') or code_elem.get('lang')
            if data_lang:
                return data_lang.lower()
        
        # 如果没有检测到语言，返回None
        return None
    
    def _get_proxy_image_url(self, original_url):
        """获取代理图片URL，解决防盗链问题"""
        if not original_url or not original_url.startswith('http'):
            return original_url
        
        encoded_url = urllib.parse.quote(original_url, safe='')
        base_url = f"https://images.weserv.nl/?url={encoded_url}"
        
        # GIF图片添加特殊参数
        if 'gif' in original_url.lower() or 'wx_fmt=gif' in original_url.lower():
            base_url += "&n=-1"
        
        return base_url

def main():
    parser = argparse.ArgumentParser(description='获取文章内容并转换为Markdown')
    parser.add_argument('url', nargs='?', help='文章URL')
    parser.add_argument('-o', '--output', default='articles', help='输出目录 (默认: articles)')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细信息')
    parser.add_argument('--html', action='store_true', help='同时保存HTML文件')
    parser.add_argument('--json', action='store_true', help='同时保存JSON信息文件')
    parser.add_argument('--all', action='store_true', help='保存所有格式文件 (HTML, JSON, Markdown)')
    parser.add_argument('--max-articles', type=int, help='微信专辑最大下载文章数量 (默认: 10)')
    parser.add_argument('--album-only', action='store_true', help='仅获取专辑文章列表，不下载内容')
    
    args = parser.parse_args()
    
    # 如果没有提供URL，进入交互模式
    if not args.url:
        print("文章获取工具")
        print("=" * 40)
        url = input("请输入文章URL: ").strip()
        if not url:
            print("URL不能为空!")
            sys.exit(1)
        output_dir = input("输出目录 (回车使用默认 'articles'): ").strip() or 'articles'
        
        # 交互模式询问输出格式
        print("\n输出格式选择:")
        print("1. 仅 Markdown (默认)")
        print("2. Markdown + HTML")
        print("3. Markdown + JSON")
        print("4. 全部格式 (HTML + JSON + Markdown)")
        
        choice = input("请选择 (1-4, 回车使用默认1): ").strip() or '1'
        
        save_html = False
        save_json = False
        save_markdown = True
        
        if choice == '2':
            save_html = True
        elif choice == '3':
            save_json = True
        elif choice == '4':
            save_html = True
            save_json = True

        # 交互模式默认值
        max_articles = 10
        album_only = False

    else:
        url = args.url
        output_dir = args.output
        
        # 命令行模式处理输出格式
        if args.all:
            save_html = True
            save_json = True
            save_markdown = True
        else:
            save_html = args.html
            save_json = args.json
            save_markdown = True  # 默认总是保存Markdown

        max_articles = args.max_articles or 10
        album_only = args.album_only

    if args.verbose:
        print(f"URL: {url}")
        print(f"输出目录: {output_dir}")
        print(f"输出格式: HTML={save_html}, JSON={save_json}, Markdown={save_markdown}")
        if hasattr(args, 'max_articles'):
            print(f"最大文章数量: {max_articles}")
        if hasattr(args, 'album_only'):
            print(f"仅获取列表: {album_only}")

    fetcher = ArticleFetcher()

    # 检查是否为专辑URL
    if fetcher.album_fetcher.is_album_url(url):
        if album_only:
            # 仅获取专辑文章列表
            print("仅获取专辑文章列表...")
            articles = fetcher.album_fetcher.fetch_album_articles(url, max_articles)
            if articles:
                print(f"\n获取到 {len(articles)} 篇文章:")
                for i, article in enumerate(articles, 1):
                    print(f"{i:2d}. {article['title']}")
                    print(f"     URL: {article['url']}")
                    print(f"     时间: {article.get('create_time', 'N/A')}")
                    if i < len(articles):
                        print()

                # 保存文章列表到文件
                list_file = os.path.join(output_dir, f"album_articles_{int(time.time())}.json")
                os.makedirs(output_dir, exist_ok=True)
                with open(list_file, 'w', encoding='utf-8') as f:
                    json.dump(articles, f, ensure_ascii=False, indent=2)
                print(f"\n文章列表已保存到: {list_file}")
            else:
                print("未获取到任何文章")
                sys.exit(1)
        else:
            # 批量下载专辑文章
            result = fetcher.fetch_album_articles(url, output_dir, max_articles, save_html, save_json, save_markdown)
            if result:
                print(f"\n批量下载完成!")
                print(f"成功下载: {len(result)} 篇文章")
            else:
                print("专辑文章下载失败!")
                sys.exit(1)
    else:
        # 单篇文章处理
        result = fetcher.fetch_article(url, output_dir, save_html, save_json, save_markdown)

        if result:
            print(f"\n成功获取文章!")
            print(f"标题: {result['title']}")
            print(f"作者: {result['author']}")
            print(f"发布时间: {result['publish_time']}")
        else:
            print("文章获取失败!")
            sys.exit(1)

if __name__ == "__main__":
    main()