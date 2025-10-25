import json
import os
from typing import Dict, Any, List
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()


def batch_analyze_videos(preprocessed_videos: Dict[str, Dict[str, Any]], batch_size: int = 5) -> Dict[str, Dict[str, Any]]:
    """
    Analyze preprocessed videos in batches using Gemini.
    
    Args:
        preprocessed_videos: Dictionary mapping filename to preprocessed video data
        batch_size: Number of videos to process in each Gemini call
    
    Returns:
        Dictionary mapping filename to complete analysis (preprocessing + Gemini analysis)
    """
    # Configure Gemini API
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Filter out only video files (mp4)
    video_files = {k: v for k, v in preprocessed_videos.items() 
                   if k.lower().endswith('.mp4') and 'error' not in v}
    
    if not video_files:
        print("No valid video files to analyze")
        return {}
    
    # Process in batches
    results = {}
    filenames = list(video_files.keys())
    
    for i in range(0, len(filenames), batch_size):
        batch_filenames = filenames[i:i + batch_size]
        batch_data = {fn: video_files[fn] for fn in batch_filenames}
        
        print(f"\nProcessing batch {i//batch_size + 1} ({len(batch_filenames)} videos)...")
        
        # Create batch prompt
        batch_prompt = create_batch_prompt(batch_data)
        
        try:
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
            for filename in batch_filenames:
                if filename in batch_analysis:
                    results[filename] = {
                        **video_files[filename],  # Original preprocessing data
                        **batch_analysis[filename]  # Gemini analysis
                    }
                else:
                    results[filename] = {
                        **video_files[filename],
                        "analysis_error": "Failed to get Gemini analysis"
                    }
                    
        except Exception as e:
            print(f"Error processing batch: {e}")
            # Add error for all videos in batch
            for filename in batch_filenames:
                results[filename] = {
                    **video_files[filename],
                    "analysis_error": str(e)
                }
    
    return results


def create_batch_prompt(batch_data: Dict[str, Dict[str, Any]]) -> str:
    """
    Create a prompt for batch video analysis.
    """
    videos_info = []
    for filename, data in batch_data.items():
        transcript = data.get('whisper_transcript', {}).get('full_text', 'No transcript available')
        length = data.get('length', 0)
        resolution = data.get('resolution', 'Unknown')
        
        videos_info.append(f"""
Video: {filename}
Duration: {length} seconds
Resolution: {resolution}
Transcript: "{transcript}"
""")
    
    prompt = f"""Analyze these {len(batch_data)} video advertisements for targeting and marketing effectiveness.

{chr(10).join(videos_info)}

For EACH video, provide analysis in the following JSON format:
{{
    "{list(batch_data.keys())[0]}": {{
        "targeting_type": "first_impression" or "retargeting",
        "comprehension_rating": 1-5 (how easy to understand),
        "target_age_range": "specific age range like 18-25, 25-35, 35-50, 50+",
        "target_income_level": "specific income level",
        "target_geographic_area": "specific geographic type that the ad targets (such as 'X county, East Coast US')",
        "target_interests": ["list", "of", "customer", "interests", "(up to 3)"],
        "hook_rating": 1-5 (how engaging are first few seconds either visually or verbally),
        "conversion_focused": true/false (direct CTA vs general brand awareness)
    }},
    ... (repeat for all videos)
}}

ANALYSIS CRITERIA:
- targeting_type: "first_impression" if introducing brand/product, "retargeting" if assumes familiarity
- comprehension_rating: 1=requires the viewer to really think to understand the message, 5=crystal clear message, even a toddler could understand
- target_age_range: infer from language, references, visual style
- target_income_level: infer from product type, pricing cues, lifestyle depicted
- target_geographic_area: infer from product, explicit mentions, setting, cultural references
- target_interests: what hobbies/interests would this customer have
- hook_rating: 1=non-engaging start, 5=EXTREMELY gripping/interesting (stunt occurs, something unexpected happens, etc.). Remember the AVERAGE video is a 2.5
- conversion_focused: true if has clear IMMEDIATE call-to-action (download, buy now, etc.), false if just building awareness (x product is good)

Analyze each video independently and objectively."""
    
    return prompt


def parse_batch_response(response_text: str, expected_filenames: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Parse the batch response from Gemini.
    """
    try:
        # Clean up response
        if response_text.startswith('```json'):
            response_text = response_text.replace('```json', '').replace('```', '').strip()
        
        batch_analysis = json.loads(response_text)
        
        # Validate we got analysis for expected files
        result = {}
        for filename in expected_filenames:
            if filename in batch_analysis:
                result[filename] = batch_analysis[filename]
            else:
                print(f"Warning: No analysis found for {filename}")
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"Error parsing Gemini response: {e}")
        return {}


def batch_analyze_images(preprocessed_images: Dict[str, Dict[str, Any]], batch_size: int = 10) -> Dict[str, Dict[str, Any]]:
    """
    Analyze preprocessed images in batches using Gemini.
    Similar to video analysis but optimized for images.
    
    Args:
        preprocessed_images: Dictionary mapping filename to preprocessed image data
        batch_size: Number of images to process in each Gemini call (higher for images)
    
    Returns:
        Dictionary mapping filename to complete analysis
    """
    # Configure Gemini API
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Filter out only image files (png)
    image_files = {k: v for k, v in preprocessed_images.items() 
                   if k.lower().endswith('.png') and 'error' not in v}
    
    if not image_files:
        print("No valid image files to analyze")
        return {}
    
    # Process in batches (similar to video but with image-specific prompt)
    results = {}
    filenames = list(image_files.keys())
    
    for i in range(0, len(filenames), batch_size):
        batch_filenames = filenames[i:i + batch_size]
        batch_data = {fn: image_files[fn] for fn in batch_filenames}
        
        print(f"\nProcessing image batch {i//batch_size + 1} ({len(batch_filenames)} images)...")
        
        # Create image-specific batch prompt
        batch_prompt = create_image_batch_prompt(batch_data)
        
        try:
            response = model.generate_content(
                batch_prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json"
                )
            )
            
            batch_analysis = parse_batch_response(response.text, batch_filenames)
            
            for filename in batch_filenames:
                if filename in batch_analysis:
                    results[filename] = {
                        **image_files[filename],
                        **batch_analysis[filename]
                    }
                else:
                    results[filename] = {
                        **image_files[filename],
                        "analysis_error": "Failed to get Gemini analysis"
                    }
                    
        except Exception as e:
            print(f"Error processing image batch: {e}")
            for filename in batch_filenames:
                results[filename] = {
                    **image_files[filename],
                    "analysis_error": str(e)
                }
    
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