from dotenv import load_dotenv
load_dotenv()  # This loads the environment variables from .env
from flask import Flask, render_template, jsonify, request
import requests
import mysql.connector
from datetime import datetime
from config import config  # Import the configuration


app = Flask(__name__)


def get_joke(category='Misc'):
    response = requests.get(f'https://v2.jokeapi.dev/joke/{category}?type=single')
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

def fetch_jokes_from_db():
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM jokes ORDER BY created_at DESC")
    jokes_list = cursor.fetchall()
    cursor.close()
    connection.close()

    # handling datetime format from DB to reflect correctly in UI
    for joke in jokes_list:
        # converting format datetime object to CST timezone
        joke['created_at'] = joke['created_at'].strftime('%m/%d/%Y, %I:%M:%S %p')
    return jokes_list

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/jokes')
def jokes():
    # Fetch jokes from the database
    jokes_list = fetch_jokes_from_db()
    return jsonify(jokes=jokes_list)


@app.route('/generate-joke', methods=['POST'])
def generate_joke():
    joke = get_joke()
    save_joke(joke)
    return jsonify(joke=joke)

if __name__ == '__main__':
    app.run(debug=True)
