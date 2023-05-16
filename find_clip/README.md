# README

In this module, we find a video clip that would make a good short video.

# Method 1: From Transcript

In [clip_from_transcript.ipynb](clip_from_transcript.ipynb), we get the transcript from a YouTube video with [youtube_transcript_api](https://github.com/jdepoix/youtube-transcript-api).
This transcript has a few words associated with timestamps.
We get an interesting video clip from GPT-4 (tested with Bing AI Chat "Precise") with the following steps:

1. Give GPT the transcript with timestamps and words.
2. Ask GPT to format the transcript as readable with good punctuation.
3. Ask GPT to find an interesting, funny, sad clip from the transcript.

Prompts that should be used are outputted to [prompts/](prompts/) after running [clip_from_transcript.ipynb](clip_from_transcript.ipynb).