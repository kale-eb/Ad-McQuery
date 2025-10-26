from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import tempfile
import os
import json
import traceback
import shutil
from pathlib import Path
from main import process_zip_file
from batch_analysis import batch_analyze_videos, batch_analyze_images
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# TESTING MODE TOGGLE
# Set to True to use batch_test.json data (no API calls)
# Set to False to use real Gemini API analysis
TESTING_MODE = True

app = FastAPI(title="Ad Media Processor API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],  # Vite default ports
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


@app.get("/datasets")
def list_datasets():
    """
    List all available datasets
    """
    try:
        datasets_dir = Path(__file__).parent / "datasets"
        if not datasets_dir.exists():
            return JSONResponse(content=[])
        
        datasets = []
        for dataset_dir in datasets_dir.iterdir():
            if dataset_dir.is_dir():
                analysis_file = dataset_dir / f"{dataset_dir.name}-analysis.json"
                datasets.append({
                    "name": dataset_dir.name,
                    "has_analysis": analysis_file.exists(),
                    "files": [f.name for f in dataset_dir.iterdir() if f.is_file() and not f.name.endswith('-analysis.json')]
                })
        
        return JSONResponse(content=datasets)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list datasets: {str(e)}")


@app.get("/batch-test")
def get_batch_test():
    """
    Return the batch_test.json data for display
    """
    try:
        batch_test_path = Path(__file__).parent / "batch_test.json"
        with open(batch_test_path, 'r') as f:
            data = json.load(f)
        return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load batch_test.json: {str(e)}")


@app.get("/media/{dataset_name}/{folder}/{filename}")
def get_media_file(dataset_name: str, folder: str, filename: str):
    """
    Serve media files (images/videos) from the datasets directory
    """
    try:
        # Try to find the file in datasets directory with folder structure
        file_path = Path(__file__).parent / "datasets" / dataset_name / folder / filename
        if file_path.exists():
            return FileResponse(file_path)

        # Also try direct path without folder for backward compatibility
        file_path = Path(__file__).parent / "datasets" / dataset_name / filename
        if file_path.exists():
            return FileResponse(file_path)

        # Also try tests directory for backward compatibility
        file_path = Path(__file__).parent / "tests" / filename
        if file_path.exists():
            return FileResponse(file_path)

        # If not found, return 404
        raise HTTPException(status_code=404, detail=f"Media file {filename} not found in dataset {dataset_name}/{folder}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to serve media file: {str(e)}")


@app.post("/process")
async def process_media(file: UploadFile = File(...)):
    """
    Process a zip file containing PNG images and MP4 videos.

    Returns a dictionary where each key is a filename and value is the complete analysis.
    """
    # Validate file is a zip
    if not file.filename or not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="File must be a .zip file")

    # Create temporary file to save upload
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    tmp_path = tmp_file.name
    temp_dir = None

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

<<<<<<< HEAD
        if TESTING_MODE:
            # TESTING MODE: Load data from batch_test.json
            print("=== TESTING MODE: Loading batch_test.json ===")
            batch_test_path = Path(__file__).parent / "batch_test.json"
            with open(batch_test_path, 'r') as f:
                results = json.load(f)

            # Copy media files from tests directory (they should already be there)
            print("Using existing media files in tests directory")
            print(f"Loaded {len(results)} files from batch_test.json")

        else:
            # REAL MODE: Process with Gemini API
            # Step 1: Process the zip file (preprocessing)
            print("=== Step 1: Preprocessing ===")
            results, temp_dir = process_zip_file(tmp_path)

            # Step 2: Copy media files to tests directory for serving
            print("\n=== Step 2: Copying media files ===")
            tests_dir = Path(__file__).parent / "tests"
            tests_dir.mkdir(exist_ok=True)

            # Walk through temp directory and copy files
            for root, dirs, files in os.walk(temp_dir):
                for filename in files:
                    file_lower = filename.lower()
                    if filename.startswith('.') or '__MACOSX' in root:
                        continue
                    if file_lower.endswith('.png') or file_lower.endswith('.mp4'):
                        src_path = os.path.join(root, filename)
                        dst_path = tests_dir / filename
                        shutil.copy2(src_path, dst_path)
                        print(f"   Copied {filename} to tests directory")

            # Step 3: Batch analyze videos and images with Gemini (concurrent processing)
            print("\n=== Step 3: Gemini Batch Analysis (Videos + Images) ===")

            with ThreadPoolExecutor(max_workers=2) as executor:
                video_future = executor.submit(batch_analyze_videos, results, 3)
                image_future = executor.submit(batch_analyze_images, results, 10)

                # Get results as they complete
                video_results = video_future.result()
                image_results = image_future.result()

            # Update results with Gemini analysis
            for filename, analysis in video_results.items():
                results[filename] = analysis
            for filename, analysis in image_results.items():
                results[filename] = analysis

            print(f"\nCompleted Gemini analysis for {len(video_results)} videos and {len(image_results)} images")
=======
        # Process the zip file using main.py (now includes full pipeline)
        # Extract dataset name from original filename
        dataset_name = Path(file.filename).stem
        results = process_zip_file(tmp_path, dataset_name)
>>>>>>> db4131f (proper function for preprocessing and analysis for fastapi)

        return JSONResponse(content=results)

    except Exception as e:
        # Print full traceback for debugging
        print("ERROR occurred during processing:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

    finally:
        # Clean up temporary files
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        if not TESTING_MODE and temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"Cleaned up temporary directory: {temp_dir}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
