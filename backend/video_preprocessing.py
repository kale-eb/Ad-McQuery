import json
import os
from typing import Dict, List, Any
import cv2
from openai import OpenAI
from pathlib import Path
import tempfile
import subprocess
import math
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def extract_video_metadata(video_path: str) -> Dict[str, Any]:
    """
    Extract resolution, aspect ratio, and length from video file.
    """
    cap = cv2.VideoCapture(video_path)
    
    try:
        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Calculate length in seconds
        length_seconds = frame_count / fps if fps > 0 else 0
        
        # Calculate aspect ratio
        gcd = math.gcd(width, height)
        aspect_ratio = f"{width//gcd}:{height//gcd}"
        
        return {
            "resolution": f"{width}x{height}",
            "aspect_ratio": aspect_ratio,
            "length": round(length_seconds, 2)
        }
    finally:
        cap.release()


def extract_audio_from_video(video_path: str, output_audio_path: str) -> bool:
    """
    Extract audio from video file using ffmpeg.
    """
    try:
        command = [
            'ffmpeg',
            '-i', video_path,
            '-vn',  # No video
            '-acodec', 'pcm_s16le',  # PCM 16-bit
            '-ar', '16000',  # 16kHz sampling rate (Whisper works well with this)
            '-ac', '1',  # Mono
            '-y',  # Overwrite output file
            output_audio_path
        ]
        
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error extracting audio: {e}")
        return False
    except FileNotFoundError:
        print("ffmpeg not found. Please install ffmpeg.")
        return False


def transcribe_with_whisper(audio_path: str) -> Dict[str, Any]:
    """
    Transcribe audio using OpenAI Whisper API - much faster than local model.
    Requires OPENAI_API_KEY environment variable.
    """
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    with open(audio_path, "rb") as audio_file:
        # Get transcription with timestamps
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="verbose_json",
            timestamp_granularities=["word", "segment"]
        )
    
    # Format transcript with word-level timestamps
    whisper_transcript = {
        "full_text": response.text.strip(),
        "segments": [],
        "words": []
    }
    
    # Process segments
    for segment in response.segments:
        segment_data = {
            "start": round(segment.start, 2),
            "end": round(segment.end, 2),
            "text": segment.text.strip()
        }
        whisper_transcript["segments"].append(segment_data)
    
    # Process words if available
    if hasattr(response, 'words') and response.words:
        for word in response.words:
            word_data = {
                "word": word.word.strip(),
                "start": round(word.start, 2),
                "end": round(word.end, 2)
            }
            whisper_transcript["words"].append(word_data)
    
    return whisper_transcript


def preprocess_video(video_path: str) -> Dict[str, Any]:
    """
    Main preprocessing function that takes a video file and returns JSON with metadata and transcript.
    
    Args:
        video_path: Path to the video file
    
    Returns:
        Dictionary containing resolution, aspect_ratio, length, and whisper_transcript
    """
    # Validate video file exists
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    print(f"Processing video: {video_path}")
    
    # Extract video metadata
    print("Extracting video metadata...")
    metadata = extract_video_metadata(video_path)
    
    # Create temporary audio file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
        temp_audio_path = temp_audio.name
    
    try:
        # Extract audio from video
        print("Extracting audio from video...")
        if not extract_audio_from_video(video_path, temp_audio_path):
            raise Exception("Failed to extract audio from video")
        
        # Transcribe audio with Whisper API
        print("Transcribing audio with Whisper API...")
        whisper_transcript = transcribe_with_whisper(temp_audio_path)
        
        # Combine all data
        result = {
            "resolution": metadata["resolution"],
            "aspect_ratio": metadata["aspect_ratio"],
            "length": metadata["length"],
            "whisper_transcript": whisper_transcript
        }
        
        return result
    
    finally:
        # Clean up temporary audio file
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)


def save_results_to_json(results: Dict[str, Any], output_path: str):
    """
    Save preprocessing results to JSON file.
    """
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python video_preprocessing.py <video_path> [output_json_path]")
        print("Requires: OPENAI_API_KEY environment variable")
        print("\nExample usage in Python:")
        print("  from video_preprocessing import preprocess_video")
        print("  result = preprocess_video('/path/to/video.mp4')")
        sys.exit(1)
    
    video_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Check for API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    
    try:
        # Process video
        results = preprocess_video(video_path)
        
        # Optionally save to JSON if output path provided
        if output_path:
            save_results_to_json(results, output_path)
        
        # Print summary and return data
        print("\n=== Preprocessing Complete ===")
        print(f"Resolution: {results['resolution']}")
        print(f"Aspect Ratio: {results['aspect_ratio']}")
        print(f"Length: {results['length']} seconds")
        print(f"Transcript words: {len(results['whisper_transcript']['words'])}")
        print("\nReturned dictionary with keys: resolution, aspect_ratio, length, whisper_transcript")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)