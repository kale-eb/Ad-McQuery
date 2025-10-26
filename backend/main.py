import os
import zipfile
import tempfile
import time
import subprocess
import json
from pathlib import Path
from typing import Dict, Any
from PIL import Image

from image_preprocess import extract_image_features
from video_preprocessing import preprocess_video
from batch_analysis import batch_analyze_videos, batch_analyze_images


def compress_image_for_gemini(image_path: str, max_size_kb: int = 300) -> str:
    """
    Compress image for Gemini API (max 500KB).
    Returns path to compressed image or original if compression not needed.
    """
    try:
        current_size_kb = os.path.getsize(image_path) / 1024
        
        # If already small enough, return original
        if current_size_kb <= max_size_kb:
            return image_path
        
        # Create compressed version
        output_path = image_path.replace('.png', '_compressed.png')
        
        with Image.open(image_path) as img:
            # Calculate compression ratio needed
            compression_ratio = max_size_kb / current_size_kb
            
            # Try quality-based compression first
            quality = max(int(95 * compression_ratio), 10)
            img.save(output_path, 'PNG', optimize=True, quality=quality)
            
            # If still too large, resize
            if os.path.getsize(output_path) / 1024 > max_size_kb:
                # Calculate new dimensions
                scale_factor = (max_size_kb / (os.path.getsize(output_path) / 1024)) ** 0.5
                new_width = int(img.width * scale_factor)
                new_height = int(img.height * scale_factor)
                
                # Resize and save
                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                img_resized.save(output_path, 'PNG', optimize=True, quality=85)
            
            compressed_size_kb = os.path.getsize(output_path) / 1024
            print(f"   Compressed image: {current_size_kb:.1f}KB → {compressed_size_kb:.1f}KB")
            return output_path
            
    except Exception as e:
        print(f"   Warning: Image compression failed: {e}")
        return image_path


