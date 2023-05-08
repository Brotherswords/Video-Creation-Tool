import re
import APIKey
import requests
import argparse
import requests
from PIL import Image
from pydub import AudioSegment
from google.cloud import vision
from io import BytesIO

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


def generate_image(keyword):
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


def save_image(keyword, filename):
    # generate the image using the generate_image function
    image = generate_image(keyword)

    # save the image to a file
    with open(filename, 'wb') as f:
        image.save(f)


if __name__ == '__main__':
    keywords = extract_keywords_from_srt(PATH_TO_FILE)
    print(keywords)
    save_image(keywords[0], keywords[0] + '.jpg')
