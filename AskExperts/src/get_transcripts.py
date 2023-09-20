import os
import json
import requests
import html
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter

YT_API_KEY= 'AIzaSyA9sXtIOtIn7qM-wYIZRcEPTrm0Ba-AAzk'
CHANNEL_IDS = {'Huberman': 'UC2D2CMWXMOVWx7giW1n3LIg', 'AIExplained': 'UCNJ1Ymd5yFuUPtn21xtRbbw', 'AthleanX':'UCe0TLA0EsQbE-MjuHXevj2A', 'PeterAttia': 'UC8kGsMa0LygSX9nkBcBH1Sg', 'LexFridman': 'UCSHZKyawb77ixDdsGog4iWA', 'kurzgesagt': 'UCsXVk37bltHxD1rDPwtNM8Q'}
base_search_url = 'https://www.googleapis.com/youtube/v3/search'

def fetch_video_data(channel_id):
    video_datas = []
    next_page_token = None

    while True:
        search_params = {
            'key': YT_API_KEY,
            'channelId': channel_id,
            'part': 'id,snippet',
            'order': 'date',
            'maxResults': 1000,
            'pageToken': next_page_token
        }

        response = requests.get(base_search_url, params=search_params).json()
        for item in response['items']:
            if 'videoId' in item['id']:
                video_datas.append({
                    'videoId': item['id']['videoId'],
                    'title': html.unescape(item['snippet']['title'])
                })

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    return video_datas

# ... [Your functions: seconds_to_hms and regroup_data]
def seconds_to_hms(seconds):
    """Convert seconds to hours, minutes, and seconds."""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

def regroup_data(data):
    grouped_data = []
    group = []
    total_duration = 0
    merged_text = ""

    for item in data:
        if len(group) < 50:
            merged_text += item['text'] + " "
            total_duration += item['duration']
            group.append(item)
        else:
            text=merged_text.strip()
            clean_text=text.replace('\n',' ')
            grouped_data.append({
                'text': clean_text,
                'start': seconds_to_hms(group[0]['start']),
                'duration': total_duration,
                'title': html.unescape(video_data['title']),
            })
            group = [item]
            merged_text = item['text'] + " "
            total_duration = item['duration']

    if group:  # Add any remaining items
        text=merged_text.strip()
        clean_text=text.replace('\n',' ')
        grouped_data.append({
            'text': clean_text,
            'start': seconds_to_hms(group[0]['start']),
            'duration': total_duration,
            'title': html.unescape(video_data['title']),
        })

    return grouped_data

for channel_name, channel_id in CHANNEL_IDS.items():
    video_datas = fetch_video_data(channel_id)

    # Create a directory for the channel if it doesn't exist
    channel_directory = os.path.join(os.getcwd(), '..', 'transcripts', f"{channel_name}Transcripts")
    if not os.path.exists(channel_directory):
        os.makedirs(channel_directory)

    for video_data in video_datas:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_data['videoId'])
            
            # Regroup the transcript data
            grouped_transcript = regroup_data(transcript)
            
            # Prettify the JSON
            pretty_json = json.dumps(grouped_transcript, indent=4, ensure_ascii=False)
            
            # Define the path for the transcript file
            transcript_file_path = os.path.join(channel_directory, f"{video_data['title']}.json")
            
            if not os.path.exists(transcript_file_path):
                # Write the prettified transcript to the file
                with open(transcript_file_path, 'w', encoding='utf-8') as json_file:
                    json_file.write(pretty_json)
            else:
                print(f"File for video ID {video_data['videoId']} already exists. Skipping...")
        except:
            print(f"No transcript available for video ID: {video_data['videoId']}")
