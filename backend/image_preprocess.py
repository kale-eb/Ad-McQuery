from PIL import Image
import numpy as np
import cv2
import pytesseract
from typing import Dict, List, Any


def extract_image_features(image: Image.Image) -> Dict[str, Any]:
    """
    Extract comprehensive features from an image including metadata,
    histogram analysis, and OCR with prominence scoring.

    Args:
        image: PIL Image object

    Returns:
        Dictionary containing:
        - metadata: frames, resolution, format, mode, size
        - contrast: histogram data and contrast metrics
        - ocr: text detection with prominence scores
    """

    img = image
    img_array = np.array(img)


    metadata = {
        'width': img.width,
        'height': img.height,
        'resolution': (img.width, img.height),
        'format': img.format,
        'mode': img.mode,
        'file_size_bytes': img.fp.tell() if hasattr(img, 'fp') and img.fp else None,
    }

    # Checks for frames (GIF/animated images)
    try:
        n_frames = getattr(img, 'n_frames', 1)
        metadata['frames'] = n_frames
        metadata['is_animated'] = bool(n_frames > 1)
    except:
        metadata['frames'] = 1
        metadata['is_animated'] = False


    # Convert to grayscale for histogram
    if len(img_array.shape) == 3:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_array

    histogram = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()

    # Basic brightness metrics (removed complex contrast calculations)
    contrast_data = {
        'histogram': histogram.tolist(),
        'mean_brightness': float(gray.mean()),
        'min_brightness': float(gray.min()),
        'max_brightness': float(gray.max())
    }

    # Get detailed OCR data with bounding boxes
    ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

    text_elements = []
    for i in range(len(ocr_data['text'])):
        text = ocr_data['text'][i].strip()
        if text:  # Only non-empty text
            width = ocr_data['width'][i]
            height = ocr_data['height'][i]
            area = width * height

            # Prominence score based on size relative to image
            image_area = img.width * img.height
            relative_size = area / image_area

            # Confidence from OCR
            confidence = float(ocr_data['conf'][i])

            # Combined prominence score (size + confidence)
            prominence_score = (relative_size * 1000) * (confidence / 100)

            text_elements.append({
                'text': text,
                'confidence': confidence,
                'bbox': {
                    'x': ocr_data['left'][i],
                    'y': ocr_data['top'][i],
                    'width': width,
                    'height': height
                },
                'area': area,
                'relative_size': relative_size,
                'prominence_score': prominence_score
            })

    # Sort by prominence score (largest/most visible first)
    text_elements.sort(key=lambda x: x['prominence_score'], reverse=True)

    full_text = pytesseract.image_to_string(img).strip()

    ocr_result = {
        'full_text': full_text,
        'text_elements': text_elements,
        'num_elements': len(text_elements),
        'most_prominent_text': text_elements[0]['text'] if text_elements else None,
        'most_prominent_score': text_elements[0]['prominence_score'] if text_elements else 0
    }

    return {
        'metadata': metadata,
        'contrast': contrast_data,
        'ocr': ocr_result
    }
