#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
掘金文章获取工具
专门用于获取掘金平台文章内容并转换为Markdown格式
"""

import os
import re
import requests
import urllib.parse
from bs4 import BeautifulSoup
import time
import json

class JuejinFetcher:
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
            'Referer': 'https://juejin.cn/'
        })
    
    def fetch_article(self, url, output_dir="articles", save_html=False, save_json=False, save_markdown=True):
        """
        获取掘金文章内容
        
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
            if 'juejin.cn' not in url:
                print("警告：URL不是掘金链接，但仍尝试获取")
            
            return self._fetch_juejin_article(url, output_dir, save_html, save_json, save_markdown)
                
        except Exception as e:
            print(f"获取掘金文章失败: {e}")
            return None
    
    def _fetch_juejin_article(self, url, output_dir, save_html=False, save_json=False, save_markdown=True):
        """获取掘金文章"""
        print(f"正在获取掘金文章: {url}")
        
        # 设置掘金特定的请求头
        headers = self.session.headers.copy()
        headers['Referer'] = 'https://juejin.cn/'
        
        response = self.session.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取文章信息
        article_info = self._extract_juejin_info(soup)
        article_info['url'] = url
        article_info['html_content'] = response.text
        
        # 保存文章
        self._save_article(article_info, output_dir, save_html, save_json, save_markdown)
        
        return article_info
    
    def _extract_juejin_info(self, soup):
        """提取掘金文章信息"""
        info = {}
        
        # 标题 - 掘金标题通常在h1.article-title
        title_elem = (soup.find('h1', {'class': 'article-title'}) or 
                     soup.find('h1', {'class': 'article-title-text'}) or
                     soup.find('h1'))
        info['title'] = title_elem.get_text().strip() if title_elem else "未知标题"
        
        # 作者 - 掘金作者信息
        author_elem = ( soup.find('span', {'class': 'name'}) )
        info['author'] = author_elem.get_text().strip() if author_elem else "未知作者"
        
        # 发布时间 - 掘金时间信息
        time_elem = (soup.find('span', {'class': 'time'}) or 
                    soup.find('time') or
                    soup.find('span', {'class': 'date'}))
        info['publish_time'] = time_elem.get_text().strip() if time_elem else ""
        
        # 内容区域 - 掘金文章内容
        content_elem = (soup.find('div', {'id': 'article-root'}) or
                       soup.find('div', {'class': 'article-content'}) or
                       soup.find('div', {'class': 'markdown-body'}) or
                       soup.find('article') or
                       soup.find('div', {'id': 'article-content'}))
        
        if content_elem:
            # 清理内容，移除CSS样式标签
            cleaned_content = self._clean_content(content_elem)
            info['content_html'] = str(cleaned_content)
            info['content_text'] = cleaned_content.get_text().strip()
        else:
            info['content_html'] = ""
            info['content_text'] = ""
        
        # 提取标签
        tags = []
        tag_elems = soup.find_all('a', {'class': 'tag'}) or soup.find_all('span', {'class': 'tag'})
        for tag_elem in tag_elems:
            tag_text = tag_elem.get_text().strip()
            if tag_text:
                tags.append(tag_text)
        info['tags'] = tags
        
        # 提取阅读数
        view_count_elem = soup.find('span', {'class': 'view-count'}) or soup.find('span', {'class': 'read-count'})
        info['view_count'] = view_count_elem.get_text().strip() if view_count_elem else ""
        
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
                'tags': article_info.get('tags', []),
                'view_count': article_info.get('view_count', ''),
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
                    if article_info.get('view_count'):
                        f.write(f"**阅读量**: {article_info['view_count']}\n")
                    if article_info.get('tags'):
                        f.write(f"**标签**: {', '.join(article_info['tags'])}\n")
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
    
    def _clean_content(self, content_elem):
        """清理内容，移除CSS样式标签但保留文章内容"""
        # 创建副本以避免修改原始soup
        cleaned_content = BeautifulSoup(str(content_elem), 'html.parser')
        
        # 移除所有style标签
        for style_tag in cleaned_content.find_all('style'):
            style_tag.decompose()
        
        # 移除具有特定属性的style标签（掘金特有的样式）
        for elem in cleaned_content.find_all(attrs={'data-highlight': True}):
            elem.decompose()
        
        # 移除所有元素的style属性，但保留元素本身
        for elem in cleaned_content.find_all(style=True):
            del elem['style']
        
        # 如果内容是空的，尝试从其他选择器获取
        if not cleaned_content.get_text().strip():
            # 尝试获取article-root下的直接内容
            article_root = cleaned_content.find('div', {'id': 'article-root'})
            if article_root:
                # 移除style标签但保留其他内容
                for style_tag in article_root.find_all('style'):
                    style_tag.decompose()
                for elem in article_root.find_all(attrs={'data-highlight': True}):
                    elem.decompose()
                for elem in article_root.find_all(style=True):
                    del elem['style']
                return article_root
        
        return cleaned_content

