try:
    from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
    from pydantic import BaseModel
    from starlette.concurrency import run_in_threadpool
except ImportError as exc:  # pragma: no cover - exercised only without [api]
    raise ImportError(
        'The TelePress API server needs optional dependencies. '
        'Install them with: pip install "telepress[api]"'
    ) from exc
from typing import Optional
import os
import shutil
import tempfile
from .core import TelegraphPublisher
from .exceptions import TelePressError

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
