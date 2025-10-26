import os
import json
import base64
from io import BytesIO
from typing import Dict, Any, List, Optional
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

from image_preprocess import extract_image_features

# Load environment variables
load_dotenv()


def analyze_image_with_gemini(image: Image.Image) -> Dict[str, Any]:
    """
    Analyze a Pillow image using Gemini 2.5 Flash API.
    Extracts image features and sends both the image and data to Gemini for analysis.

    Args:
        image: PIL Image object

    Returns:
        Dictionary containing:
        - product_visibility_score: "Low", "Medium", or "High"
        - negative_space_ratio: "Low", "Medium", or "High"
        - color_palette: List of up to 5 hex colors
        - age_demographic: "child", "teenage", "adult", or "senior"
        - gender_demographic: "male", "female", "other", or "N/A"
        - verbosity: "low", "medium", "high", or "none"
        - activity: "sedentary" or "dynamic"
        - call_to_action_level: 1-3 (based on OCR)
        - formality_level: 1-4 (based on OCR)
        - benefit_framing: "outcome", "feature", or "social_proof"
        - temporal_urgency_intensity: 1-3
        - scene_setting: "scene/location description"
        - fear_index: 0.0-1.0
        - comfort_index: 0.0-1.0
        - humor_index: 0.0-1.0
        - success_index: 0.0-1.0
        - love_index: 0.0-1.0
        - family_index: 0.0-1.0
        - adventure_index: 0.0-1.0
        - nostalgia_index: 0.0-1.0
        - health_index: 0.0-1.0
        - luxury_index: 0.0-1.0
    """
    # Configure Gemini API
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    # Step 1: Extract image features
    image_data = extract_image_features(image)

    # Step 2: Convert image to base64 for Gemini
    buffer = BytesIO()
    # Save in PNG format for consistency
    image.save(buffer, format='PNG')
    image_bytes = buffer.getvalue()
    image_b64 = base64.b64encode(image_bytes).decode('utf-8')

    # Load prompts from JSON
    with open(os.path.join(os.path.dirname(__file__), 'prompts.json'), 'r') as f:
        prompts = json.load(f)
    
    image_prompt = prompts['image_analysis']
    
    # Create format string from the format dict
    format_str = json.dumps(image_prompt['format'], indent=4)
    criteria_str = '\n'.join([f"- {k}: {v}" for k, v in image_prompt['criteria'].items()])
    
    prompt = f"""Analyze this advertisement image for visual and textual characteristics.

IMAGE METADATA:
- Resolution: {image_data.get('resolution', 'Unknown')}

Please analyze and return the following fields in JSON format:
{format_str}

ANALYSIS CRITERIA:
{criteria_str}

{image_prompt['instruction']}"""

    try:
        # Step 4: Send to Gemini with both image and prompt
        image_part = {
            "mime_type": "image/png",
            "data": image_b64
        }

        response = model.generate_content(
            [image_part, prompt],
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json"
            )
        )

        # Step 5: Parse response
        analysis_text = response.text.strip()
        if analysis_text.startswith('```json'):
            analysis_text = analysis_text.replace('```json', '').replace('```', '').strip()

        analysis = json.loads(analysis_text)

        # Return the structured analysis
        return {
            "product_visibility_score": analysis.get("product_visibility_score"),
            "visual_density": analysis.get("visual_density"),
            "color_palette": analysis.get("color_palette", []),
            "age_demographic": analysis.get("age_demographic"),
            "gender_demographic": analysis.get("gender_demographic"),
            "verbosity": analysis.get("verbosity"),
            "visual_complexity": analysis.get("visual_complexity"),
            "purchase_urgency": analysis.get("purchase_urgency"),
            "formality_level": analysis.get("formality_level"),
            "benefit_framing": analysis.get("benefit_framing"),
            "scene_setting": analysis.get("scene_setting"),
            "fear_index": analysis.get("fear_index"),
            "comfort_index": analysis.get("comfort_index"),
            "humor_index": analysis.get("humor_index"),
            "success_index": analysis.get("success_index"),
            "love_index": analysis.get("love_index"),
            "family_index": analysis.get("family_index"),
            "adventure_index": analysis.get("adventure_index"),
            "nostalgia_index": analysis.get("nostalgia_index"),
            "health_index": analysis.get("health_index"),
            "luxury_index": analysis.get("luxury_index"),
            "summary": analysis.get("summary")
        }

    except Exception as e:
        return {
            "error": f"Gemini API error: {str(e)}",
            "product_visibility_score": None,
            "visual_density": None,
            "color_palette": [],
            "age_demographic": None,
            "gender_demographic": None,
            "verbosity": None,
            "visual_complexity": None,
            "purchase_urgency": None,
            "formality_level": None,
            "benefit_framing": None,
            "scene_setting": None,
            "fear_index": None,
            "comfort_index": None,
            "humor_index": None,
            "success_index": None,
            "love_index": None,
            "family_index": None,
            "adventure_index": None,
            "nostalgia_index": None,
            "health_index": None,
            "luxury_index": None
        }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python image_analysis.py <image_path> [output_json_path]")
        print("\nThis script will:")
        print("  1. Extract image features (metadata + OCR)")
        print("  2. Analyze with Gemini 2.5 Flash")
        print("  3. Return structured analysis with visual and textual metrics")
        print("\nRequires:")
        print("  - GEMINI_API_KEY environment variable")
        sys.exit(1)

    image_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        # Load image
        print(f"Loading image: {image_path}")
        with Image.open(image_path) as img:
            # Analyze image
            print("Analyzing image with Gemini...")
            results = analyze_image_with_gemini(img)

        # Print results
        print("\n=== Analysis Results ===")
        print(json.dumps(results, indent=2))

        # Optionally save to JSON
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\nResults saved to: {output_path}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
