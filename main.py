from dotenv import load_dotenv
load_dotenv()  # This loads the environment variables from .env
from flask import Flask, render_template, jsonify, request
import requests
import mysql.connector
from datetime import datetime
from config import config  # Import the configuration

app = Flask(__name__)


def get_joke():
    response = requests.get('https://v2.jokeapi.dev/joke/Pun?type=single')
    if response.status_code == 200:
        return response.json()['joke']
    else:
        return 'No joke available at the moment.'

def save_joke(joke):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    add_joke = ("INSERT INTO jokes "
                "(joke, created_at) "
                "VALUES (%s, %s)")
    data_joke = (joke, datetime.now())
    cursor.execute(add_joke, data_joke)
    connection.commit()
    cursor.close()
    connection.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-joke', methods=['POST'])
def generate_joke():
    joke = get_joke()
    save_joke(joke)
    return jsonify(joke=joke)

if __name__ == '__main__':
    app.run(debug=True)