def compress_video_for_gemini(input_path: str, max_size_mb: int = 2) -> str:
    """
    Compress video for Gemini API (max 2MB, 720p).
    Returns path to compressed video or original if compression not needed.
    """
    try:
        current_size_mb = os.path.getsize(input_path) / (1024 * 1024)
        
        # If already small enough, check resolution
        if current_size_mb <= max_size_mb:
            probe_cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', input_path]
            result = subprocess.run(probe_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                probe_data = json.loads(result.stdout)
                video_stream = next((s for s in probe_data['streams'] if s['codec_type'] == 'video'), None)
                if video_stream and int(video_stream.get('height', 0)) <= 720:
                    return input_path
        
        # Create compressed version
        output_path = input_path.replace('.mp4', '_compressed.mp4')
        
        # Get duration for bitrate calculation
        duration_cmd = ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', '-of', 'csv=p=0', input_path]
        duration_result = subprocess.run(duration_cmd, capture_output=True, text=True)
        duration = float(duration_result.stdout.strip()) if duration_result.returncode == 0 else 30
        
        target_bitrate_kbps = max(int((max_size_mb * 8 * 1024) / duration * 0.9), 100)
        
        cmd = [
            'ffmpeg', '-i', input_path, '-vf', 'scale=-2:min(720\\,ih)',
            '-c:v', 'libx264', '-b:v', f'{target_bitrate_kbps}k',
            '-c:a', 'aac', '-b:a', '64k', '-movflags', '+faststart',
            '-y', output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            compressed_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            if compressed_size_mb < current_size_mb:
                print(f"   Compressed: {current_size_mb:.2f}MB → {compressed_size_mb:.2f}MB")
                return output_path
        
        # Compression failed or didn't help
        if os.path.exists(output_path):
            os.remove(output_path)
        return input_path
        
    except Exception as e:
        print(f"   Warning: Compression failed: {e}")
        return input_path


def process_zip_file(zip_path: str, dataset_name: str = None) -> Dict[str, Dict[str, Any]]:
    """
    Complete processing pipeline: unzip, preprocess, and analyze all media files.
    Uses persistent storage in /datasets with caching.

    Args:
        zip_path: Path to the zip file

    Returns:
        Dictionary mapping filename to complete analysis results (preprocessing + Gemini)
    """
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"Zip file not found: {zip_path}")

    if not zipfile.is_zipfile(zip_path):
        raise ValueError(f"File is not a valid zip file: {zip_path}")

    # Get dataset name (use provided name or extract from zip path)
    zip_filename = dataset_name if dataset_name else Path(zip_path).stem
    backend_dir = Path(__file__).parent
    dataset_dir = backend_dir / "datasets" / zip_filename
    analysis_json_path = dataset_dir / f"{zip_filename}-analysis.json"

    # Step 1: Check for existing analysis
    if analysis_json_path.exists():
        print(f"Found existing analysis: {analysis_json_path}")
        with open(analysis_json_path, 'r') as f:
            return json.load(f)

    # Step 2: Check if dataset directory exists
    if dataset_dir.exists():
        print(f"Using existing dataset directory: {dataset_dir}")
        extract_dir = dataset_dir
    else:
        print(f"Creating new dataset directory: {dataset_dir}")
        dataset_dir.mkdir(parents=True, exist_ok=True)
        extract_dir = dataset_dir
        
        # Extract zip file to dataset directory
        print(f"Extracting zip file to: {extract_dir}")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Clean up extraction: move files from nested directories to root and remove garbage
        print("Cleaning up extracted structure...")
        for item in extract_dir.iterdir():
            if item.name == '__MACOSX':
                # Remove __MACOSX garbage
                import shutil
                shutil.rmtree(item)
                print(f"   Removed: {item.name}")
            elif item.is_dir() and item.name != 'images' and item.name != 'videos':
                # Move contents from nested directory (like 'ads/') to root
                for sub_item in item.iterdir():
                    target = extract_dir / sub_item.name
                    if target.exists():
                        if target.is_dir():
                            import shutil
                            shutil.rmtree(target)
                    sub_item.rename(target)
                    print(f"   Moved: {item.name}/{sub_item.name} → {sub_item.name}")
                # Remove now-empty nested directory
                item.rmdir()
                print(f"   Removed empty: {item.name}")

    # Step 3: Preprocessing - walk through all files in dataset directory
    print("=== Step 1: Preprocessing ===")
    preprocess_start = time.time()
    results = {}

    for root, dirs, files in os.walk(extract_dir):
        for filename in files:
            file_path = os.path.join(root, filename)
            file_lower = filename.lower()

            # Skip hidden files, __MACOSX, and analysis JSON
            if filename.startswith('.') or '__MACOSX' in file_path or filename.endswith('-analysis.json'):
                continue

            try:
                # Process PNG images
                if file_lower.endswith('.png'):
                    print(f"Processing image: {filename}")
                    img_start = time.time()
                    with Image.open(file_path) as img:
                        results[filename] = extract_image_features(img)
                    
                    # Compress image for batch analysis
                    compressed_path = compress_image_for_gemini(file_path)
                    results[filename]['_temp_file_path'] = compressed_path
                    
                    img_time = time.time() - img_start
                    print(f"   Completed image preprocessing ({img_time:.2f}s)")

                # Process MP4 videos
                elif file_lower.endswith('.mp4'):
                    print(f"Processing video: {filename}")
                    video_start = time.time()
                    results[filename] = preprocess_video(file_path)
                    
                    # Compress video for batch analysis
                    compressed_path = compress_video_for_gemini(file_path)
                    results[filename]['_temp_file_path'] = compressed_path
                    
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

    preprocess_time = time.time() - preprocess_start
    print(f"\n=== Preprocessing Complete ===")
    print(f"Successfully processed {len([r for r in results.values() if 'error' not in r])} files")
    print(f"Failed: {len([r for r in results.values() if 'error' in r])} files")
    print(f"Total preprocessing time: {preprocess_time:.2f}s")

    # Step 4: Gemini Batch Analysis (Images First, Then Videos)
    print("\n=== Step 2: Gemini Batch Analysis (Images First, Then Videos) ===")
    gemini_start = time.time()
    
    # First process images in 3 batches, all at once
    print("Processing images in 3 concurrent batches...")
    image_start = time.time()
    
    # Calculate batch size to split images into 3 batches
    image_files = {k: v for k, v in results.items() if k.lower().endswith('.png') and 'error' not in v}
    total_images = len(image_files)
    if total_images > 0:
        batch_size = max(1, (total_images + 2) // 3)  # Split into 3 batches
        num_batches = (total_images + batch_size - 1) // batch_size
        print(f"Sending {total_images} images in {num_batches} batches of {batch_size} - ALL sent simultaneously!")
        
        image_results = batch_analyze_images(results, batch_size)  # Process images in batches
    else:
        image_results = {}
    
    image_time = time.time() - image_start
    print(f"Image processing time: {image_time:.2f}s")
    
    # Then process videos (5 per batch, ALL batches sent at once)
    print("\nProcessing videos...")
    video_start = time.time()
    
    # Count total videos
    video_files = {k: v for k, v in results.items() if k.lower().endswith('.mp4') and 'error' not in v}
    total_videos = len(video_files)
    
    if total_videos > 0:
        batch_size = 5
        num_batches = (total_videos + batch_size - 1) // batch_size
        print(f"Sending {total_videos} videos in {num_batches} batches of {batch_size} - ALL sent simultaneously!")
        video_results = batch_analyze_videos(results, batch_size)  # 5 per batch, unlimited concurrent
    else:
        video_results = {}
        
    video_time = time.time() - video_start
    print(f"Video processing time: {video_time:.2f}s")
    
    gemini_time = time.time() - gemini_start
    
    # Update results with Gemini analysis
    for filename, analysis in video_results.items():
        results[filename] = analysis
    for filename, analysis in image_results.items():
        results[filename] = analysis
    
    print(f"\nCompleted Gemini analysis for {len(video_results)} videos and {len(image_results)} images")
    print(f"Total Gemini analysis time: {gemini_time:.2f}s")

    # Step 5: Clean up compressed files after analysis
    print("\n=== Cleaning up compressed files ===")
    compressed_files_removed = 0
    
    # Find all compressed files in the dataset directory
    for folder in ['images', 'videos']:
        folder_path = extract_dir / folder
        if folder_path.exists():
            for file_path in folder_path.iterdir():
                if '_compressed.' in file_path.name:
                    try:
                        file_path.unlink()  # Remove the file
                        compressed_files_removed += 1
                        print(f"   Removed: {file_path.name}")
                    except Exception as e:
                        print(f"   Warning: Failed to remove {file_path}: {e}")
    
    print(f"Removed {compressed_files_removed} compressed files")

    # Step 6: Save analysis results to dataset directory
    with open(analysis_json_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {analysis_json_path}")

    # Print final summary
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
            status = " Preprocessed only"
        print(f"  {status} {filename}")

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
        print("  1. Extract the zip file to /datasets")
        print("  2. Process all .png files with image preprocessing")
        print("  3. Process all .mp4 files with video preprocessing")
        print("  4. Batch analyze videos and images with Gemini")
        print("  5. Save complete analysis results")
        print("  6. Cache results for future use")
        print("\nRequires:")
        print("  - GEMINI_API_KEY environment variable (for batch analysis)")
        sys.exit(1)

    zip_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        # Process the zip file (full pipeline with caching)
        results = process_zip_file(zip_path)

        # Optionally save to additional output path
        if output_path:
            save_results(results, output_path)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)