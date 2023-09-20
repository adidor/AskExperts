import chromadb
import os
import json

CHANNEL_IDS = {'Huberman': 'UC2D2CMWXMOVWx7giW1n3LIg', 'AIExplained': 'UCNJ1Ymd5yFuUPtn21xtRbbw', 'AthleanX':'UCe0TLA0EsQbE-MjuHXevj2A', 'PeterAttia': 'UC8kGsMa0LygSX9nkBcBH1Sg', 'LexFridman': 'UCSHZKyawb77ixDdsGog4iWA', 'kurzgesagt': 'UCsXVk37bltHxD1rDPwtNM8Q'}


client = chromadb.PersistentClient(path=os.path.join(os.getcwd(), '..', 'chroma',))

global_id_counter = 0

for channel_name, channel_id in CHANNEL_IDS.items():
    # Create or get the collection for the current channel
    collection = client.create_collection(name=f"{channel_name}Transcripts")

    # Define the directory path for the current channel's transcripts
    channel_directory = os.path.join(os.getcwd(), '..', 'transcripts', f"{channel_name}Transcripts")

    # List all JSON files in the current channel's directory
    json_files = [f for f in os.listdir(channel_directory) if f.endswith('.json')]

    for json_file in json_files:
        json_path = os.path.join(channel_directory, json_file)

        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Extract the relevant data from the current JSON file
        documents = [item['text'] for item in data]
        metadatas = [{"title": item['title'], "start": item['start'], "duration": item['duration']} for item in data]
        ids = [str(i) for i in range(len(data))]

        # Add the data from the current JSON file to the collection
        ids = ["id" + str(global_id_counter + i) for i in range(len(data))]
        global_id_counter += len(data)
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
