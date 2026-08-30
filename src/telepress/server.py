try:
    from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
    from pydantic import BaseModel
    from starlette.concurrency import run_in_threadpool
except ImportError as exc:  # pragma: no cover - exercised only without [api]
    raise ImportError(
        'The TelePress API server needs optional dependencies. '
        'Install them with: pip install "telepress[api]"'
    ) from exc
from typing import Optional, List, Dict
import os
import shutil
import tempfile
import zipfile
from .core import TelegraphPublisher
from .exceptions import TelePressError, ValidationError

app = FastAPI(
    title="TelePress API",
    description="REST API to convert text, markdown, images, and zips to Telegraph pages.",
    version="0.1.0"
)

# Request Models
class TextPublishRequest(BaseModel):
    content: str
    title: str
    token: Optional[str] = None

class PublishResponse(BaseModel):
    url: str
    status: str = "success"

class GalleryPublishResponse(BaseModel):
    url: str
    status: str = "success"
    ok: bool = True
    files: int = 0

def get_publisher(token: Optional[str] = None):
    try:
        return TelegraphPublisher(token=token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _write_text_temp(content: str) -> str:
    """Write request text without blocking the async event loop."""
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.md', delete=False, encoding='utf-8'
    ) as tmp:
        tmp.write(content)
        return tmp.name


def _copy_upload_temp(file_obj, suffix: str) -> str:
    """Copy an uploaded file into a stable temporary path."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file_obj, tmp)
        return tmp.name


def _build_gallery_footer(
    tags: Optional[str],
    link: Optional[str],
    spoiler: Optional[str]
) -> List[Dict]:
    """
    Build the first-page footer nodes for a gallery from optional metadata.
    
    Renders an R-18 warning when spoiler is truthy, a #tag paragraph, and a
    source link paragraph. Returns [] when nothing is provided.
    """
    nodes: List[Dict] = []
    if spoiler and str(spoiler).strip().lower() in ('1', 'true', 'yes', 'on'):
        nodes.append({
            'tag': 'p',
            'children': ['⚠️ Contains adult content (R-18) / 成人内容']
        })
    if tags:
        tag_list = [t.strip() for t in tags.split(',') if t.strip()]
        if tag_list:
            nodes.append({
                'tag': 'p',
                'children': ['# ' + ' #'.join(tag_list)]
            })
    if link and str(link).strip():
        link = link.strip()
        nodes.append({
            'tag': 'p',
            'children': [
                'Source: ',
                {'tag': 'a', 'attrs': {'href': link}, 'children': [link]}
            ]
        })
    return nodes


def _publish_gallery_worker(
    files,
    title: Optional[str],
    tags: Optional[str],
    link: Optional[str],
    spoiler: Optional[str],
    token: Optional[str]
) -> Dict:
    """
    Save the uploaded images in order, pack them into a zip, and publish them
    as a Telegra.ph gallery. Runs off the async event loop because publishing
    performs synchronous HTTP requests and may wait for rate limits.
    """
    tmp_dir = tempfile.mkdtemp(prefix='telepress-gallery-')
    try:
        paths = []
        used_names = set()
        for index, upload in enumerate(files, start=1):
            raw_name = os.path.basename(upload.filename or '')
            filename = raw_name or f'image_{index}.jpg'
            base, ext = os.path.splitext(filename)
            candidate = filename
            counter = 1
            while candidate in used_names:
                candidate = f'{base}_{counter}{ext}'
                counter += 1
            used_names.add(candidate)
            dest = os.path.join(tmp_dir, candidate)
            with open(dest, 'wb') as out:
                shutil.copyfileobj(upload.file, out)
            paths.append(dest)

        if not paths:
            raise ValidationError("No files provided for gallery publishing")

        zip_path = os.path.join(tmp_dir, 'gallery.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for p in paths:
                zf.write(p, arcname=os.path.basename(p))

        footer = _build_gallery_footer(tags, link, spoiler)
        pub_title = title or os.path.splitext(os.path.basename(paths[0]))[0]
        publisher = get_publisher(token)
        url = publisher.publish_zip_gallery(
            zip_path, title=pub_title, footer_nodes=footer
        )
        return {'url': url, 'files': len(paths)}
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.get("/")
def health_check():
    return {"status": "ok", "service": "telepress"}

@app.post("/publish/text", response_model=PublishResponse)
async def publish_text(request: TextPublishRequest):
    """
    Publish raw Markdown/Text content directly.
    """
    try:
        tmp_path = await run_in_threadpool(_write_text_temp, request.content)
        
        # Publishing performs synchronous HTTP requests and may wait for rate
        # limits, so keep it off the async event loop.
        publisher = await run_in_threadpool(get_publisher, request.token)
        url = await run_in_threadpool(
            publisher.publish, tmp_path, title=request.title
        )
        return PublishResponse(url=url)
        
    except TelePressError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)

@app.post("/publish/file", response_model=PublishResponse)
async def publish_file(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    token: Optional[str] = Form(None)
):
    """
    Upload a file (md, txt, zip, image) to be processed and published.
    """
    try:
        suffix = os.path.splitext(file.filename)[1]
        tmp_path = await run_in_threadpool(
            _copy_upload_temp, file.file, suffix
        )
            
        publisher = await run_in_threadpool(get_publisher, token)
        
        # If no title provided, use filename from upload
        pub_title = title if title else file.filename
        
        url = await run_in_threadpool(
            publisher.publish, tmp_path, title=pub_title
        )
        return PublishResponse(url=url)
        
    except TelePressError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)

@app.post("/publish/gallery", response_model=GalleryPublishResponse)
async def publish_gallery(
    files: List[UploadFile] = File(...),
    title: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    link: Optional[str] = Form(None),
    spoiler: Optional[str] = Form(None),
    token: Optional[str] = Form(None)
):
    """
    Upload multiple image files and publish them as a Telegra.ph gallery.

    Files are packed into a zip in upload order and published with automatic
    pagination and Prev/Next navigation. The optional `tags` (comma-separated),
    `link` (source URL) and `spoiler` (truthy for R-18 content) fields are
    rendered as a footer on the first page. `title` defaults to the first
    file's name when omitted.

    Compatible with generic multipart delivery clients (e.g. PixivFlow
    `httpMultipart` targets posting repeated `files` parts).
    """
    try:
        result = await run_in_threadpool(
            _publish_gallery_worker, files, title, tags, link, spoiler, token
        )
        return GalleryPublishResponse(
            url=result['url'], files=result['files']
        )
    except TelePressError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def start_server(host="0.0.0.0", port=8000):
    """Start the TelePress API server."""
    import uvicorn
    uvicorn.run(app, host=host, port=port)


def main():
    """
    CLI entry point for telepress-server command.
    
    Usage:
        telepress-server
        telepress-server --host 127.0.0.1 --port 9000
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Start the TelePress REST API server."
    )
    parser.add_argument(
        "--host", 
        default="0.0.0.0", 
        help="Host to bind (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="Port to listen on (default: 8000)"
    )
    
    args = parser.parse_args()
    
    print(f"Starting TelePress API server at http://{args.host}:{args.port}")
    print("API docs available at: http://localhost:{}/docs".format(args.port))
    
    start_server(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
