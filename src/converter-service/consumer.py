import pika, sys, os, time
from pymongo import MongoClient
import gridfs
from convert import to_mp3
import threading
import health_server

def run_health_server():
    health_server.app.run(host='0.0.0.0', port=8000)

def get_mongodb_client():
    # Pull individual pieces from environment variables
    host = os.environ.get("MONGODB_HOST")
    port = os.environ.get("MONGODB_PORT")
    user = os.environ.get("MONGO_USER")
    password = os.environ.get("MONGO_PASS")

    # Assemble the URI manually
    uri = f"mongodb://{user}:{password}@{host}:{port}/?authSource=admin"
    
    return MongoClient(uri)

def main():

    # Start health server in a background thread
    t = threading.Thread(target=run_health_server, daemon=True)
    t.start()

    client = get_mongodb_client()
    db_videos = client.videos
    db_mp3s = client.mp3s
    # gridfs
    fs_videos = gridfs.GridFS(db_videos)
    fs_mp3s = gridfs.GridFS(db_mp3s)

    connection = None
    channel = None

    # # rabbitmq connection
    # connection = pika.BlockingConnection(
    #     pika.ConnectionParameters(host='rabbitmq',heartbeat=0)
    # )

    # Robust RabbitMQ connection and consuming loop
    while True:
        try:
            print("Attempting to connect to RabbitMQ...")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='rabbitmq', heartbeat=0)
            )
            print("✅ Connected to RabbitMQ")
            
            channel = connection.channel()
            health_server.set_rabbit_connection(connection)
            health_server.set_rabbit_channel(channel)
            
            def callback(ch, method, properties, body):
                err = to_mp3.start(body, fs_videos, fs_mp3s, ch, properties)
                if err:
                    ch.basic_nack(delivery_tag=method.delivery_tag)
                else:
                    ch.basic_ack(delivery_tag=method.delivery_tag)
            
            channel.basic_consume(
                queue=os.environ.get("VIDEO_QUEUE"), on_message_callback=callback
            )
            
            print("Waiting for messages, to exit press CTRL+C")
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError as e:
            print(f"❌ Connection error: {e}. Retrying in 5 seconds...")
            if connection is not None and not connection.is_closed:
                connection.close()
            connection = None
            channel = None
            health_server.clear_rabbit_connection()
            time.sleep(5)
        except pika.exceptions.ConnectionClosedByBroker as e:
            print(f"❌ Connection closed by broker: {e}. Retrying in 5 seconds...")
            connection = None
            channel = None
            health_server.clear_rabbit_connection()
            time.sleep(5)
        except Exception as e:
            print(f"❌ Unexpected error: {e}. Retrying in 5 seconds...")
            if connection is not None and not connection.is_closed:
                connection.close()
            connection = None
            channel = None
            health_server.clear_rabbit_connection()
            time.sleep(5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)