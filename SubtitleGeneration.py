
'''
This file is used to build the final clip with the subtitles overlayed on top of the video clip.
'''
import argparse
import json
import subprocess
import speechmatics as Speechmatics
import APIKey
from speechmatics.models import ConnectionSettings
from speechmatics.batch_client import BatchClient
from httpx import HTTPStatusError


# Parse command line arguments
parser = argparse.ArgumentParser(description='Generate subtitles and overlay them on a video file')
parser.add_argument('file', help='path to the video file')
args = parser.parse_args()

# Set variables
PATH_TO_FILE = args.file
LANGUAGE = "en"
json_data = None

# Use the Speechmatics API key in Speechmatics.APIKey
settings = ConnectionSettings(
    url="https://asr.api.speechmatics.com/v2",
    auth_token=APIKey.API_KEY,
)

# Define transcription parameters
conf = {
    "type": "transcription",
    "transcription_config": {
        "language": LANGUAGE
    }
}

# Open the client using a context manager
with BatchClient(settings) as client:
    try:
        job_id = client.submit_job(
            audio=PATH_TO_FILE,
            transcription_config=conf,
        )
        print(f'job {job_id} submitted successfully, waiting for transcript')

        #Get Transcript
        transcript = client.wait_for_completion(job_id, transcription_format='json-v2')
        print(transcript)

        # Parse the JSON response transcript into an SRT format to be stored in a file
        timestamps = []
        transcriptions = []
        for item in transcript['results']:
            if item['type'] == 'word':
                start_time = item['start_time']
                end_time = item['end_time']
                transcriptions.append(item['alternatives'][0]['content'])
                timestamps.append((start_time, end_time))

        # Generate the SRT file
        srt = ''
        for i in range(len(timestamps)):
            start = '{:02d}:{:02d}:{:02d},{:03d}'.format(
                int(timestamps[i][0])//3600, int(timestamps[i][0])//60%60,
                int(timestamps[i][0])%60, int((timestamps[i][0] - int(timestamps[i][0]))*1000))
            end = '{:02d}:{:02d}:{:02d},{:03d}'.format(
                int(timestamps[i][1])//3600, int(timestamps[i][1])//60%60,
                int(timestamps[i][1])%60, int((timestamps[i][1] - int(timestamps[i][1]))*1000))
            srt += f'{i+1}\n{start} --> {end}\n{transcriptions[i]}\n\n'

        with open('output.srt', 'w') as f:
            f.write(srt)

        # Overlay the SRT file onto the video
        subprocess.run(['ffmpeg', '-i', PATH_TO_FILE, '-vf', f'subtitles=output.srt', '-c:a', 'copy', 'output.mp4'])

    except HTTPStatusError as e:
        if e.response.status_code == 401:
            print('Invalid API key - Check your API_KEY at the top of the code!')
        elif e.response.status_code == 400:
            print(e.response.json()['detail'])
            json_data = e.response.json()
        else:
            raise e



# Parse the JSON response

