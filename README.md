# Video Creation Tool

# README

This script is used to generate subtitles and overlay them onto a video clip using the Speechmatics API and the ffmpeg command-line tool.

# Prerequisites

Before running this script, you need to have the following installed on your system:

# Python 3.6 or higher

The speechmatics and httpx Python packages (you can install them using pip)
The ffmpeg command-line tool
You also need to have a Speechmatics API key, which you can obtain from the Speechmatics website.

# Usage

Set the API_KEY, PATH_TO_FILE, and LANGUAGE variables at the top of the script to the appropriate values for your use case.

Run the script using the following command:

'''
python generate_subtitles.py
'''

The script will submit a transcription job to the Speechmatics API and wait for the results. Once the results are available, it will generate an SRT file containing the subtitles and overlay them onto the video clip using ffmpeg. The output video file will be named output.mp4.
