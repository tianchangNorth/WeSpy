# WeSpy

[![PyPI version](https://badge.fury.io/py/wespy.svg)](https://badge.fury.io/py/wespy)
[![Python Support](https://img.shields.io/pypi/pyversions/wespy.svg)](https://pypi.org/project/wespy/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

WeSpy 是一个用于获取微信公众号文章并转换为 Markdown 格式的 Python 工具,支持图片防盗链处理和多种输出格式。

## 特性

- 🚀 **智能文章提取**：自动识别文章标题、作者、发布时间和正文内容
- 📱 **微信公众号支持**：专门优化微信公众号文章的提取
- 🖼️ **图片防盗链处理**：自动处理图片防盗链问题，确保图片正常显示
- 📝 **灵活输出配置**：默认只输出 Markdown，可选择 HTML 和 JSON 格式
- 🌐 **通用网页支持**：支持大多数网站的文章提取
- 🎯 **命令行友好**：提供简单易用的命令行界面
- 📂 **批量处理**：支持批量处理多个文章链接

## 安装

### 使用 pip 安装（推荐）

```bash
pip install wespy
```

### 从源码安装

```bash
git clone https://github.com/tianchang/wespy.git
cd wespy
pip install -e .
```

## 快速开始

### 命令行使用

```bash
# 获取微信公众号文章（默认只输出 Markdown）
wespy "https://mp.weixin.qq.com/s/xxxxx"

# 指定输出目录
wespy "https://mp.weixin.qq.com/s/xxxxx" -o /path/to/output

# 输出 Markdown + HTML 格式
wespy "https://example.com/article" --html

# 输出 Markdown + JSON 格式
wespy "https://example.com/article" --json

# 输出所有格式（HTML + JSON + Markdown）
wespy "https://example.com/article" --all

# 显示详细信息
wespy "https://example.com/article" -v
```

### 交互式使用

如果不提供任何参数，程序会进入交互模式：

```bash
wespy
```

然后根据提示输入文章 URL、输出目录和输出格式选择：

1. 仅 Markdown（默认）
2. Markdown + HTML
3. Markdown + JSON  
4. 全部格式（HTML + JSON + Markdown）

### Python API 使用

```python
from wespy import ArticleFetcher

# 创建文章获取器实例
fetcher = ArticleFetcher()

# 获取文章（默认只输出 Markdown）
article_info = fetcher.fetch_article(
    url="https://mp.weixin.qq.com/s/xxxxx",
    output_dir="articles"
)

# 获取文章并指定输出格式
article_info = fetcher.fetch_article(
    url="https://mp.weixin.qq.com/s/xxxxx",
    output_dir="articles",
    save_html=True,      # 同时保存HTML文件
    save_json=True,      # 同时保存JSON文件
    save_markdown=True   # 保存Markdown文件（默认为True）
)

if article_info:
    print(f"标题: {article_info['title']}")
    print(f"作者: {article_info['author']}")
    print(f"发布时间: {article_info['publish_time']}")
```

## 输出格式

WeSpy 默认只生成 Markdown 文件，但可以通过配置选项选择其他格式：

### 默认输出（仅 Markdown）
```
articles/
└── 文章标题_1627834567.md        # Markdown格式
```

### 可选格式
- **HTML 文件**：原始 HTML 内容（使用 `--html` 选项）
- **JSON 文件**：文章元数据信息（使用 `--json` 选项）
- **Markdown 文件**：转换后的 Markdown 格式内容（默认生成）

### 全部格式输出示例
```
articles/
├── 文章标题_1627834567.html      # 原始HTML
├── 文章标题_1627834567.md        # Markdown格式
└── 文章标题_1627834567_info.json # 元数据信息
```

### JSON 元数据格式

```json
{
  "title": "文章标题",
  "author": "作者名称",
  "publish_time": "2023-07-30",
  "url": "https://example.com/article",
  "html_file": "文章标题_1627834567.html",
  "fetch_time": "2023-07-30 12:34:56"
}
```

## 支持的网站

### 完全支持
- 微信公众号 (mp.weixin.qq.com)
- 大部分基于标准 HTML 结构的博客和新闻网站

### 通用支持
WeSpy 使用智能算法尝试从以下元素中提取内容：
- `<article>` 标签
- 带有 `content`、`article-content`、`post-content` 等 class 的元素
- `<main>` 标签
- 标准的 meta 标签信息

## 命令行选项

```
wespy [-h] [-o OUTPUT] [-v] [--html] [--json] [--all] url

获取文章内容并转换为Markdown

positional arguments:
  url                   文章URL

optional arguments:
  -h, --help            显示帮助信息
  -o OUTPUT, --output OUTPUT
                        输出目录 (默认: articles)
  -v, --verbose         显示详细信息
  --html                同时保存HTML文件
  --json                同时保存JSON信息文件
  --all                 保存所有格式文件 (HTML, JSON, Markdown)
```

### 输出格式选项说明
- **默认行为**：只生成 Markdown 文件
- **`--html`**：生成 Markdown + HTML 文件
- **`--json`**：生成 Markdown + JSON 文件  
- **`--all`**：生成所有格式文件（HTML + JSON + Markdown）

## 依赖要求

- Python 3.6+
- requests >= 2.20.0
- beautifulsoup4 >= 4.9.0

## 开发

### 开发环境设置

```bash
git clone https://github.com/tianchang/wespy.git
cd wespy
pip install -e ".[dev]"
```

### 运行测试

```bash
python -m pytest tests/
```

### 代码格式化

```bash
black wespy/
flake8 wespy/
```

## 常见问题

### Q: 为什么有些图片无法显示？
A: WeSpy 使用 images.weserv.nl 作为代理服务来解决图片防盗链问题。如果仍然无法显示，可能是原图片已被删除或网络问题。

### Q: 支持哪些网站？
A: WeSpy 对微信公众号有特别优化，对大部分使用标准 HTML 结构的网站都有较好的支持。如果某个网站不支持，欢迎提交 issue。

### Q: 如何批量处理文章？
A: 目前需要通过脚本调用 Python API 来实现批量处理，命令行版本暂不支持批量处理。

## 贡献

欢迎提交 issue 和 pull request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目使用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 更新日志

### v0.1.2 (2025-01-01)
- **改进输出格式配置**：默认只输出 Markdown 文件
- **新增命令行选项**：`--html`、`--json`、`--all` 用于控制输出格式
- **优化交互模式**：添加输出格式选择菜单
- **更新 Python API**：支持参数化输出格式控制

### v0.1.0 (2023-07-30)
- 初始版本发布
- 支持微信公众号文章提取
- 支持通用网页文章提取
- 支持 HTML/JSON/Markdown 多格式输出
- 图片防盗链处理
- 命令行界面

## 联系方式

- GitHub: [https://github.com/tianchangNorth/WeSpy](https://github.com/tianchangNorth/WeSpy)
- Issues: [https://github.com/tianchangNorth/WeSpy/issues](https://github.com/tianchangNorth/WeSpy/issues)

---

**注意**: 请遵守网站的 robots.txt 和使用条款，合理使用本工具。