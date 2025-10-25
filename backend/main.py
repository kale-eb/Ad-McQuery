import os
import zipfile
import tempfile
from pathlib import Path
from typing import Dict, Any
from PIL import Image

from image_preprocess import extract_image_features
from video_preprocessing import preprocess_video
from batch_analysis import batch_analyze_videos


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
                        with Image.open(file_path) as img:
                            results[filename] = extract_image_features(img)
                        print(f"   Completed image preprocessing")

                    # Process MP4 videos
                    elif file_lower.endswith('.mp4'):
                        print(f"Processing video: {filename}")
                        results[filename] = preprocess_video(file_path)
                        print(f"   Completed video preprocessing")

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
        print("  3. Process all .mp4 files with video preprocessing + Whisper")
        print("  4. Batch analyze videos with Gemini (5 at a time)")
        print("  5. Return complete analysis results")
        print("\nRequires:")
        print("  - OPENAI_API_KEY environment variable (for video transcription)")
        print("  - GEMINI_API_KEY environment variable (for batch analysis)")
        print("  - ffmpeg installed (for video audio extraction)")
        sys.exit(1)

    zip_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        # Step 1: Process all files in zip (preprocessing)
        print("=== Step 1: Preprocessing ===")
        results = process_zip_file(zip_path)

        # Step 2: Batch analyze videos with Gemini (always run for videos)
        print("\n=== Step 2: Gemini Batch Analysis for Videos ===")
        video_results = batch_analyze_videos(results, batch_size=5)
        
        # Update results with Gemini analysis for videos only
        for filename, analysis in video_results.items():
            results[filename] = analysis
        
        print(f"\nCompleted Gemini analysis for {len(video_results)} videos")

        # Optionally save to JSON
        if output_path:
            save_results(results, output_path)

        # Print summary
        print(f"\n=== Final Summary ===")
        print(f"Total files processed: {len(results)}")
        
        video_count = len([f for f in results.keys() if f.lower().endswith('.mp4')])
        analyzed_count = len([r for r in results.values() if 'targeting_type' in r])
        print(f"Videos with Gemini analysis: {analyzed_count}/{video_count}")
        
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