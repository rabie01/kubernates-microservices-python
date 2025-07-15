import pika, json, uuid, time


def upload(f, fs, channel, access):
    try:
        video_fid = fs.put(f)
    except Exception as err:
        print(err)
        return "internal server error, fs level", 500

# 1. define correlation_id
    correlation_id = str(uuid.uuid4())

    # 2. Set up a temporary reply queue
    result = channel.queue_declare(queue='', exclusive=True)
    callback_queue = result.method.queue

    # 3. Publish message with reply_to and correlation_id
    message = {
        "video_fid": str(video_fid),
        "mp3_fid": None,
        "username": access["username"],
    }
    channel.basic_publish(
        exchange="",
        routing_key="video",
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
            reply_to=callback_queue,
            correlation_id=correlation_id,
        ),
    )

    # 4. Wait for the reply with the mp3_fid, with timeout
    mp3_fid = None
    timeout_seconds = 120  # Set your desired timeout
    start_time = time.time()

    def on_response(ch, method, props, body):
        nonlocal mp3_fid
        if props.correlation_id == correlation_id:
            mp3_fid = json.loads(body)["mp3_fid"]
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=callback_queue,
        on_message_callback=on_response,
        auto_ack=False,
    )
    while mp3_fid is None and (time.time() - start_time) < timeout_seconds:
        channel.connection.process_data_events(time_limit=1)

    if mp3_fid is None:
        return {"error": "Timeout waiting for mp3 conversion"}, 504

    return {"mp3_fid": mp3_fid}, 200