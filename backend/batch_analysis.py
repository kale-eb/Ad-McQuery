import json
import os
import time
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()


def batch_analyze_videos(preprocessed_videos: Dict[str, Dict[str, Any]], batch_size: int = 5) -> Dict[str, Dict[str, Any]]:
    """
    Analyze preprocessed videos in batches using Gemini with multithreading.
    
    Args:
        preprocessed_videos: Dictionary mapping filename to preprocessed video data
        batch_size: Number of videos to process in each Gemini call
    
    Returns:
        Dictionary mapping filename to complete analysis (preprocessing + Gemini analysis)
    """
    # Configure Gemini API
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    
    # Filter out only video files (mp4)
    video_files = {k: v for k, v in preprocessed_videos.items() 
                   if k.lower().endswith('.mp4') and 'error' not in v}
    
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
        
        print(f"\nProcessing batch {batch_num} ({len(batch_filenames)} videos)...")
        batch_start = time.time()
        
        try:
            # Create batch prompt
            batch_prompt = create_batch_prompt(batch_data)
            
            # Get Gemini analysis for batch
            response = model.generate_content(
                batch_prompt,
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
                    batch_results[filename] = {
                        **batch_data[filename],  # Original preprocessing data
                        **batch_analysis[filename]  # Gemini analysis
                    }
                else:
                    batch_results[filename] = {
                        **batch_data[filename],
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
                batch_results[filename] = {
                    **batch_data[filename],
                    "analysis_error": str(e)
                }
            return batch_results
    
    # Process all batches concurrently
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
    
    prompt = f"""Analyze these {len(batch_data)} video advertisements for targeting and marketing effectiveness.

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


def batch_analyze_images(preprocessed_images: Dict[str, Dict[str, Any]], batch_size: int = 10) -> Dict[str, Dict[str, Any]]:
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
    
    # Filter out only image files (png)
    image_files = {k: v for k, v in preprocessed_images.items() 
                   if k.lower().endswith('.png') and 'error' not in v}
    
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
            # Create image-specific batch prompt
            batch_prompt = create_image_batch_prompt(batch_data)
            
            response = model.generate_content(
                batch_prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json"
                )
            )
            
            batch_analysis = parse_batch_response(response.text, batch_filenames)
            
            batch_results = {}
            for filename in batch_filenames:
                if filename in batch_analysis:
                    batch_results[filename] = {
                        **batch_data[filename],
                        **batch_analysis[filename]
                    }
                else:
                    batch_results[filename] = {
                        **batch_data[filename],
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
                batch_results[filename] = {
                    **batch_data[filename],
                    "analysis_error": str(e)
                }
            return batch_results
    
    # Process all image batches concurrently
    with ThreadPoolExecutor(max_workers=len(batches)) as executor:
        future_to_batch = {executor.submit(process_image_batch, batch): batch for batch in batches}
        
        for future in as_completed(future_to_batch):
            batch_results = future.result()
            results.update(batch_results)
    
    return results


def create_image_batch_prompt(batch_data: Dict[str, Dict[str, Any]]) -> str:
    """
    Create a prompt for batch image analysis.
    """
    images_info = []
    for filename, data in batch_data.items():
        text = data.get('text', 'No text extracted')
        resolution = data.get('resolution', 'Unknown')
        colors = data.get('dominant_colors', [])
        
        images_info.append(f"""
Image: {filename}
Resolution: {resolution}
Extracted Text: "{text}"
Dominant Colors: {colors[:3] if colors else 'Unknown'}
""")
    
    prompt = f"""Analyze these {len(batch_data)} image advertisements for targeting and marketing effectiveness.

{chr(10).join(images_info)}

For EACH image, provide analysis in the following JSON format:
{{
    "{list(batch_data.keys())[0]}": {{
        "targeting_type": "first_impression" or "retargeting",
        "comprehension_rating": 1-5,
        "target_age_range": "18-25", "25-35", "35-50", or "50+",
        "target_income_level": "low", "middle", "high", or "mixed",
        "target_geographic_area": "specific area type",
        "target_interests": ["up to 3 interests"],
        "visual_appeal_rating": 1-5,
        "conversion_focused": true/false
    }},
    ... (repeat for all images)
}}

CRITERIA:
- visual_appeal_rating: 1=unappealing, 5=extremely eye-catching
- Other criteria same as video analysis

Analyze each image independently based on text, colors, and visual elements."""
    
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
    video_results = batch_analyze_videos(preprocessed_data, batch_size=5)
    print(f"\nAnalyzed {len(video_results)} videos")
    
    # Analyze images in batches
    image_results = batch_analyze_images(preprocessed_data, batch_size=10)
    print(f"Analyzed {len(image_results)} images")
    
    # Combine results
    all_results = {**video_results, **image_results}
    
    # Save results
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n=== Batch Analysis Complete ===")
    print(f"Total files analyzed: {len(all_results)}")
    print(f"Results saved to: {output_file}")