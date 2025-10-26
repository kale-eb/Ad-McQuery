import json
import os
import time
import subprocess
import tempfile
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()



def batch_analyze_videos(preprocessed_videos: Dict[str, Dict[str, Any]], batch_size: int = 3) -> Dict[str, Dict[str, Any]]:
    """
    Analyze preprocessed videos in batches using Gemini with multithreading.
    
    Args:
        preprocessed_videos: Dictionary mapping filename to preprocessed video data
        batch_size: Number of videos to process in each Gemini call (default: 3)
    
    Returns:
        Dictionary mapping filename to complete analysis (preprocessing + Gemini analysis)
    """
    # Configure Gemini API
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    
    # Filter out only video files (mp4) and ensure they have file paths
    video_files = {k: v for k, v in preprocessed_videos.items() 
                   if k.lower().endswith('.mp4') and 'error' not in v and '_temp_file_path' in v}
    
    if not video_files:
        print("No valid video files to analyze")
        return {}
    
    # Split into batches
    filenames = list(video_files.keys())
    batches = []
    for i in range(0, len(filenames), batch_size):
        batch_filenames = filenames[i:i + batch_size]
        batch_data = {fn: video_files[fn] for fn in batch_filenames}
        batches.append((i//batch_size + 1, batch_filenames, batch_data))
    
    results = {}
    
    def process_batch(batch_info):
        batch_num, batch_filenames, batch_data = batch_info
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        print(f"\nProcessing video batch {batch_num} ({len(batch_filenames)} videos)...")
        batch_start = time.time()
        file_prep_time = 0
        api_call_time = 0
        
        try:
            # Create batch prompt
            batch_prompt = create_batch_prompt(batch_data)
            
            # Prepare video files for Gemini
            content_parts = [batch_prompt]
            
            # Add each video file to the content
            import base64
            for i, filename in enumerate(batch_filenames):
                try:
                    file_path = batch_data[filename]['_temp_file_path']
                    
                    with open(file_path, 'rb') as f:
                        video_bytes = f.read()
                    
                    video_part = {
                        "mime_type": "video/mp4",
                        "data": base64.b64encode(video_bytes).decode('utf-8')
                    }
                    content_parts.append(video_part)
                        
                except Exception as e:
                    print(f"   Warning: Could not process video file {filename}: {e}")
                    # Continue without this video
                    continue
            
            # Get Gemini analysis for batch with video content
            response = model.generate_content(
                content_parts,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json"
                )
            )
            
            # Parse batch response
            batch_analysis = parse_batch_response(response.text, batch_filenames)
            
            # Combine with preprocessing data
            batch_results = {}
            for filename in batch_filenames:
                if filename in batch_analysis:
                    # Clean preprocessing data (remove temp file path)
                    clean_preprocessing_data = {k: v for k, v in batch_data[filename].items() if k != '_temp_file_path'}
                    batch_results[filename] = {
                        **clean_preprocessing_data,  # Original preprocessing data
                        **batch_analysis[filename]  # Gemini analysis
                    }
                else:
                    # Clean preprocessing data (remove temp file path)
                    clean_preprocessing_data = {k: v for k, v in batch_data[filename].items() if k != '_temp_file_path'}
                    batch_results[filename] = {
                        **clean_preprocessing_data,
                        "analysis_error": "Failed to get Gemini analysis"
                    }
            
            batch_time = time.time() - batch_start
            print(f"   Batch {batch_num} completed ({batch_time:.2f}s)")
            return batch_results
                    
        except Exception as e:
            batch_time = time.time() - batch_start
            print(f"   Batch {batch_num} failed ({batch_time:.2f}s): {e}")
            # Add error for all videos in batch
            batch_results = {}
            for filename in batch_filenames:
                # Clean preprocessing data (remove temp file path)
                clean_preprocessing_data = {k: v for k, v in batch_data[filename].items() if k != '_temp_file_path'}
                batch_results[filename] = {
                    **clean_preprocessing_data,
                    "analysis_error": str(e)
                }
            return batch_results
    
    # Process ALL batches concurrently - let Gemini handle it
    with ThreadPoolExecutor(max_workers=len(batches)) as executor:
        future_to_batch = {executor.submit(process_batch, batch): batch for batch in batches}
        
        for future in as_completed(future_to_batch):
            batch_results = future.result()
            results.update(batch_results)
    
    return results


def create_batch_prompt(batch_data: Dict[str, Dict[str, Any]]) -> str:
    """
    Create a prompt for batch video analysis using indices.
    """
    # Load prompts from JSON
    with open(os.path.join(os.path.dirname(__file__), 'prompts.json'), 'r') as f:
        prompts = json.load(f)
    
    video_prompt = prompts['video_analysis']
    
    videos_info = []
    filenames = list(batch_data.keys())
    
    for i, filename in enumerate(filenames):
        data = batch_data[filename]
        length = data.get('length', 0)
        resolution = data.get('resolution', 'Unknown')
        aspect_ratio = data.get('aspect_ratio', 'Unknown')
        
        videos_info.append(f"""
Video {i}: {filename}
Duration: {length} seconds
Resolution: {resolution}
Aspect Ratio: {aspect_ratio}
""")
    
    # Create format example using indices
    format_str = json.dumps({str(i): video_prompt['format'] for i in range(len(batch_data))}, indent=4)
    criteria_str = '\n'.join([f"- {k}: {v}" for k, v in video_prompt['criteria'].items()])
    
    prompt = f"""Analyze these {len(batch_data)} video advertisements for meaningful signals.

{chr(10).join(videos_info)}

For EACH video, provide analysis using the video INDEX as the key in the following JSON format:
{format_str}

ANALYSIS CRITERIA:
{criteria_str}

{video_prompt['instruction']}

IMPORTANT: Use the video index (0, 1, 2, etc.) as the JSON key, not the filename."""
    
    return prompt


def parse_batch_response(response_text: str, expected_filenames: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Parse the batch response from Gemini using indices and map back to filenames.
    """
    try:
        # Clean up response
        if response_text.startswith('```json'):
            response_text = response_text.replace('```json', '').replace('```', '').strip()
        
        batch_analysis = json.loads(response_text)
        
        # Map indices back to filenames
        result = {}
        for i, filename in enumerate(expected_filenames):
            index_key = str(i)
            if index_key in batch_analysis:
                result[filename] = batch_analysis[index_key]
            else:
                print(f"Warning: No analysis found for index {i} (file: {filename})")
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"Error parsing Gemini response: {e}")
        print(f"Raw response: {response_text[:500]}...")
        return {}


def batch_analyze_images(preprocessed_images: Dict[str, Dict[str, Any]], batch_size: int = 5) -> Dict[str, Dict[str, Any]]:
    """
    Analyze preprocessed images in batches using Gemini with multithreading.
    Similar to video analysis but optimized for images.
    
    Args:
        preprocessed_images: Dictionary mapping filename to preprocessed image data
        batch_size: Number of images to process in each Gemini call (higher for images)
    
    Returns:
        Dictionary mapping filename to complete analysis
    """
    # Configure Gemini API
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    
    # Filter out only image files (png) and ensure they have file paths
    image_files = {k: v for k, v in preprocessed_images.items() 
                   if k.lower().endswith('.png') and 'error' not in v and '_temp_file_path' in v}
    
    if not image_files:
        print("No valid image files to analyze")
        return {}
    
    # Split into batches
    filenames = list(image_files.keys())
    batches = []
    for i in range(0, len(filenames), batch_size):
        batch_filenames = filenames[i:i + batch_size]
        batch_data = {fn: image_files[fn] for fn in batch_filenames}
        batches.append((i//batch_size + 1, batch_filenames, batch_data))
    
    results = {}
    
    def process_image_batch(batch_info):
        batch_num, batch_filenames, batch_data = batch_info
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        print(f"\nProcessing image batch {batch_num} ({len(batch_filenames)} images)...")
        batch_start = time.time()
        
        try:
            # Create image-specific batch prompt with actual image files
            batch_prompt = create_image_batch_prompt(batch_data)
            
            # Prepare content parts with actual images
            content_parts = [batch_prompt]
            
            # Add each image file to the content
            import base64
            from PIL import Image
            from io import BytesIO
            
            for i, filename in enumerate(batch_filenames):
                try:
                    file_path = batch_data[filename]['_temp_file_path']
                    
                    # Read and encode image file
                    with Image.open(file_path) as img:
                        buffer = BytesIO()
                        img.save(buffer, format='PNG')
                        image_bytes = buffer.getvalue()
                    
                    image_part = {
                        "mime_type": "image/png",
                        "data": base64.b64encode(image_bytes).decode('utf-8')
                    }
                    content_parts.append(image_part)
                        
                except Exception as e:
                    print(f"   Warning: Could not process image file {filename}: {e}")
                    continue
            
            # Send actual image files + prompt to Gemini
            response = model.generate_content(
                content_parts,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json"
                )
            )
            
            batch_analysis = parse_batch_response(response.text, batch_filenames)
            
            batch_results = {}
            for filename in batch_filenames:
                if filename in batch_analysis:
                    # Clean preprocessing data (remove temp file path)
                    clean_preprocessing_data = {k: v for k, v in batch_data[filename].items() if k != '_temp_file_path'}
                    batch_results[filename] = {
                        **clean_preprocessing_data,  # Original preprocessing data
                        **batch_analysis[filename]  # Gemini analysis
                    }
                else:
                    # Clean preprocessing data (remove temp file path)
                    clean_preprocessing_data = {k: v for k, v in batch_data[filename].items() if k != '_temp_file_path'}
                    batch_results[filename] = {
                        **clean_preprocessing_data,
                        "analysis_error": "Failed to get Gemini analysis"
                    }
            
            batch_time = time.time() - batch_start
            print(f"   Image batch {batch_num} completed ({batch_time:.2f}s)")
            return batch_results
                    
        except Exception as e:
            batch_time = time.time() - batch_start
            print(f"   Image batch {batch_num} failed ({batch_time:.2f}s): {e}")
            batch_results = {}
            for filename in batch_filenames:
                # Clean preprocessing data (remove temp file path)
                clean_preprocessing_data = {k: v for k, v in batch_data[filename].items() if k != '_temp_file_path'}
                batch_results[filename] = {
                    **clean_preprocessing_data,
                    "analysis_error": str(e)
                }
            return batch_results
    
    # Process image batches with limited concurrency
    max_concurrent = min(3, len(batches))  # Max 3 concurrent requests
    with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
        future_to_batch = {executor.submit(process_image_batch, batch): batch for batch in batches}
        
        for future in as_completed(future_to_batch):
            batch_results = future.result()
            results.update(batch_results)
    
    return results


def create_image_batch_prompt(batch_data: Dict[str, Dict[str, Any]]) -> str:
    """
    Create a prompt for batch image analysis using the new format from prompts.json.
    """
    # Load prompts from JSON
    with open(os.path.join(os.path.dirname(__file__), 'prompts.json'), 'r') as f:
        prompts = json.load(f)
    
    image_prompt = prompts['image_analysis']
    
    # Create images info with metadata and OCR details
    images_info = []
    filenames = list(batch_data.keys())
    
    for i, filename in enumerate(filenames):
        data = batch_data[filename]
        resolution = data.get('resolution', 'Unknown')
        
        images_info.append(f"""
Image {i}: {filename}
Resolution: {resolution}
""")
    
    # Create format example using indices
    format_str = json.dumps({str(i): image_prompt['format'] for i in range(len(batch_data))}, indent=4)
    criteria_str = '\n'.join([f"- {k}: {v}" for k, v in image_prompt['criteria'].items()])
    
    prompt = f"""Analyze these {len(batch_data)} image advertisements for visual and textual characteristics.

{chr(10).join(images_info)}

For EACH image, provide analysis using the image INDEX as the key in the following JSON format:
{format_str}

ANALYSIS CRITERIA:
{criteria_str}

{image_prompt['instruction']}

IMPORTANT: Use the image index (0, 1, 2, etc.) as the JSON key, not the filename."""
    
    return prompt


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python batch_analysis.py <preprocessed_results.json> [output.json]")
        print("\nThis script:")
        print("  1. Loads preprocessed results from main.py")
        print("  2. Sends videos/images to Gemini in batches")
        print("  3. Returns complete analysis for all media files")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "batch_analysis_results.json"
    
    # Load preprocessed data
    with open(input_file, 'r') as f:
        preprocessed_data = json.load(f)
    
    print(f"Loaded {len(preprocessed_data)} preprocessed files")
    
    # Analyze videos in batches
    video_results = batch_analyze_videos(preprocessed_data, batch_size=3)
    print(f"\nAnalyzed {len(video_results)} videos")
    
    # Analyze images in batches
    image_results = batch_analyze_images(preprocessed_data, batch_size=5)
    print(f"Analyzed {len(image_results)} images")
    
    # Combine results
    all_results = {**video_results, **image_results}
    
    # Save results
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n=== Batch Analysis Complete ===")
    print(f"Total files analyzed: {len(all_results)}")
    print(f"Results saved to: {output_file}")