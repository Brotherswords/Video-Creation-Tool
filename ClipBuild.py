
'''
This file is used to build the final clip with the subtitles overlayed on top of the video clip.
'''
import sys
import pysrt
import io
import os
from google.cloud import speech_v1p1beta1 as speech
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.io.VideoFileClip import VideoFileClip

clip_path = "/Users/lavan/Desktop/Python Things hissssss/Video-Creation-Tool/Video-Creation-Tool/ValorantClip.mp4"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/lavan/Downloads/Dont Delete/APIKeys/GCPSpeechToText/video-creation-tool-de8442b66120.json"

video = VideoFileClip(clip_path)
audio = video.audio
if audio is None:
    print("Error: The video does not have an audio track.")
    sys.exit(1)
print("Audio track found - transcribing audio...")
def transcribe_audio(video):
    client = speech.SpeechClient()

    # The language of the video's audio
    language_code = "en-US"

    # The encoding of the video's audio
    audio_encoding = speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED

    filename, ext = os.path.splitext(video.audio.filename)
    if ext == ".aac":
        audio_encoding = speech.RecognitionConfig.AudioEncoding.AAC
    else:
        audio_encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16

    config = speech.RecognitionConfig(
        encoding=audio_encoding,
        sample_rate_hertz=video.audio.fps,
        language_code=language_code,
        enable_word_time_offsets=True,
    )

    # Set up the audio stream for the video
    audio = video.audio.to_soundarray()

    # Call the Google Cloud Speech-to-Text API to transcribe the audio
    def audio_chunks(audio, chunk_size=16000):
        audio_bytes = audio.tobytes()
        for i in range(0, len(audio_bytes), chunk_size):
            yield audio_bytes[i:i + chunk_size]

    # Update the requests variable to use the generator function
    requests = (
        speech.StreamingRecognizeRequest(audio_content=chunk)
        for chunk in audio_chunks(audio)
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=False,
    )

    responses = client.streaming_recognize(requests=requests, config=streaming_config)

    # Parse the transcript and create a subtitle file
    subs = pysrt.SubRipFile()
    subs_idx = 1
    current_phrase = ""
    start_time = 0
    end_time = 0
    for response in responses:
        for result in response.results:
            if not result.is_final:
                continue

            for i, word in enumerate(result.alternatives[0].words):
                if i == 0:
                    start_time = int(word.start_time.seconds * 1000 + word.start_time.nanos / 1000000)
                current_phrase += " " + word.word
                end_time = int(word.end_time.seconds * 1000 + word.end_time.nanos / 1000000)

            subs.append(pysrt.SubRipItem(index=subs_idx, start=pysrt.SubRipTime(milliseconds=start_time), end=pysrt.SubRipTime(milliseconds=end_time), text=current_phrase.strip()))
            subs_idx += 1
            current_phrase = ""

    return subs


subs = transcribe_audio(video)

print("Transcription complete - saving subtitles...")
subs.save("subtitles.srt", encoding="utf-8")
print("Subtitles saved - overlaying subtitles on video...")
# Load your video file and extract the audio track
video = VideoFileClip(clip_path)
audio = video.audio

# Parse the subtitle file using pysrt and extract the subtitle entries
subtitle_file = pysrt.open("subtitles.srt")
subtitle_entries = []
for entry in subtitle_file:
    start_time = timedelta(milliseconds=entry.start.ordinal)
    end_time = timedelta(milliseconds=entry.end.ordinal)
    text = entry.text
    subtitle_entries.append(((start_time, end_time), text))

# Check if the subtitle_entries list is empty
if not subtitle_entries:
    print("Error: No subtitle entries found.")
    sys.exit(1)

# Create a SubtitlesClip object using the subtitle entries and the audio track
subtitles = SubtitlesClip(subtitle_entries, video.size)
subtitles = subtitles.set_audio(audio)

# Overlay the subtitles onto the video clip using the CompositeVideoClip method
final_clip = CompositeVideoClip([video, subtitles])
print("Subtitles overlayed - saving video...")

# Write the final clip to a file
final_clip.write_videofile("final_clip.mp4")
print("Video saved - done.")




