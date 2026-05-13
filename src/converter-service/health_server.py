import os
from flask import Flask
from pymongo import MongoClient

app = Flask(__name__)
# Assemble the URI manually from individual environment variables
def get_mongodb_uri():
    user = os.environ.get('MONGO_USER')
    password = os.environ.get('MONGO_PASS')
    host = os.environ.get('MONGODB_HOST')
    port = os.environ.get('MONGODB_PORT')
    return f"mongodb://{user}:{password}@{host}:{port}/?authSource=admin"

# Initialize client using the manual URI
client = MongoClient(get_mongodb_uri(), serverSelectionTimeoutMS=2000)

rabbit_connection = None
rabbit_channel = None


def set_rabbit_connection(conn):
    global rabbit_connection
    rabbit_connection = conn


def set_rabbit_channel(ch):
    global rabbit_channel
    rabbit_channel = ch


def clear_rabbit_connection():
    global rabbit_connection, rabbit_channel
    rabbit_channel = None
    rabbit_connection = None


@app.route('/', methods=['GET'])
def simple_liveness():
    return "Alive", 200


@app.route('/healthz')
def health():
    try:
        client.server_info()
    except Exception as e:
        return f"MongoDB error: {e}", 500

    if rabbit_connection is None or getattr(rabbit_connection, 'is_closed', True):
        return "RabbitMQ connection not ready", 503

    if rabbit_channel is None or getattr(rabbit_channel, 'is_closed', True):
        return "RabbitMQ channel not ready", 503

    return "OK", 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
