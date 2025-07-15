import pika, json, tempfile, os
from bson.objectid import ObjectId
import moviepy.editor

def start(message, fs_videos, fs_mp3s, channel, properties=None):
    message = json.loads(message)

    # empty temp file
    tf = tempfile.NamedTemporaryFile()
    # video content
    out = fs_videos.get(ObjectId(message["video_fid"]))
    # add video content to temp file
    tf.write(out.read())
    # create audio from temp video file
    audio = moviepy.editor.VideoFileClip(tf.name).audio
    tf.close()

    # write audio to the file
    tf_path = tempfile.gettempdir() + f"/{message['video_fid']}.mp3"
    audio.write_audiofile(tf_path)

     # Save the mp3 file to MongoDB GridFS
    with open(tf_path, "rb") as f:
        data = f.read()
        fid = fs_mp3s.put(data)
    os.remove(tf_path)

    message["mp3_fid"] = str(fid)

    if properties and getattr(properties, "reply_to", None) and getattr(properties, "correlation_id", None):
        try:
            channel.basic_publish(
                exchange="",
                routing_key=properties.reply_to,
                body=json.dumps({"mp3_fid": str(fid)}),
                properties=type(properties)(
                    correlation_id=properties.correlation_id
                ),
            )
        except Exception as err:
            fs_mp3s.delete(fid)
            return "failed to publish RPC reply"

        # Legacy: publish to MP3_QUEUE for non-RPC usage
        try:
            print("Publishing to MP3_QUEUE:", message)
            channel.basic_publish(
                exchange="",
                routing_key=os.environ.get("MP3_QUEUE"),
                body=json.dumps(message),
                properties=pika.BasicProperties(
                        delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                    ),
            )
        except Exception as err:
            fs_mp3s.delete(fid)
            return "failed to publish message to MP3_QUEUE"


