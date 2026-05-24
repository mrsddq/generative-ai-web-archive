import os
import uuid

import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request


load_dotenv()
app = Flask(__name__)


def translate_text(text, target_language):
    key = os.environ.get('KEY')
    endpoint = os.environ.get('ENDPOINT')
    location = os.environ.get('LOCATION')

    if not all([key, endpoint, location]):
        raise RuntimeError('Azure Translator environment variables are not configured.')

    constructed_url = f"{endpoint.rstrip('/')}/translate?api-version=3.0&to={target_language}"
    headers = {
        'Ocp-Apim-Subscription-Key': key,
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4()),
    }
    body = [{'text': text}]

    response = requests.post(constructed_url, headers=headers, json=body, timeout=20)
    response.raise_for_status()
    payload = response.json()
    return payload[0]['translations'][0]['text']


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def index_post():
    original_text = request.form.get('text', '').strip()
    target_language = request.form.get('language', 'en')

    if not original_text:
        return render_template('index.html', error='Enter text before translating.'), 400

    try:
        translated_text = translate_text(original_text, target_language)
    except (RuntimeError, requests.RequestException, KeyError, IndexError) as exc:
        return render_template('index.html', error=str(exc)), 502

    return render_template(
        'results.html',
        translated_text=translated_text,
        original_text=original_text,
        target_language=target_language
    )


if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true')
