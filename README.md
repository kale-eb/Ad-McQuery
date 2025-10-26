# Ad-McQuery

Get your ads to your audience quicker, faster, smarter.

## How to run:
1. Install Python packages: `pip install -r requirements.txt`
2. Install npm packages: `cd frontend && npm i`
3. Run backend server with `python api.py`
4. Run frontend website with `cd frontend && npm run dev`
5. Go to http://localhost:5173
6. Upload a zip file that includes image and video ads.

> Note: The only zip file tested is the one given by AppLovin. The format in this zip file was 
>```
>ads
> ├── images
> │   └── image.png
> └── videos
>     └── videos.mp4
>```
> Other zip file structures may not be processed correctly.

## Video and Image metrics and criteria

- The image analysis criteria can be found [here](backend/ImageAnalysisCriteria.md)
- The video analysis criteria can be found [here](backend/VideoAnalysisCriteria.md)