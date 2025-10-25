from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tempfile
import os
import traceback
from pathlib import Path
from main import process_zip_file

app = FastAPI(title="Ad Media Processor API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {
        "message": "Ad Media Processor API",
        "endpoints": {
            "/process": "POST - Upload and process a zip file",
            "/health": "GET - Health check"
        }
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/process")
async def process_media(file: UploadFile = File(...)):
    """
    Process a zip file containing PNG images and MP4 videos.

    Returns a dictionary where each key is a filename and value is the preprocessing result.
    """
    # Validate file is a zip
    if not file.filename or not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="File must be a .zip file")

    # Create temporary file to save upload
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    tmp_path = tmp_file.name

    try:
        # Write uploaded file to temporary location
        contents = await file.read()
        print(f"Read {len(contents)} bytes from upload")
        tmp_file.write(contents)
        tmp_file.close()  # Close the file so it can be read as a zip

        print(f"Processing zip file: {tmp_path}")
        print(f"File exists: {os.path.exists(tmp_path)}")
        print(f"File size: {os.path.getsize(tmp_path)} bytes")

        import zipfile as zf
        print(f"Is valid zip: {zf.is_zipfile(tmp_path)}")

        # Process the zip file using main.py
        results = process_zip_file(tmp_path)

        return JSONResponse(content=results)

    except Exception as e:
        # Print full traceback for debugging
        print("ERROR occurred during processing:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

    finally:
        # Clean up temporary file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
