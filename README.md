# WeSpy

[![PyPI version](https://badge.fury.io/py/wespy.svg)](https://badge.fury.io/py/wespy)
[![Python Support](https://img.shields.io/pypi/pyversions/wespy.svg)](https://pypi.org/project/wespy/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

WeSpy 是一个用于获取wx公众号文章并转换为 Markdown 格式的 Python 工具,支持图片防盗链处理、专辑批量下载和多种输出格式。

## 特性

- 🚀 **智能文章提取**：自动识别文章标题、作者、发布时间和正文内容
- 📱 **wx公众号支持**：专门优化wx公众号文章的提取，支持长短链接自动转换
- 🎵 **专辑批量下载**：支持微信公众号专辑文章批量获取和下载
- 🖼️ **图片防盗链处理**：自动处理图片防盗链问题，确保图片正常显示
- 📝 **灵活输出配置**：默认只输出 Markdown，可选择 HTML 和 JSON 格式
- 🌐 **通用网页支持**：支持大多数网站的文章提取
- 🎯 **命令行友好**：提供简单易用的命令行界面
- 📂 **批量处理**：支持批量处理多个文章链接和专辑文章

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
# 获取wx公众号文章（默认只输出 Markdown）
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

# === 微信专辑功能 ===

# 获取微信专辑文章列表（不下载内容）
wespy "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=...&album_id=..." --album-only

# 批量下载微信专辑文章（默认下载前10篇）
wespy "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=...&album_id=..."

# 限制专辑文章下载数量
wespy "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=...&album_id=..." --max-articles 5

# 下载专辑文章并保存所有格式
wespy "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=...&album_id=..." --max-articles 5 --all
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
from wespy.main import WeChatAlbumFetcher

# 创建文章获取器实例
fetcher = ArticleFetcher()

# 获取单篇文章（默认只输出 Markdown）
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

# === 微信专辑功能 ===

# 创建专辑获取器
album_fetcher = WeChatAlbumFetcher()

# 仅获取专辑文章列表
articles = album_fetcher.fetch_album_articles(
    "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=...&album_id=...",
    max_articles=20  # 限制获取数量
)

print(f"获取到 {len(articles)} 篇文章")

# 批量下载专辑文章
successful_articles = fetcher.fetch_album_articles(
    album_url="https://mp.weixin.qq.com/mp/appmsgalbum?__biz=...&album_id=...",
    output_dir="articles",
    max_articles=10,
    save_html=True,
    save_json=True,
    save_markdown=True
)

print(f"成功下载 {len(successful_articles)} 篇文章")
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
- wx公众号 (mp.weixin.qq.com)
- 大部分基于标准 HTML 结构的博客和新闻网站

### 通用支持
WeSpy 使用智能算法尝试从以下元素中提取内容：
- `<article>` 标签
- 带有 `content`、`article-content`、`post-content` 等 class 的元素
- `<main>` 标签
- 标准的 meta 标签信息

## 命令行选项

```
wespy [-h] [-o OUTPUT] [-v] [--html] [--json] [--all] [--max-articles MAX_ARTICLES] [--album-only] url

获取文章内容并转换为Markdown，支持微信专辑批量下载

positional arguments:
  url                   文章URL或微信专辑URL

optional arguments:
  -h, --help            显示帮助信息
  -o OUTPUT, --output OUTPUT
                        输出目录 (默认: articles)
  -v, --verbose         显示详细信息
  --html                同时保存HTML文件
  --json                同时保存JSON信息文件
  --all                 保存所有格式文件 (HTML, JSON, Markdown)
  --max-articles MAX_ARTICLES
                        微信专辑最大下载文章数量 (默认: 10)
  --album-only          仅获取专辑文章列表，不下载内容
```

### 输出格式选项说明
- **默认行为**：只生成 Markdown 文件
- **`--html`**：生成 Markdown + HTML 文件
- **`--json`**：生成 Markdown + JSON 文件
- **`--all`**：生成所有格式文件（HTML + JSON + Markdown）

## 微信专辑功能

### 功能介绍
WeSpy 支持微信公众号专辑文章的批量获取和下载，可以一次性下载整个专辑中的所有文章。

### 使用方式

#### 仅获取文章列表
使用 `--album-only` 参数只获取专辑中的文章列表，不下载具体内容：

```bash
wespy "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=...&album_id=..." --album-only
```

输出示例：
```
获取到 25 篇文章:
 1. 文章标题一
     URL: http://mp.weixin.qq.com/s?__biz=...
     时间: 1704067200

 2. 文章标题二
     URL: http://mp.weixin.qq.com/s?__biz=...
     时间: 1703980800
```

文章列表会保存为JSON文件，包含标题、URL、发布时间等完整信息。

#### 批量下载专辑文章
直接使用专辑URL即可批量下载专辑中的所有文章：

```bash
# 下载前10篇文章（默认）
wespy "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=...&album_id=..."

# 限制下载文章数量
wespy "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=...&album_id=..." --max-articles 5

# 下载并保存所有格式
wespy "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=...&album_id=..." --max-articles 5 --all
```

### 输出结构
专辑文章下载后会创建独立的专辑目录：

```
articles/
├── album_1703980800/                    # 专辑专用目录
│   ├── 文章标题一_1703980800.md         # Markdown格式
│   ├── 文章标题一_1703980800_info.json  # 文章信息
│   ├── 文章标题二_1703980801.md         # 下一篇文章
│   └── ...
└── album_1703980800_summary.json        # 专辑下载汇总信息
```

### 汇总信息
每个专辑下载完成后会生成详细的汇总报告，包含：
- 专辑URL和下载时间
- 成功/失败统计
- 成功下载的文章列表
- 失败的文章列表和错误信息

### 技术特性
- **智能分页**：自动处理微信分页获取，支持大型专辑
- **错误处理**：分离成功和失败的文章，确保部分失败不影响整体下载
- **速率控制**：内置延迟机制避免请求过快
- **进度显示**：实时显示下载进度和统计信息

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
A: WeSpy 对wx公众号有特别优化，对大部分使用标准 HTML 结构的网站都有较好的支持。如果某个网站不支持，欢迎提交 issue。

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

### v0.2.0 (2025-01-22)
- **🎵 新增微信专辑功能**：支持微信公众号专辑文章批量获取和下载
- **📝 增强命令行选项**：`--max-articles`、`--album-only` 用于专辑操作
- **🔗 智能链接转换**：自动检测并转换微信长链接为短链接
- **📊 详细汇总报告**：专辑下载完成后生成详细的统计报告
- **🚀 优化错误处理**：分离成功和失败的文章，提升批量处理稳定性
- **⚡ 性能优化**：内置速率控制机制避免请求过快
- **📁 改进文件组织**：专辑文章保存到独立目录，便于管理

### v0.1.2 (2025-01-01)
- **改进输出格式配置**：默认只输出 Markdown 文件
- **新增命令行选项**：`--html`、`--json`、`--all` 用于控制输出格式
- **优化交互模式**：添加输出格式选择菜单
- **更新 Python API**：支持参数化输出格式控制

### v0.1.0 (2023-07-30)
- 初始版本发布
- 支持wx公众号文章提取
- 支持通用网页文章提取
- 支持 HTML/JSON/Markdown 多格式输出
- 图片防盗链处理
- 命令行界面

## 联系方式

- GitHub: [https://github.com/tianchangNorth/WeSpy](https://github.com/tianchangNorth/WeSpy)
- Issues: [https://github.com/tianchangNorth/WeSpy/issues](https://github.com/tianchangNorth/WeSpy/issues)

---  

## 推荐🐔场

自用🐔场，稳定，线路多，速度快，[点这里注册](https://joinus-2.202402.best/#/register?code=HlpuGibO)

## 免责声明

本项目仅供学习和研究目的使用。使用本工具时，请务必遵守以下原则：

### 使用责任
- 用户需自行承担使用本工具的所有风险和责任
- 请确保您的使用行为符合目标网站的robots.txt文件要求
- 尊重内容创作者的知识产权，不得用于商业目的
- 不要对网站服务器造成过大的访问压力

### 法律合规
- 请遵守当地法律法规以及目标网站的使用条款
- 不得将本工具用于任何非法或未经授权的活动
- 下载的内容应仅用于个人学习、研究或存档目的

### 技术风险
- 网站结构可能随时变化，本工具可能无法正常工作
- 本工具按"原样"提供，不提供任何明示或暗示的保证
- 开发者不对因使用本工具造成的任何损失承担责任

### 数据安全
- 本工具不会收集或上传您的任何个人信息
- 所有数据处理都在本地完成
- 请妥善保管您下载的内容

---

**重要提醒**: 请合理、合法、负责任地使用本工具，尊重网络服务提供者和内容创作者的权益.

