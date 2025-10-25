"""
Test script for image_preprocess.py
"""
from PIL import Image
import sys
import os
import json

# Add parent directory to path to import image_preprocess
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from image_preprocess import extract_image_features


def test_extract_image_features():
    """Test the extract_image_features function with a sample PNG image."""

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
    print("\nExtracting image features...")
    result = extract_image_features(img)

    # Display results
    print("\n" + "="*60)
    print("METADATA:")
    print("="*60)
    for key, value in result['metadata'].items():
        print(f"  {key}: {value}")

    print("\n" + "="*60)
    print("CONTRAST ANALYSIS:")
    print("="*60)
    contrast = result['contrast']
    for key, value in contrast.items():
        if key != 'histogram':  # Skip histogram data for readability
            print(f"  {key}: {value}")

    print("\n" + "="*60)
    print("OCR RESULTS:")
    print("="*60)
    ocr = result['ocr']
    print(f"  Number of text elements: {ocr['num_elements']}")
    print(f"  Most prominent text: {ocr['most_prominent_text']}")
    print(f"  Most prominent score: {ocr['most_prominent_score']:.4f}")

    print(f"\n  Full extracted text:")
    print(f"  {'-'*58}")
    if ocr['full_text']:
        for line in ocr['full_text'].split('\n'):
            print(f"  {line}")
    else:
        print("  (No text detected)")

    if ocr['text_elements']:
        print(f"\n  Top 5 text elements by prominence:")
        print(f"  {'-'*58}")
        for i, elem in enumerate(ocr['text_elements'][:5], 1):
            print(f"  {i}. '{elem['text']}' (score: {elem['prominence_score']:.4f}, confidence: {elem['confidence']:.1f}%)")

    print("\n" + "="*60)
    print("TEST COMPLETED SUCCESSFULLY")
    print("="*60)

    # Optionally save full results to JSON
    output_file = os.path.join(os.path.dirname(__file__), 'test_results.json')
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\nFull results saved")


if __name__ == "__main__":
    test_extract_image_features()
