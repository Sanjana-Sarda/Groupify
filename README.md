# Groupify

## Building and Running
- Prerequisites
    - Python >=3.7 (and pip)
    - npm

- Clone the repo and cd into it
- Install the dependencies
```bash
$ pip install -r requirements.txt
$ cd app
$ npm install
```
- Transpile the JSX to `app/static/js/build/` (you can keep this running in the background)
```bash
$ cd js
$ npx babel --watch . --out-dir ../static/js/build --presets react-app/prod
```
- Make `app/psecrets.py`
```python
# spotify client and secret id (https://developer.spotify.com/dashboard)
client_id = 'your_client_id'
secret = 'your_client_secret'
```
- Run Flask
```bash
$ cd ..
$ python app.py
```

## Data
We are using the following datasets: 
1. Spotify Million Playlist Challenge database: https://research.atspotify.com/the-million-playlist-dataset-remastered/ 
2. Spotify Skip Prediction Data Challenge: https://www.aicrowd.com/challenges/spotify-sequential-skip-prediction-challenge 
3. Public data available through Spotipy API

For 1 and 2, they can be accessed at the following GCP bucket gs://groupify2022, project name: strategic-altar-342721 for purposes of running source code - Please contact us for access. 

```
$ gsutil config
$ gstuil ls 
$ gsutil cp gs://<bucketname>>/<<filename>> <<localpath>>
```
