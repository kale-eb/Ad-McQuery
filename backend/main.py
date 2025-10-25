import os
import zipfile
import tempfile
import time
from pathlib import Path
from typing import Dict, Any
from PIL import Image

from image_preprocess import extract_image_features
from video_preprocessing import preprocess_video
from batch_analysis import batch_analyze_videos, batch_analyze_images


def process_zip_file(zip_path: str) -> Dict[str, Dict[str, Any]]:
    """
    Unzip a file and process all media files (PNG images and MP4 videos).

    Args:
        zip_path: Path to the zip file

    Returns:
        Dictionary where:
        - key: filename (without directory path)
        - value: preprocessing result dictionary from image_preprocess or video_preprocessing
    """
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"Zip file not found: {zip_path}")

    if not zipfile.is_zipfile(zip_path):
        raise ValueError(f"File is not a valid zip file: {zip_path}")

    results = {}

    # Create temporary directory for extraction
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Extracting zip file to temporary directory: {temp_dir}")

        # Extract zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Walk through all extracted files
        for root, dirs, files in os.walk(temp_dir):
            for filename in files:
                file_path = os.path.join(root, filename)
                file_lower = filename.lower()

                # Skip hidden files and __MACOSX
                if filename.startswith('.') or '__MACOSX' in file_path:
                    continue

                try:
                    # Process PNG images
                    if file_lower.endswith('.png'):
                        print(f"Processing image: {filename}")
                        img_start = time.time()
                        with Image.open(file_path) as img:
                            results[filename] = extract_image_features(img)
                        img_time = time.time() - img_start
                        print(f"   Completed image preprocessing ({img_time:.2f}s)")

                    # Process MP4 videos
                    elif file_lower.endswith('.mp4'):
                        print(f"Processing video: {filename}")
                        video_start = time.time()
                        results[filename] = preprocess_video(file_path)
                        video_time = time.time() - video_start
                        print(f"   Completed video preprocessing ({video_time:.2f}s)")

                    else:
                        print(f"Skipping unsupported file: {filename}")

                except Exception as e:
                    print(f"Error processing {filename}: {e}")
                    results[filename] = {
                        "error": str(e),
                        "status": "failed"
                    }

    print(f"\n=== Preprocessing Complete ===")
    print(f"Successfully processed {len([r for r in results.values() if 'error' not in r])} files")
    print(f"Failed: {len([r for r in results.values() if 'error' in r])} files")

    return results


def save_results(results: Dict[str, Dict[str, Any]], output_path: str):
    """
    Save preprocessing results to JSON file.
    """
    import json
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python main.py <zip_file_path> [output_json_path]")
        print("\nThis script will:")
        print("  1. Extract the zip file")
        print("  2. Process all .png files with image preprocessing")
        print("  3. Process all .mp4 files with video preprocessing (metadata only)")
        print("  4. Batch analyze videos and images with Gemini")
        print("  5. Return complete analysis results")
        print("\nRequires:")
        print("  - GEMINI_API_KEY environment variable (for batch analysis)")
        sys.exit(1)

    zip_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        # Step 1: Process all files in zip (preprocessing)
        print("=== Step 1: Preprocessing ===")
        preprocess_start = time.time()
        results = process_zip_file(zip_path)
        preprocess_time = time.time() - preprocess_start
        print(f"Total preprocessing time: {preprocess_time:.2f}s")

        # Step 2: Batch analyze videos and images with Gemini (concurrent processing)
        print("\n=== Step 2: Gemini Batch Analysis (Videos + Images) ===")
        gemini_start = time.time()
        
        # Run video and image analysis concurrently
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            video_future = executor.submit(batch_analyze_videos, results, 5)
            image_future = executor.submit(batch_analyze_images, results, 10)
            
            # Get results as they complete
            video_results = video_future.result()
            image_results = image_future.result()
        
        gemini_time = time.time() - gemini_start
        
        # Update results with Gemini analysis
        for filename, analysis in video_results.items():
            results[filename] = analysis
        for filename, analysis in image_results.items():
            results[filename] = analysis
        
        print(f"\nCompleted Gemini analysis for {len(video_results)} videos and {len(image_results)} images")
        print(f"Total Gemini analysis time: {gemini_time:.2f}s")

        # Optionally save to JSON
        if output_path:
            save_results(results, output_path)

        # Print summary
        # Calculate timing summary
        total_time = preprocess_time + gemini_time
        
        print(f"\n=== Final Summary ===")
        print(f"Total files processed: {len(results)}")
        
        video_count = len([f for f in results.keys() if f.lower().endswith('.mp4')])
        image_count = len([f for f in results.keys() if f.lower().endswith('.png')])
        analyzed_count = len([r for r in results.values() if 'targeting_type' in r])
        
        print(f"Images processed: {image_count}")
        print(f"Videos processed: {video_count}")
        print(f"Total files with Gemini analysis: {analyzed_count}")
        
        print(f"\n=== Timing Summary ===")
        print(f"Preprocessing time: {preprocess_time:.2f}s")
        print(f"Gemini analysis time: {gemini_time:.2f}s")
        print(f"Total processing time: {total_time:.2f}s")
        total_files = video_count + image_count
        if total_files > 0:
            print(f"Average time per file (full pipeline): {total_time/total_files:.2f}s")
        
        print(f"\nProcessed files:")
        for filename in results.keys():
            if "error" in results[filename]:
                status = " Error"
            elif "targeting_type" in results[filename]:
                status = " Complete (with Gemini)"
            else:
                status = " Preprocessed (images)"
            print(f"  {status} {filename}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)