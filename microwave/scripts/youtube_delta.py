from pprint import pprint
from apiclient.discovery import build

DEVELOPER_KEY = 'AIzaSyC-epq05GzsgImwy_Z62oKDE4Ur06hOGSo'

youtube = build('youtube', 'v3', developerKey=DEVELOPER_KEY)

queries = ['The Dawn of a New Age Makeup And Vanity Set',
           'Reunion Arc Lab Remix Near The Parenthesis']

for query in queries:

    print(query)
    results = youtube.search().list(
        q=query,
        part='snippet',
        type='video'
    ).execute()
    ids = [item['id']['videoId'] for item in results.get('items', [])]
    for i in ids:
        print(i)
    print()