# Subtitle Image Overlay

This script generates subtitles from an SRT file and overlays corresponding images on a video file. It utilizes the DALLE-2 API to generate images based on keywords extracted from the subtitles. The generated images are then overlaid on the video at specific timestamps.

# Usage

Run this function by doing ImageGeneration.py output.srt

# Functions

### extract_keywords_from_srt(srt_file_path: str) -> List[Tuple[str, str]]

- This function extracts keywords from the provided SRT file. It returns a list of tuples, where each tuple contains a set of 5 keywords and the timestamp of the earliest word in the set.

### generate_image(keyword: str) -> Image

- This function generates an image using the DALLE-2 API based on the provided keyword. It returns the generated image.

### Note: This function incurs a cost of approximately 0.02 USD per call to the API.

### save_image(keyword: str, filename: str) -> None

- This function saves the generated image to the specified filename.

### filter_keywords_by_timestamp(keywords_with_timestamps: List[Tuple[str, str]], separation_time: int) -> List[Tuple[str, str]]

- This function filters the list of keyword-timestamp tuples based on the specified minimum separation time (in seconds). It ensures that keywords are spaced at least separation_time seconds apart.

### convert_timestamp_to_seconds(timestamp: str) -> int

- This function converts a timestamp string in the format "HH:MM:SS,MMM" to the number of seconds since the start of the video.

### Overlay_Images_With_AI(duration: int, input_file: str, output_file: str, keywords: List[Tuple[str, str]]) -> None

- This function overlays images on the input video file based on the specified keywords and their corresponding timestamps. It generates images using the DALLE-2 API and saves them temporarily. The function then uses ffmpeg to overlay the images on the video file and save the output to the specified output file.

### Note: Ensure that ffmpeg is installed on your system and available in the command line.
