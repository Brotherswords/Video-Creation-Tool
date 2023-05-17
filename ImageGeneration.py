import re
import APIKey
import requests
import argparse
from PIL import Image
from io import BytesIO
import subprocess

from typing import List, Tuple


# Obtain Path from command line arguments and parse it
parser = argparse.ArgumentParser(
    description='Generate subtitles and overlay them on a video file')
parser.add_argument('file', help='path to the srt file')
args = parser.parse_args()

PATH_TO_FILE = args.file


def extract_keywords_from_srt(srt_file_path: str) -> List[Tuple[str, str]]:
    """
    Extracts the keywords from the srt file and stores the timestamp of the earliest word in each set of 5 keywords.

    :param srt_file_path: The path to the srt file.
    :return: A list of tuples, where each tuple contains a set of 5 keywords and the timestamp of the earliest word in the set.
    """
    with open(srt_file_path, 'r') as srt_file:

        # Extract the keywords from the srt file
        srt_content = srt_file.read()
        regex_pattern = r"\d+\n(\d{2}:\d{2}:\d{2},\d{3}) --> \d{2}:\d{2}:\d{2},\d{3}\n(.+)"
        matches = re.findall(regex_pattern, srt_content)
        timestamps = [match[0] for match in matches]
        keywords = [re.findall(r'\w+', match[1])[0] for match in matches]
        common_words = ['a', 'about', 'all', 'also', 'an', 'and', 'as', 'at', 'be', 'because', 'but', 'by', 'can', 'come', 'could', 'day', 'do', 'even', 'find', 'first', 'for', 'from', 'get', 'give', 'go', 'have', 'he', 'her', 'here', 'him', 'his', 'how', 'i', 'if', 'in', 'into', 'it', 'its', 'just', 'know', 'like', 'look', 'make', 'man', 'many', 'me', 'more', 'my', 'new', 'no', 'not',
                        'now', 'of', 'on', 'one', 'only', 'or', 'other', 'our', 'out', 'people', 'say', 'see', 'she', 'so', 'some', 'take', 'tell', 'than', 'that', 'the', 'their', 'them', 'then', 'there', 'these', 'they', 'thing', 'think', 'this', 'those', 'time', 'to', 'two', 'up', 'use', 'very', 'want', 'way', 'we', 'well', 'what', 'when', 'which', 'who', 'will', 'with', 'would', 'year', 'you', 'your']

        # Remove common words from the list of keywords
        key_words_without_common_words = [
            word for word in keywords if word.lower() not in common_words]

        # Concatenate every 5 strings in the list to form a single string -> Used as queries for DALLE-2
        key_words_without_common_words = [' '.join(
            key_words_without_common_words[i:i+5]) for i in range(0, len(key_words_without_common_words), 5)]

        # Create a list of tuples, where each tuple contains a set of 5 keywords and the timestamp of the earliest word in the set
        keywords_with_timestamps = list(
            zip(key_words_without_common_words, timestamps[::5]))

        return keywords_with_timestamps


def generate_image(keyword: str) -> Image:
    """
    Generates an image using the DALLE-2 API using keywords generated from extract_keywords_from_srt
    @param keyword: The keyword to generate an image of
    @return: The generated image
    NOTE: This function costs approximately 0.02 USD per call. Use sparingly.
    """

    api_key = APIKey.OPENAI_API_KEY
    url = f'https://api.openai.com/v1/images/generations'
    prompt = f'Generate an image of a {keyword}'
    data = {
        'model': 'image-alpha-001',
        'prompt': prompt,
    }
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    response = requests.post(url, json=data, headers=headers)
    response_json = response.json()
    image_url = response_json['data'][0]['url']
    image_data = requests.get(image_url).content
    image = Image.open(BytesIO(image_data))
    return image


def save_image(keyword: str, filename: str) -> None:
    """
    Saves the generated image to a file: filename
    @param keyword: The keyword to generate an image of
    @param filename: The name of the file to save the image to
    @return: None
    """
    # generate the image using the generate_image function
    image = generate_image(keyword)

    # save the image to a file
    with open(filename, 'wb') as f:
        image.save(f)


def filter_keywords_by_timestamp(keywords_with_timestamps: List[Tuple[str, str]], separation_time: int) -> List[Tuple[str, str]]:
    """
    Filters a list of keyword-timestamp tuples such that keywords are spaced at least separation_time seconds apart.

    :param keywords_with_timestamps: A list of keyword-timestamp tuples.
    :return: A filtered list of keyword-timestamp tuples.
    """
    filtered_keywords_with_timestamps = [
        keywords_with_timestamps[0]]  # Always include the first keyword in the list
    for i in range(1, len(keywords_with_timestamps)):
        current_timestamp = keywords_with_timestamps[i][1]
        previous_timestamp = filtered_keywords_with_timestamps[-1][1]
        if (convert_timestamp_to_seconds(current_timestamp) - convert_timestamp_to_seconds(previous_timestamp)) >= separation_time:
            filtered_keywords_with_timestamps.append(
                keywords_with_timestamps[i])
    return filtered_keywords_with_timestamps


