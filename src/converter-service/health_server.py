import os
from flask import Flask
from pymongo import MongoClient
import pika

app = Flask(__name__)

@app.route('/', methods=['GET'])
def simple_liveness():
    return "Alive", 200

@app.route('/healthz')
def health():
    try:
        client = MongoClient(os.environ['MONGODB_URI'], serverSelectionTimeoutMS=2000)
        client.server_info()
    except Exception as e:
        return f"MongoDB error: {e}", 500

    try:
        conn = pika.BlockingConnection(pika.ConnectionParameters(host=os.environ['RABBITMQ_HOST'], heartbeat=0, blocked_connection_timeout=2))
        conn.close()
    except Exception as e:
        return f"RabbitMQ error: {e}", 500

    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
