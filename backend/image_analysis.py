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
        - demographic_cues: Dict with age_band, hairstyle_archetype, presence_of_kids, presence_of_elders
        - activity: "sedentary" or "dynamic"
        - call_to_action_level: 1-3 (based on OCR)
        - formality_level: 1-4 (based on OCR)
        - benefit_framing: "outcome", "feature", or "social_proof"
        - temporal_urgency_intensity: 1-3
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

    # Step 3: Create the analysis prompt
    ocr_text = image_data.get('text', 'No text detected')
    ocr_details = image_data.get('ocr_details', {})
    text_elements = ocr_details.get('text_elements', [])

    # Format text elements for context
    prominent_texts = []
    for elem in text_elements[:10]:  # Top 10 most prominent text elements
        prominent_texts.append({
            'text': elem['text'],
            'prominence_score': elem['prominence_score']
        })

    prompt = f"""Analyze this advertisement image for visual and textual characteristics.

IMAGE METADATA:
- Resolution: {image_data.get('resolution', 'Unknown')}
- Extracted Text (OCR): "{ocr_text}"
- Prominent Text Elements: {json.dumps(prominent_texts, indent=2)}

Please analyze and return the following fields in JSON format:

{{
    "product_visibility_score": "Low" | "Medium" | "High",
    "negative_space_ratio": "Low" | "Medium" | "High",
    "color_palette": ["#RRGGBB", "#RRGGBB", ...],
    "demographic_cues": {{
        "age_band": "child (0-12)" | "teenage (13-19)" | "adult (20-64)" | "senior (65+)" | null,
        "hairstyle_archetype": "description" | null,
        "presence_of_kids": true | false,
        "presence_of_elders": true | false
    }},
    "activity": "sedentary" | "dynamic",
    "call_to_action_level": 1 | 2 | 3,
    "formality_level": 1 | 2 | 3 | 4,
    "benefit_framing": "outcome" | "feature" | "social_proof",
    "temporal_urgency_intensity": 1 | 2 | 3
}}

ANALYSIS CRITERIA:

1. **product_visibility_score**: How prominently the product appears in the image
   - "Low": Product barely visible or only mentioned in text
   - "Medium": Product appears but not dominant focus
   - "High": Product is prominently featured and clearly visible

2. **negative_space_ratio**: Proportion of empty/negative space in the image
   - "Low": Image is crowded with minimal empty space (high visual density)
   - "Medium": Balanced mix of content and negative space
   - "High": Lots of empty space, minimalist design (low visual density)

3. **color_palette**: Extract up to 5 most significant/recurring hex colors in the image
   - Order from most to least significant
   - Use uppercase format: #RRGGBB
   - Must be EXACTLY 5 colors (or fewer if image is very simple)

4. **demographic_cues**: Analyze human presence (if any)
   - age_band: Age range of MAJORITY of people visible (null if no humans)
   - hairstyle_archetype: Describe predominant hairstyle if humans present (e.g., "long wavy", "short professional", "bald", "curly afro") (null if no humans)
   - presence_of_kids: true if children (0-12) are visible
   - presence_of_elders: true if elderly people (65+) are visible
   - IMPORTANT: If NO humans are present in the image, all fields should be null/false

5. **activity**: Visual dynamism level
   - "sedentary": Static, calm, peaceful imagery (people sitting, standing still, minimal motion)
   - "dynamic": Active, energetic imagery (people moving, sports, action, motion blur)

6. **call_to_action_level** (based on OCR text):
   - 1: Not urgent - No clear CTA or very soft CTA ("Learn more", "Discover")
   - 2: Semi-urgent - Moderate CTA ("Shop now", "Get started", "Try it")
   - 3: Urgent - Strong immediate CTA ("Buy now", "Limited time", "Act now", "Don't miss out")

7. **formality_level** (based on OCR text and visual style):
   - 1: Meme speak - Internet slang, all caps, emojis, casual abbreviations
   - 2: Casual - Conversational, friendly, informal tone
   - 3: Semi-professional - Polished but approachable
   - 4: Professional - Formal, corporate, business language

8. **benefit_framing** (based on OCR text):
   - "outcome": Focuses on results/benefits user will achieve ("Get fit", "Save money", "Feel confident")
   - "feature": Focuses on product attributes ("Made with X", "Features Y", "Includes Z")
   - "social_proof": Focuses on testimonials, reviews, popularity ("1M+ users", "5-star rated", "Trusted by...")

9. **temporal_urgency_intensity** (based on OCR text):
   - 1: Longer than week or no urgency - No time pressure or general timeline
   - 2: Within week - "This week", "7 days", weekly timeline
   - 3: Within day - "Today only", "24 hours", "Ends tonight", immediate urgency

Analyze the image objectively based on what you see and the extracted text. Return ONLY valid JSON.
"""

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
            "negative_space_ratio": analysis.get("negative_space_ratio"),
            "color_palette": analysis.get("color_palette", []),
            "demographic_cues": analysis.get("demographic_cues", {
                "age_band": None,
                "hairstyle_archetype": None,
                "presence_of_kids": False,
                "presence_of_elders": False
            }),
            "activity": analysis.get("activity"),
            "call_to_action_level": analysis.get("call_to_action_level"),
            "formality_level": analysis.get("formality_level"),
            "benefit_framing": analysis.get("benefit_framing"),
            "temporal_urgency_intensity": analysis.get("temporal_urgency_intensity")
        }

    except Exception as e:
        return {
            "error": f"Gemini API error: {str(e)}",
            "product_visibility_score": None,
            "negative_space_ratio": None,
            "color_palette": [],
            "demographic_cues": {
                "age_band": None,
                "hairstyle_archetype": None,
                "presence_of_kids": False,
                "presence_of_elders": False
            },
            "activity": None,
            "call_to_action_level": None,
            "formality_level": None,
            "benefit_framing": None,
            "temporal_urgency_intensity": None
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