def convert_timestamp_to_seconds(timestamp: str) -> int:
    """
    Converts a timestamp string in the format "HH:MM:SS,MMM" to the number of seconds since the start of the video.

    :param timestamp: A string representing a timestamp in the format "HH:MM:SS,MMM".
    :return: An integer representing the number of seconds since the start of the video.
    """
    parts = timestamp.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds, milliseconds = parts[2].split(',')
    seconds = int(seconds)
    milliseconds = int(milliseconds)
    return ((hours * 60 + minutes) * 60 + seconds) + (milliseconds // 1000)


# def Overlay_Images_With_AI(duration: int, input_file: str, output_file: str, keywords: List[Tuple[str, str]]) -> None:
#     ffmpeg_cmd = ""
#     ffmpeg_imgStr = ''
#     ffmpeg_imgStrTemp = ''
#     with open('image_list.txt', 'w') as f:
#         f.write('')

# # ffmpeg -i output.mp4 -f concat -safe 0 -i image_list.txt -filter_complex "[1:v]overlay=x=100:y=100:enable='between(t,2,12)'[overlay1];[overlay1][2:v]overlay=x=100:y=100:enable='between(t,12,22)'" -codec:a copy outputOverlay.mp4

#     with open('image_list.txt', 'w') as f:
#         for keyword, time in keywords:
#             ffmpeg_imgStrTemp = ffmpeg_imgStr
#             try:
#                 keyword_without_spaces = keyword.replace(
#                     " ", "").replace("\t", "").replace("\n", "")
#                 start_time = convert_timestamp_to_seconds(time)
#                 end_time = start_time + duration
#                 ffmpeg_imgStr += f'[0:v][{keyword_without_spaces}.jpg]overlay=x=100:y=100:enable=\'between(t,{start_time},{end_time})\';'
#                 f.write(f"file '{keyword_without_spaces}.jpg'\n")
#                 # save_image(keyword_without_spaces,
#                 #    keyword_without_spaces+'.jpg')
#             except Exception as e:
#                 print(e, "ignoring keyword: ", keyword)
#                 ffmpeg_imgStr = ffmpeg_imgStrTemp

#     ffmpeg_cmd = f'ffmpeg -i {input_file} -f concat -safe 0 -i image_list.txt -filter_complex "{ffmpeg_imgStr}" -codec:a copy {output_file}'
#     print(ffmpeg_cmd)
#     subprocess.run(ffmpeg_cmd, shell=True)


def Overlay_Images_With_AI(duration: int, input_file: str, output_file: str, keywords: List[Tuple[str, str]]) -> None:
    filter_complex = ""
    ffmpeg_cmd = ['ffmpeg', '-y', '-i', input_file]

    for i, (keyword, time) in enumerate(keywords):
        keyword_without_spaces = keyword.replace(
            " ", "").replace("\t", "").replace("\n", "")
        save_image(keyword_without_spaces, keyword_without_spaces + '.jpg')
        start_time = convert_timestamp_to_seconds(time)
        end_time = start_time + duration
        ffmpeg_cmd.extend(['-i', f'{keyword_without_spaces}.jpg'])

        if i > 0:
            filter_complex += f"[tmp{i-1}][{i+1}:v] "
        else:
            filter_complex += f"[0:v][{i+1}:v] "

        if i == len(keywords) - 1:  # If it is the last keyword, do not add a label to the output
            filter_complex += f"overlay=x=50:y=50:enable='between(t,{start_time},{end_time})' "
        else:
            filter_complex += f"overlay=x=50:y=50:enable='between(t,{start_time},{end_time})' [tmp{i}]; "

    ffmpeg_cmd.extend(['-filter_complex', filter_complex,
                      '-codec:a', 'copy', output_file])

    print(' '.join(ffmpeg_cmd))
    subprocess.run(ffmpeg_cmd)


if __name__ == '__main__':
    duration: int = 4
    keywords = extract_keywords_from_srt(PATH_TO_FILE)
    print(keywords)
    keywords = filter_keywords_by_timestamp(keywords, duration)
    print(keywords)
    Overlay_Images_With_AI(duration//2, 'outputSubtitles.mp4',
                           'outputOverlay.mp4', keywords)
