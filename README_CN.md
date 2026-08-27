# TelePress

[![CI](https://github.com/redtidev1918/telepress/actions/workflows/ci.yml/badge.svg)](https://github.com/redtidev1918/telepress/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/telepress.svg)](https://pypi.org/project/telepress/)
[![Python](https://img.shields.io/pypi/pyversions/telepress.svg)](https://pypi.org/project/telepress/)

[English](README.md)

TelePress 用于把 Markdown、纯文本、图片和 ZIP 图集发布到
[Telegraph](https://telegra.ph)，支持自动分页、外部图床、图片压缩、并发上传和可选的 REST API。

## 环境要求

- Python 3.10 或更高版本
- Telegraph token；首次使用时也可以自动创建
- 只有发布图片或图集时才需要配置图床

## 安装

```bash
pip install telepress

# 可选：REST API
pip install "telepress[api]"

# 可选：AWS S3、Cloudflare R2 等 S3 兼容图床
pip install "telepress[s3]"

# 可选：YAML 配置文件
pip install "telepress[yaml]"
```

从源码安装开发环境：

```bash
git clone https://github.com/redtidev1918/telepress.git
cd telepress
python -m pip install --editable ".[dev]"
```

## 快速开始

发布文档：

```bash
telepress article.md --title "我的文章"

# 显式子命令写法与上面等价
telepress publish article.md --title "我的文章"
```

配置图床后发布图片或 ZIP 图集：

```bash
telepress configure
telepress check
telepress photo.jpg --title "照片"
telepress gallery.zip --title "图集"
```

常用参数：

```bash
# 临时覆盖图片大小限制，单位 MiB
telepress gallery.zip --image-size-limit 10

# 不压缩超限图片
telepress gallery.zip --no-compress

# 使用兼容 Telegraph 的自定义 API
telepress article.md --api-url http://localhost:9009
```

纯文本发布不会加载或要求图床配置。Telegraph token 会在需要时自动创建并保存到
`~/.telegraph_token`，也可以用 `--token` 显式传入。

## REST API

使用前先安装可选 API 依赖：`pip install "telepress[api]"`。

```bash
telepress-server --host 127.0.0.1 --port 8000
```

OpenAPI 交互文档位于 `http://127.0.0.1:8000/docs`。

```bash
curl -X POST http://127.0.0.1:8000/publish/text \
  -H "Content-Type: application/json" \
  -d '{"content":"# 标题\n\n正文","title":"示例"}'

curl -X POST http://127.0.0.1:8000/publish/file \
  -F "file=@article.md" \
  -F "title=示例"
```

文件读写、图片压缩和同步网络请求会在线程池执行，不会阻塞 API 的异步事件循环。

## 图片托管

支持的图床：

- ImgBB
- Imgur
- sm.ms
- AWS S3、Cloudflare R2、OSS、MinIO 等 S3 兼容存储
- Rclone remote
- 自定义 HTTP 上传 API

运行 `telepress configure` 可以交互式配置，也可以创建 `~/.telepress.json`：

```json
{
  "image_host": {
    "type": "rclone",
    "remote_path": "myremote:bucket/path",
    "public_url": "https://cdn.example.com/path",
    "rclone_flags": ["--transfers=32", "--checkers=32"],
    "max_size_mb": 20,
    "max_workers": 8
  }
}
```

S3 兼容配置：

```json
{
  "image_host": {
    "type": "s3",
    "access_key_id": "your-access-key",
    "secret_access_key": "your-secret-key",
    "bucket": "your-bucket",
    "public_url": "https://cdn.example.com",
    "endpoint_url": "https://s3.example.com",
    "region_name": "auto"
  }
}
```

环境变量的优先级高于配置文件：

```bash
export TELEPRESS_IMAGE_HOST_TYPE=imgbb
export TELEPRESS_IMAGE_HOST_API_KEY=your-key
```

配置文件查找顺序：

1. 传给 `load_config()` 的显式路径
2. `TELEPRESS_CONFIG`
3. `~/.telepress.json`、`~/.telepress.yaml`、`~/.telepress.yml`
4. `~/.config/telepress.json`

## Python API

```python
from telepress import TelegraphPublisher, publish, publish_text

url = publish("article.md", title="我的文章")
text_url = publish_text("# 标题\n\n正文", title="示例")

publisher = TelegraphPublisher(image_size_limit=10)
gallery_url = publisher.publish("gallery.zip", title="图集")
```

直接上传图片：

```python
from telepress import ImageUploader

uploader = ImageUploader("imgbb", api_key="your-key")
url = uploader.upload("photo.jpg")

batch = uploader.upload_batch(["1.jpg", "2.jpg"])
print(batch.success_rate, batch.get_url_map())
```

## 行为与限制

- Markdown 和纯文本会转换为 Telegraph DOM 节点。
- 可以识别 `Chapter 1`、`第一章` 等纯文本章节标题。
- 大文本会在约 10,000 字符边界自动分页，并生成上一页、下一页导航。
- 图集每 100 张图片分页。
- 单张图片默认限制为 5 MiB，超限时自动压缩；GIF 不会自动压缩。
- 处理前会应用 2 GiB 的输入安全上限。
- 默认使用 `~/.telepress_cache.json` 避免重复发布相同文本。

支持 `.txt`、`.md`、`.markdown`、`.rst`、`.text`、`.jpg`、`.jpeg`、
`.png`、`.gif`、`.webp`、`.bmp` 和 `.zip`。

## 错误处理

```python
from telepress import TelePressError, ValidationError, publish

try:
    url = publish("article.md")
except ValidationError as exc:
    print(f"输入无效：{exc}")
except TelePressError as exc:
    print(f"发布失败：{exc}")
```

## 开发与发版

```bash
python -m pip install --editable ".[dev]"
python -m pytest --cov
python -m build
python -m twine check dist/*
```

贡献规范见 [CONTRIBUTING.md](CONTRIBUTING.md)，自动发版的配置和操作步骤见
[docs/RELEASING.md](docs/RELEASING.md)，版本变化记录在 [CHANGELOG.md](CHANGELOG.md)。

## License

[MIT](LICENSE)
