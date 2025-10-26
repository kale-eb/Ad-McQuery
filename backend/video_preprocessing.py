import json
import os
import subprocess
from typing import Dict, List, Any
import cv2
import math
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def extract_video_metadata(video_path: str) -> Dict[str, Any]:
    """
    Extract resolution, aspect ratio, length, video bitrate, and audio bitrate from video file.
    """
    cap = cv2.VideoCapture(video_path)
    
    try:
        # Get basic video properties from OpenCV
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Calculate length in seconds
        length_seconds = frame_count / fps if fps > 0 else 0
        
        # Calculate aspect ratio
        gcd = math.gcd(width, height)
        aspect_ratio = f"{width//gcd}:{height//gcd}"
        
        # Get bitrate information using ffprobe
        video_bitrate, audio_bitrate = extract_bitrates(video_path)
        
        return {
            "resolution": f"{width}x{height}",
            "aspect_ratio": aspect_ratio,
            "length": round(length_seconds, 2),
            "video_bitrate_kbps": video_bitrate,
            "audio_bitrate_kbps": audio_bitrate
        }
    finally:
        cap.release()


def extract_bitrates(video_path: str) -> tuple[int, int]:
    """
    Extract video and audio bitrates using ffprobe.
    
    Returns:
        Tuple of (video_bitrate_kbps, audio_bitrate_kbps)
        Returns None for values that cannot be determined
    """
    try:
        # Run ffprobe to get stream information
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json', 
            '-show_streams', video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Warning: ffprobe failed for {video_path}")
            return None, None
        
        probe_data = json.loads(result.stdout)
        streams = probe_data.get('streams', [])
        
        video_bitrate = None
        audio_bitrate = None
        
        for stream in streams:
            codec_type = stream.get('codec_type')
            bit_rate = stream.get('bit_rate')
            
            if bit_rate and bit_rate != 'N/A':
                bitrate_kbps = int(int(bit_rate) / 1000)  # Convert bps to kbps
                
                if codec_type == 'video' and video_bitrate is None:
                    video_bitrate = bitrate_kbps
                elif codec_type == 'audio' and audio_bitrate is None:
                    audio_bitrate = bitrate_kbps
        
        return video_bitrate, audio_bitrate
        
    except Exception as e:
        print(f"Warning: Could not extract bitrates from {video_path}: {e}")
        return None, None




def preprocess_video(video_path: str) -> Dict[str, Any]:
    """
    Main preprocessing function that takes a video file and returns JSON with metadata only.
    
    Args:
        video_path: Path to the video file
    
    Returns:
        Dictionary containing resolution, aspect_ratio, and length
    """
    # Validate video file exists
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    print(f"Processing video: {video_path}")
    
    # Extract video metadata
    print("Extracting video metadata...")
    metadata = extract_video_metadata(video_path)
    
    return metadata


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
        print("\nExample usage in Python:")
        print("  from video_preprocessing import preprocess_video")
        print("  result = preprocess_video('/path/to/video.mp4')")
        sys.exit(1)
    
    video_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
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
        print(f"Video Bitrate: {results['video_bitrate_kbps']} kbps" if results['video_bitrate_kbps'] else "Video Bitrate: N/A")
        print(f"Audio Bitrate: {results['audio_bitrate_kbps']} kbps" if results['audio_bitrate_kbps'] else "Audio Bitrate: N/A")
        print("\nReturned dictionary with keys: resolution, aspect_ratio, length, video_bitrate_kbps, audio_bitrate_kbps")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)