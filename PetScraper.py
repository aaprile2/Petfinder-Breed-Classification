'''
Petfinder Scraper

Modified: 2/26/2020

Notes (before implementing on HPC): 
* Update variable 'pages' in 'Data Collection' - defaults to ALL pages of response
* Update image/CSV paths in 'Image and Label Scraping' 
'''

# Imports
import urllib.request
import requests
import pandas as pd
from pandas.io.json import json_normalize
from urllib.error import URLError, HTTPError
import csv
from datetime import datetime
from datetime import timedelta

''' API Preparation '''
# Connecting to Petfinder API
key = '5Wc74lvn49ytLih94Gpgflqyysnne1Fyf9sup9Nf3G9qJkZ2Cb'
secret = 'l5kiXMs8IoBDMpBsvWvLiy8p41GKXyUICrSO23ue'

# Get access token
data = {
  'grant_type': 'client_credentials',
  'client_id': key,
  'client_secret': secret
}

# Saves access token
token = requests.post('https://api.petfinder.com/v2/oauth2/token', data=data).json()['access_token']

# Gets expiration time (necessary to refresh access token)
expires = datetime.now() + timedelta(seconds=3600)

# Creater header for API calls
auth = 'Bearer ' + token

headers = {
    'Authorization': auth,
}


''' Data Collection '''
# Request url head - page number added in for loop
temp = 'https://api.petfinder.com/v2/animals?type=dog&limit=100&sort=-recent&page='

# Gets total page numbers
pages = requests.get(temp+'1', headers=headers).json()['pagination']['total_pages']

# List of dogs
dog_list = []

# Iterates over # of pages wanted, used limit=10 for small testing purposes
for i in range(pages):
    # Check if token expired
    if datetime.now() >= expires:
        token = requests.post('https://api.petfinder.com/v2/oauth2/token', data=data).json()['access_token']
        auth = 'Bearer ' + token
        headers = {'Authorization': auth,}
        expires = datetime.now() + timedelta(seconds=3600)
    
    url = temp + str(i+1)   # Finishes url
    response = requests.get(url, headers=headers)  # Gets response
    
    # If response valid, add response to dogs_list
    if response.status_code == 200: 
        dog_list = dog_list + response.json()['animals']
    

# Reads in breeds mapping and converts to dictionary
breeds = pd.read_csv('breeds2.csv', index_col = 0, header=None, squeeze = True).to_dict()


'''
Data Processing

* Converts response to DataFrame
* Handles missing values
* Maps Petfinder breed labels to Stanford Dog labels
'''
# Converts list to DataFrame
dogs = json_normalize(dog_list)

# Temporarily replaces None (no breed assigned by Petfinder) 
dogs[['breeds.primary','breeds.secondary']] = dogs[['breeds.primary','breeds.secondary']].where(dogs[['breeds.primary','breeds.secondary']].notna(), 'Not avail')

# Replaces Petfinder breed labels with Stanford Dogs labels
dogs[['breeds.primary','breeds.secondary']] = dogs[['breeds.primary','breeds.secondary']].where(dogs[['breeds.primary','breeds.secondary']].isin(breeds.keys()), None)
dogs = dogs.replace({"breeds.primary": breeds, "breeds.secondary": breeds})

# Resets original missing value notation and indices
dogs = dogs[dogs['breeds.primary'].notna() & dogs['breeds.secondary'].notna()]
dogs = dogs.replace({'breeds.primary': {'Not available': None}, 'breeds.secondary':{'Not available': None}})
dogs = dogs.reset_index()


'''
Image and Label Scraping

* Creates empty DataFrame to hold ID and attributes 'Mixed' (Boolean), 'Breeds_Unknown' (Boolean), 'Primary_Breed' (String), 'Secondary_Breed' (String)
* Scrapes images and saves them to designated location
* Exports DataFrame to CSV
'''
# Scraping images
scraped= pd.DataFrame(columns=['ID', 'Mixed', 'Breeds_Unknown','Primary_Breed', 'Secondary_Breed'])

for i in range(len(dogs)):
    
    # Collects image and saves to folder Petfinder_Test with ID as name (matching Stanford Dog Dataset)
    if len(dogs['photos'][i]) != 0:
        # Grabs unique ID (for image name)
        id = dogs.loc[i, 'id']
        
        url = dogs['photos'][i][0].get('large')
        name = "Petfinder_Images\\" + str(id) + ".jpg"
        try:
            urllib.request.urlretrieve(url,name)
            scraped = scraped.append({'ID': id, 'Mixed': dogs.loc[i,'breeds.mixed'], 'Breeds_Unknown': dogs.loc[i,'breeds.unknown'], 'Primary_Breed': dogs.loc[i, 'breeds.primary'], 'Secondary_Breed': dogs.loc[i,'breeds.secondary']},ignore_index=True)
        except HTTPError as e:
            print(e.reason)

# Exports to CSV
scraped.to_csv(r'Petfinder_Labels.csv', index = False)
