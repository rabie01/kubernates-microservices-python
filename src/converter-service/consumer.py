import pika, sys, os, time
from pymongo import MongoClient
import gridfs
from convert import to_mp3
import threading
from health_server import app # Import your flask app

def run_health_server():
    app.run(host='0.0.0.0', port=8000)

def main():

    # Start health server in a background thread
    t = threading.Thread(target=run_health_server, daemon=True)
    t.start()

    client = MongoClient(os.environ.get('MONGODB_URI'))
    db_videos = client.videos
    db_mp3s = client.mp3s
    # gridfs
    fs_videos = gridfs.GridFS(db_videos)
    fs_mp3s = gridfs.GridFS(db_mp3s)

    # # rabbitmq connection
    # connection = pika.BlockingConnection(
    #     pika.ConnectionParameters(host='rabbitmq',heartbeat=0)
    # )

    # Robust RabbitMQ connection loop
    connection = None
    while True:
        try:
            print("Attempting to connect to RabbitMQ...")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='rabbitmq', heartbeat=0)
            )
            print("✅ Connected to RabbitMQ")
            break # Exit loop once connected
        except pika.exceptions.AMQPConnectionError:
            print("❌ RabbitMQ connection failed. Retrying in 5 seconds...")
            time.sleep(5)

    channel = connection.channel()

    def callback(ch, method, properties, body):
        err = to_mp3.start(body, fs_videos, fs_mp3s, ch, properties)
        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=os.environ.get("VIDEO_QUEUE"), on_message_callback=callback
    )

    print("Waitting for messages, to exit press CTRL+C")

    channel.start_consuming()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
