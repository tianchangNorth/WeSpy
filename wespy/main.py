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
    
    def fetch_article(self, url, output_dir="articles"):
        """
        获取文章内容
        
        Args:
            url (str): 文章URL
            output_dir (str): 输出目录
        
        Returns:
            dict: 包含文章信息的字典
        """
        try:
            # 特殊处理微信公众号链接
            if 'mp.weixin.qq.com' in url:
                return self._fetch_wechat_article(url, output_dir)
            else:
                return self._fetch_general_article(url, output_dir)
                
        except Exception as e:
            print(f"获取文章失败: {e}")
            return None
    
    def _fetch_wechat_article(self, url, output_dir):
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
        self._save_article(article_info, output_dir)
        
        return article_info
    
    def _fetch_general_article(self, url, output_dir):
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
        self._save_article(article_info, output_dir)
        
        return article_info
    
    def _extract_wechat_info(self, soup):
        """提取微信文章信息"""
        info = {}
        
        # 标题
        title_elem = soup.find('h1', {'class': 'rich_media_title'}) or soup.find('h1')
        info['title'] = title_elem.get_text().strip() if title_elem else "未知标题"
        
        # 作者
        author_elem = soup.find('a', {'class': 'profile_nickname'}) or soup.find('span', {'class': 'profile_nickname'})
        info['author'] = author_elem.get_text().strip() if author_elem else "未知作者"
        
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
                      soup.find('div', {'class': re.compile(r'author', re.I)}))
        
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
    
    def _save_article(self, article_info, output_dir):
        """保存文章到文件"""
        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 生成安全的文件名
        safe_title = re.sub(r'[<>:"/\\|?*]', '_', article_info['title'])[:50]
        timestamp = int(time.time())
        
        # 保存HTML文件
        html_filename = f"{safe_title}_{timestamp}.html"
        html_path = os.path.join(output_dir, html_filename)
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(article_info['html_content'])
        
        print(f"HTML文件已保存: {html_path}")
        
        # 保存文章信息为JSON
        info_filename = f"{safe_title}_{timestamp}_info.json"
        info_path = os.path.join(output_dir, info_filename)
        
        info_to_save = {
            'title': article_info['title'],
            'author': article_info['author'],
            'publish_time': article_info['publish_time'],
            'url': article_info['url'],
            'html_file': html_filename,
            'fetch_time': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(info_to_save, f, ensure_ascii=False, indent=2)
        
        print(f"文章信息已保存: {info_path}")
        
        # 转换为Markdown
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
            
        except Exception as e:
            print(f"转换Markdown失败: {e}")
    
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
    parser.add_argument('url', help='文章URL')
    parser.add_argument('-o', '--output', default='articles', help='输出目录 (默认: articles)')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细信息')
    
    args = parser.parse_args()
    
    if args.verbose:
        print(f"URL: {args.url}")
        print(f"输出目录: {args.output}")
    
    fetcher = ArticleFetcher()
    result = fetcher.fetch_article(args.url, args.output)
    
    if result:
        print(f"\n成功获取文章!")
        print(f"标题: {result['title']}")
        print(f"作者: {result['author']}")
        print(f"发布时间: {result['publish_time']}")
    else:
        print("文章获取失败!")
        sys.exit(1)

if __name__ == "__main__":
    # 如果没有命令行参数，提供交互式输入
    if len(sys.argv) == 1:
        print("文章获取工具")
        print("=" * 40)
        url = input("请输入文章URL: ").strip()
        output_dir = input("输出目录 (回车使用默认 'articles'): ").strip() or 'articles'
        
        fetcher = ArticleFetcher()
        result = fetcher.fetch_article(url, output_dir)
        
        if result:
            print(f"\n成功获取文章!")
            print(f"标题: {result['title']}")
            print(f"作者: {result['author']}")
            print(f"发布时间: {result['publish_time']}")
        else:
            print("文章获取失败!")
    else:
        main()