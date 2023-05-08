import argparse
from regex import re
from cv2 import cv2
import requests
from PIL import Image
from pydub import AudioSegment
from google.cloud import vision
from google.cloud.vision import types


parser = argparse.ArgumentParser(
    description='Generate subtitles and overlay them on a video file')
parser.add_argument('file', help='path to the video file')
args = parser.parse_args()

PATH_TO_FILE = args.file


def extract_keywords_from_srt(srt_file_path):
    with open(srt_file_path, 'r') as srt_file:
        srt_content = srt_file.read()
        regex_pattern = r"\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n(.+)"
        matches = re.findall(regex_pattern, srt_content)
        keywords = [re.findall(r'\w+', match)[0] for match in matches]
        common_words = ['a', 'about', 'all', 'also', 'an', 'and', 'as', 'at', 'be', 'because', 'but', 'by', 'can', 'come', 'could', 'day', 'do', 'even', 'find', 'first', 'for', 'from', 'get', 'give', 'go', 'have', 'he', 'her', 'here', 'him', 'his', 'how', 'i', 'if', 'in', 'into', 'it', 'its', 'just', 'know', 'like', 'look', 'make', 'man', 'many', 'me', 'more', 'my', 'new', 'no', 'not',
                        'now', 'of', 'on', 'one', 'only', 'or', 'other', 'our', 'out', 'people', 'say', 'see', 'she', 'so', 'some', 'take', 'tell', 'than', 'that', 'the', 'their', 'them', 'then', 'there', 'these', 'they', 'thing', 'think', 'this', 'those', 'time', 'to', 'two', 'up', 'use', 'very', 'want', 'way', 'we', 'well', 'what', 'when', 'which', 'who', 'will', 'with', 'would', 'year', 'you', 'your']

        key_words_without_common_words = [
            word for word in keywords if word.lower() not in common_words]
        return key_words_without_common_words


def main():
    print(extract_keywords_from_srt(PATH_TO_FILE))


if __name__ == '__main__':
    print(extract_keywords_from_srt(PATH_TO_FILE))
