import os, gridfs, pika, json, time
from flask import Flask, request, send_file, jsonify
from flask_pymongo import PyMongo
from auth import validate
from auth_svc import access
from storage import util
from bson.objectid import ObjectId
from werkzeug.middleware.dispatcher import DispatcherMiddleware

server = Flask(__name__)

mongo_video = PyMongo(server, uri=os.environ.get('MONGODB_VIDEOS_URI'))

mongo_mp3 = PyMongo(server, uri=os.environ.get('MONGODB_MP3S_URI'))

fs_videos = gridfs.GridFS(mongo_video.db)
fs_mp3s = gridfs.GridFS(mongo_mp3.db)

# Global connection and channel - lazy initialized
connection = None
channel = None

def get_channel(max_retries=5):
    """Lazy initialize and return RabbitMQ channel with retry logic."""
    global connection, channel
    
    if channel is not None and not channel.is_closed:
        return channel
    
    for attempt in range(max_retries):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host="rabbitmq",
                    heartbeat=600,  # Enable heartbeat (10 minutes)
                    connection_attempts=1,
                    socket_timeout=5.0
                )
            )
            channel = connection.channel()
            print(f"Successfully connected to RabbitMQ on attempt {attempt + 1}")
            return channel
        except pika.exceptions.AMQPConnectionError as e:
            print(f"RabbitMQ connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                wait_time = min(2 ** attempt, 30)  # Exponential backoff, max 30s
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise
    
    return channel

@server.route("/login", methods=["POST"])
def login():
    token, err = access.login(request)

    if not err:
        return token
    else:
        return err

@server.route("/upload", methods=["POST"])
def upload():
    access, err = validate.token(request)

    if err:
        return err

    access = json.loads(access)
    if not access["admin"]:
        return "not authorized", 401
    if len(request.files) != 1:
        return "exactly 1 file required", 400

    try:
        ch = get_channel()
        # f = next(iter(request.files.values()))
        for _, f in request.files.items():
            result, status = util.upload(f, fs_videos, ch, access)
        return jsonify(result), status
    except Exception as e:
        print(f"Upload error: {e}")
        return "service unavailable", 503
        

@server.route("/download", methods=["GET"])
def download():
    access, err = validate.token(request)

    if err:
        return err

    access = json.loads(access)

    if access["admin"]:
        fid_string = request.args.get("fid")

        if not fid_string:
            return "fid is required", 400

        try:
            out = fs_mp3s.get(ObjectId(fid_string))
            return send_file(out, download_name=f"{fid_string}.mp3")
        except Exception as err:
            print(err)
            return "internal server error", 500

    return "not authorized", 401


@server.route("/health", methods=["GET"])
def health():
    """Health check endpoint for Kubernetes liveness/readiness probes."""
    try:
        # Check MongoDB connections
        mongo_video.db.command('ping')
        mongo_mp3.db.command('ping')
        return {"status": "healthy"}, 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return {"status": "unhealthy"}, 503

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)
