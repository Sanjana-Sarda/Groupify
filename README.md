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
- Make `app/secrets.py`
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
