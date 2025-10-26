"""
Test script for image_analysis.py
"""
from PIL import Image
import sys
import os
import json

# Add parent directory to path to import image_analysis
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from image_analysis import analyze_image_with_gemini


def test_analyze_image_with_gemini():
    """Test the analyze_image_with_gemini function with i0006.png."""

    # Get the path to the test image
    test_image_path = os.path.join(os.path.dirname(__file__), 'i0006.png')

    # Check if image exists
    if not os.path.exists(test_image_path):
        print(f"Error: Test image not found at {test_image_path}")
        return

    print(f"Loading image from: {test_image_path}")

    # Load the image as PIL Image object
    img = Image.open(test_image_path)
    print(f"Image loaded successfully: {img.size} ({img.mode})")

    # Test the function
    print("\nAnalyzing image with Gemini...")
    print("(This may take a few seconds...)")
    result = analyze_image_with_gemini(img)

    # Display results
    print("\n" + "="*60)
    print("IMAGE ANALYSIS RESULTS")
    print("="*60)

    if "error" in result:
        print(f"\nERROR: {result['error']}")
        print("\nPartial results:")

    print("\n" + "-"*60)
    print("VISUAL CHARACTERISTICS")
    print("-"*60)
    print(f"  Product Visibility Score: {result.get('product_visibility_score')}")
    print(f"  Negative Space Ratio: {result.get('negative_space_ratio')}")
    print(f"  Activity Level: {result.get('activity')}")

    print("\n" + "-"*60)
    print("COLOR PALETTE")
    print("-"*60)
    color_palette = result.get('color_palette', [])
    if color_palette:
        for i, color in enumerate(color_palette, 1):
            print(f"  {i}. {color}")
    else:
        print("  (No colors extracted)")

    print("\n" + "-"*60)
    print("DEMOGRAPHIC CUES")
    print("-"*60)
    demographics = result.get('demographic_cues', {})
    print(f"  Age Band: {demographics.get('age_band', 'N/A')}")
    print(f"  Hairstyle Archetype: {demographics.get('hairstyle_archetype', 'N/A')}")
    print(f"  Presence of Kids: {demographics.get('presence_of_kids', False)}")
    print(f"  Presence of Elders: {demographics.get('presence_of_elders', False)}")

    print("\n" + "-"*60)
    print("TEXT-BASED METRICS (from OCR)")
    print("-"*60)
    print(f"  Call to Action Level: {result.get('call_to_action_level')}/3")
    print(f"    (1=not urgent, 2=semi urgent, 3=urgent)")
    print(f"  Formality Level: {result.get('formality_level')}/4")
    print(f"    (1=meme speak, 2=casual, 3=semi professional, 4=professional)")
    print(f"  Benefit Framing: {result.get('benefit_framing')}")
    print(f"    (outcome/feature/social_proof)")
    print(f"  Temporal Urgency Intensity: {result.get('temporal_urgency_intensity')}/3")
    print(f"    (1=longer than week, 2=within week, 3=within day)")

    print("\n" + "="*60)
    print("TEST COMPLETED SUCCESSFULLY")
    print("="*60)

    # Save full results to JSON
    output_file = os.path.join(os.path.dirname(__file__), 'test_image_analysis_results.json')
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\nFull results saved to: {output_file}")

    # Close the image
    img.close()

    return result


if __name__ == "__main__":
    try:
        test_analyze_image_with_gemini()
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
