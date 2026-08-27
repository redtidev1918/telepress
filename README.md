# TelePress

[![CI](https://github.com/redtidev1918/telepress/actions/workflows/ci.yml/badge.svg)](https://github.com/redtidev1918/telepress/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/telepress.svg)](https://pypi.org/project/telepress/)
[![Python](https://img.shields.io/pypi/pyversions/telepress.svg)](https://pypi.org/project/telepress/)

[中文文档](README_CN.md)

TelePress publishes Markdown, plain text, images, and ZIP galleries to
[Telegraph](https://telegra.ph). It supports automatic pagination, external
image hosts, image compression, concurrent uploads, and an optional REST API.

## Requirements

- Python 3.10 or newer
- A Telegraph token, or permission to create one on first use
- An image-host configuration only when publishing images or galleries

## Installation

```bash
pip install telepress

# Optional REST API
pip install "telepress[api]"

# Optional S3-compatible hosts such as AWS S3 and Cloudflare R2
pip install "telepress[s3]"

# Optional YAML configuration files
pip install "telepress[yaml]"
```

Install from source for development:

```bash
git clone https://github.com/redtidev1918/telepress.git
cd telepress
python -m pip install --editable ".[dev]"
```

## Quick start

Publish a document:

```bash
telepress article.md --title "My post"

# The explicit subcommand is equivalent
telepress publish article.md --title "My post"
```

Publish an image or ZIP gallery after configuring an image host:

```bash
telepress configure
telepress check
telepress photo.jpg --title "Photo"
telepress gallery.zip --title "Gallery"
```

Useful publishing options:

```bash
# Override the configured image limit in MiB
telepress gallery.zip --image-size-limit 10

# Keep original images instead of compressing oversized files
telepress gallery.zip --no-compress

# Use a Telegraph-compatible API endpoint
telepress article.md --api-url http://localhost:9009
```

Text-only publishing does not load or require an image-host configuration.
The Telegraph access token is created automatically when needed and stored in
`~/.telegraph_token` unless one is supplied with `--token`.

## REST API

Install the optional API dependencies first: `pip install "telepress[api]"`.

```bash
telepress-server --host 127.0.0.1 --port 8000
```

Interactive OpenAPI documentation is available at
`http://127.0.0.1:8000/docs`.

```bash
curl -X POST http://127.0.0.1:8000/publish/text \
  -H "Content-Type: application/json" \
  -d '{"content":"# Title\n\nBody","title":"Example"}'

curl -X POST http://127.0.0.1:8000/publish/file \
  -F "file=@article.md" \
  -F "title=Example"
```

Blocking file, compression, and network work is dispatched away from the API
event loop, so concurrent requests do not serialize on those operations.

## Image hosts

Supported hosts:

- ImgBB
- Imgur
- sm.ms
- S3-compatible storage, including AWS S3, Cloudflare R2, OSS, and MinIO
- Rclone remotes
- Custom HTTP upload APIs

Run `telepress configure` for the interactive setup, or create
`~/.telepress.json`:

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

S3-compatible configuration:

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

Environment variables override file configuration:

```bash
export TELEPRESS_IMAGE_HOST_TYPE=imgbb
export TELEPRESS_IMAGE_HOST_API_KEY=your-key
```

Configuration is searched in the following locations:

1. The path passed to `load_config()`
2. `TELEPRESS_CONFIG`
3. `~/.telepress.json`, `~/.telepress.yaml`, `~/.telepress.yml`
4. `~/.config/telepress.json`

## Python API

```python
from telepress import TelegraphPublisher, publish, publish_text

url = publish("article.md", title="My article")
text_url = publish_text("# Hello\n\nWorld", title="Hello")

publisher = TelegraphPublisher(image_size_limit=10)
gallery_url = publisher.publish("gallery.zip", title="Gallery")
```

Upload images directly:

```python
from telepress import ImageUploader

uploader = ImageUploader("imgbb", api_key="your-key")
url = uploader.upload("photo.jpg")

batch = uploader.upload_batch(["1.jpg", "2.jpg"])
print(batch.success_rate, batch.get_url_map())
```

## Behavior and limits

- Markdown and plain text are converted to Telegraph DOM nodes.
- Plain text chapter headings such as `Chapter 1` and `第一章` are detected.
- Large text is split near 10,000-character boundaries and linked with
  previous/next navigation.
- Galleries are split at 100 images per page.
- Images larger than 5 MiB are compressed by default; GIF compression is
  intentionally skipped.
- A 2 GiB input safety limit is applied before processing.
- Duplicate text publications are cached in `~/.telepress_cache.json` by
  default.

Supported input extensions include `.txt`, `.md`, `.markdown`, `.rst`,
`.text`, `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.bmp`, and `.zip`.

## Error handling

```python
from telepress import TelePressError, ValidationError, publish

try:
    url = publish("article.md")
except ValidationError as exc:
    print(f"Invalid input: {exc}")
except TelePressError as exc:
    print(f"Publishing failed: {exc}")
```

## Development and releases

```bash
python -m pip install --editable ".[dev]"
python -m pytest --cov
python -m build
python -m twine check dist/*
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution conventions and
[docs/RELEASING.md](docs/RELEASING.md) for the automated release workflow.
Notable changes are recorded in [CHANGELOG.md](CHANGELOG.md).

## License

[MIT](LICENSE)
