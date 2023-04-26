
'''
This file is used to build the final clip with the subtitles overlayed on top of the video clip.
'''

# clip_path = "/Users/lavan/Desktop/Python Things hissssss/Video-Creation-Tool/Video-Creation-Tool/ValorantClip.mp4"

# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/lavan/Downloads/Dont Delete/APIKeys/GCPSpeechToText/video-creation-tool-de8442b66120.json"

import os
import subprocess
import io
import pysrt
from typing import List, Tuple
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from google.cloud import speech_v1p1beta1 as speech
from google.cloud.speech_v1p1beta1 import SpeechClient, RecognitionConfig, RecognitionAudio
from google.api_core.exceptions import InvalidArgument

def authenticate_google_cloud():
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/lavan/Downloads/Dont Delete/APIKeys/GCPSpeechToText/video-creation-tool-de8442b66120.json'

def extract_audio(video_file, audio_file):
    subprocess.run(['ffmpeg', '-i', video_file, '-vn', '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', audio_file])

def transcribe_audio_to_subtitles(video_file):
    authenticate_google_cloud()
    audio_file = 'extracted_audio.wav'
    extract_audio(video_file, audio_file)

    client = SpeechClient()

    with io.open(audio_file, 'rb') as audio_file:
        content = audio_file.read()

    audio = RecognitionAudio(content=content)
    config = RecognitionConfig(
        encoding=RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code='en-US',
        enable_automatic_punctuation=True,
        enable_word_time_offsets=True
    )

    try:
        response = client.recognize(config=config, audio=audio)
    except InvalidArgument:
        operation = client.long_running_recognize(config=config, audio=audio)
        response = operation.result()

    subtitles = []
    for result in response.results:
        for word_info in result.alternatives[0].words:
            word = word_info.word
            start_time = word_info.start_time.total_seconds()
            end_time = word_info.end_time.total_seconds()
            subtitles.append((word, start_time, end_time))

    return subtitles

def write_subtitles_to_srt(subtitles: List[Tuple[str, float, float]], output_file: str):
    with open(output_file, 'w', encoding='utf-8') as srt_file:
        index = 1
        for i, (word, start_time, end_time) in enumerate(subtitles):
            if i == 0 or subtitles[i-1][2] != start_time:
                srt_file.write(f"{index}\n")
                index += 1
                srt_file.write(f"{format_timestamp(start_time)} --> {format_timestamp(end_time)}\n")
            srt_file.write(f"{word} ")

            if i == len(subtitles) - 1 or subtitles[i+1][1] != end_time:
                srt_file.write("\n\n")

def format_timestamp(timestamp: float) -> str:
    hours, remainder = divmod(timestamp, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{seconds:06.3f}".replace('.', ',')

def srt_time_to_seconds(srt_time):
    return srt_time.hours * 3600 + srt_time.minutes * 60 + srt_time.seconds + srt_time.milliseconds / 1000.0

def add_subtitles_to_video(video_path, subtitles_path, output_path):
    # Load subtitles
    subs = pysrt.open(subtitles_path)
    
    # Load video
    video = VideoFileClip(video_path)
    
    # Iterate through subtitles and create TextClips for each subtitle
    subtitle_clips = []
    for sub in subs:
        start_time = srt_time_to_seconds(sub.start)
        end_time = srt_time_to_seconds(sub.end)
        duration = end_time - start_time

        txt_clip = TextClip(sub.text,
                            fontsize=24,
                            color='white',
                            bg_color='black',
                            transparent_bg=True,
                            size=video.size,
                            print_cmd=True).set_position(('center', 'bottom')).set_duration(duration).set_start(start_time)

        subtitle_clips.append(txt_clip)

    # Overlay subtitles on video
    final_clip = CompositeVideoClip([video] + subtitle_clips)
    
    # Write the output video file
    final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

video_file = 'ValorantClip.mp4'
subtitles = transcribe_audio_to_subtitles(video_file)

print(subtitles)

output_srt_file = 'subtitles.srt'
write_subtitles_to_srt(subtitles, output_srt_file)

add_subtitles_to_video(video_file, output_srt_file, 'output_path.mp4')




