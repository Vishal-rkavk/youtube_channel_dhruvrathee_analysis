#!/usr/bin/env python
# coding: utf-8


'''

--------

This is a script to fetch youtube channel's data
using developer API and analyse the channel performance of a
popular youtube channel "Dhruv Rathee"

--------


'''


# Youtube developer API access key
api_key = 'AIzaSyCIGnwrsI9wp6RxyP6vfOCOD1XcVTMXPVQ'



# Import all necessary Libs.
from googleapiclient.discovery import build
import pandas as pd
import googleapiclient
import pprint
import dateutil,isodate
import seaborn as sns
import matplotlib.pyplot as plt
from numpy.polynomial.polynomial import polyfit
from wordcloud import WordCloud



# Declaring constants to fetch data from youtubr API
api_service_name = "youtube"
api_version = "v3"


# This snippet below fetches the channel's general data for username provided
youtube =  build(
    api_service_name, api_version, developerKey=api_key)

request = youtube.channels().list(
    forUsername= 'dhruvrathee',
    part='statistics,snippet,id,contentDetails',
    maxResults =5
)
response = request.execute()



# This snippet below feteches at max 50 playlists from the channelID provided
youtube =  build(
    api_service_name, api_version, developerKey=api_key)

request = youtube.playlists().list(
    channelId = 'UC-CSyyi47VX1lD9zyeABW3w',part = 'contentDetails,snippet',maxResults=50
        
    )
response = request.execute()

playlist_ids = []
for i in response['items']:
    playlist_ids.append(i['id'])



# This snippet below fetches the videos present from the playlistIds given
video_ids= []
for j in playlist_ids:
    request = youtube.playlistItems().list(
            playlistId = j,
            part = 'contentDetails,status,snippet',maxResults=50
        )
    response = request.execute()

    for k in response['items']:
        video_ids.append(k['contentDetails']['videoId'])
print('Total Playists',len(playlist_ids) )
print('Total Videos', len(video_ids) )



# The snippet below gets all the information of the videos and we convert it into dataframe
request = youtube.videos().list(
    
    id = video_ids[0:50],
    part="contentDetails,statistics,snippet"
   
)
response = request.execute()
all_videos = []
for video in response['items']:
    stats= {'snippet':   ['channelTitle','description','title','tags','publishedAt'],
            'contentDetails': ['duration','definition','caption'],
            'statistics': ['commentCount','likeCount','viewCount']
    }
    
    video_info = {}
    video_info['video_id'] = video['id']
    for k in stats.keys():
        for v in stats[k]:
            video_info[v] = video[k][v]
            
    all_videos.append(video_info)
df= pd.DataFrame(all_videos)



# Convert appropriate columns to numeric
numeric_cols = ['commentCount','likeCount','viewCount']
df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric,errors='coerce')





# Make day of the week available
df['publishedAt'] = df['publishedAt'].apply(lambda x : dateutil.parser.parse(x))
df['publishedDay'] = df['publishedAt'].apply(lambda x : x.strftime("%A"))



# Converts ISO861 date format to seconds
df['duration'] = df['duration'].apply(lambda x :  isodate.parse_duration(x))
df['duration'] = df['duration'].dt.total_seconds()





# Top 10 best performing videos from playlist
df['smallTitle'] = df['title'].apply(lambda x: x.split('|',1)[0])

ax=sns.barplot(x= 'smallTitle',y='viewCount',data=df[:10].sort_values('viewCount',ascending=False))
plot = ax.set_xticklabels(ax.get_xticklabels(),rotation=90)


# # Top 10 worst performing videos from the playlist
ax=sns.barplot(x= 'smallTitle',y='viewCount',data=df[:10].sort_values('viewCount',ascending=True))
plot = ax.set_xticklabels(ax.get_xticklabels(),rotation=90)

"""
Distribution of views across videos, looks like evenly distributed views 
This shows all the videos Dhruv makes normally gets views from atleast 2M to 10M

"""
sns.violinplot(df, x='channelTitle',y='viewCount')


# Visualise correlation between comments-views, Likes-views
# This shows the comment count is not linearly(strongly correlated) growing as the views grows

plt.scatter(x=df['viewCount'],y=df['commentCount'])

# regression line
sns.regplot(x=df['viewCount'], y=df['commentCount'])



# This shows strong linear correlation between views and likes
plt.scatter(x=df['viewCount'],y=df['likeCount'])
# regression line
sns.regplot(x=df['viewCount'], y=df['likeCount'])


# This plot shows the number of videos with specific duration
sns.histplot(data=df,x='duration',bins=20)


# # Wordcloud i.e frequency of words from the title of each video

text = ' '.join(df['title'].tolist())

# Create and generate a word cloud image:
wordcloud = WordCloud().generate(text)

# Display the generated image:
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.show()


# # Count of videos uploaded by weekday
df_temp = pd.DataFrame(df['publishedDay'].value_counts())
weekdays = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
# df_temp = df_temp.reindex(weekdays)
df_temp.reset_index().plot.bar(x='index',y='publishedDay')

