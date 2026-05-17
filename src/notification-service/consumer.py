import pika, sys, os, time, threading
from send import email
from flask import Flask


class BackoffTracker:
    def __init__(self):
        self.failures = 0
        self.base_delay = 2     # Initial wait time in seconds
        self.max_delay = 300    # Caps the maximum delay at 5 minutes

    def get_delay(self):
        self.failures += 1
        # Calculate delay: 2^failures (e.g., 2s, 4s, 8s, 16s...)
        delay = min(self.base_delay ** self.failures, self.max_delay)
        print(f"⚠️ Email failed. Backing off for {delay} seconds to protect IP...")
        return delay

    def reset(self):
        self.failures = 0

# Instantiate the tracker globally
tracker = BackoffTracker()

# Global connection and channel for health checks
connection = None
channel = None
health_status = {"status": "starting"}

# Flask app for health checks
app = Flask(__name__)

@app.route("/live", methods=["GET"])
def live():
    """Liveness endpoint: container process is alive."""
    return {"status": "alive"}, 200

@app.route("/ready", methods=["GET"])
def ready():
    """Readiness endpoint: service can consume from RabbitMQ."""
    try:
        if not os.getenv("GMAIL_ADDRESS") or not os.getenv("GMAIL_PASSWORD"):
            print("🔴 GMAIL_ADDRESS or GMAIL_PASSWORD env vars are not set!")
            return {"status": "not ready, missing gmail configuration"}, 503
        if channel is not None and not channel.is_closed:
            return {"status": "ready"}, 200
        return {"status": "not ready"}, 503
    except Exception as e:
        print(f"Readiness check failed: {e}")
        return {"status": "not ready"}, 503

@app.route("/status", methods=["GET"])
def status():
    return {"status": health_status.get("status", "unknown")}, 200


# RabbitMQ connection and consuming loop mirrors converter service behavior
# so the pod remains alive and retries on broker restart.

def main():
    global connection, channel

    # Start health check server in a separate thread
    def run_health_server():
        app.run(host="0.0.0.0", port=8080, debug=False, use_reloader=False)

    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()

    queue_name = os.environ.get("MP3_QUEUE")
    if not queue_name:
        print("MP3_QUEUE is not configured")
        sys.exit(1)

    while True:
        try:
            print("Attempting to connect to RabbitMQ...")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host="rabbitmq", heartbeat=0)
            )
            print("✅ Connected to RabbitMQ")

            channel = connection.channel()
            channel.queue_declare(queue=queue_name, durable=True)
            health_status["status"] = "healthy"

            # 🚀 2. Update your callback function to use the tracker
            def callback(ch, method, properties, body):
                err = email.notification(body)
                
                if err:                    
                    # Negatively acknowledge and requeue the message safely
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                    ch.stop_consuming()  # Stop consuming to trigger reconnection
                    # 🚀 Explicitly raise an error to crash out of start_consuming()
                    # and jump directly into the backoff sleep exception block below.
                    raise RuntimeError("Email pipeline error triggered backoff")
                else:
                    # Success! Reset the failure counter back to 0
                    tracker.reset()
                    ch.basic_ack(delivery_tag=method.delivery_tag)


            channel.basic_consume(queue=queue_name, on_message_callback=callback)

            print("Waiting for messages. To exit press CTRL+C")
            channel.start_consuming()
        except KeyboardInterrupt:
            print("Interrupted")
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)
        except pika.exceptions.AMQPConnectionError as e:
            print(f"❌ Connection error: {e}. Retrying in 5 seconds...")
            health_status["status"] = "connecting"
            if connection is not None and not connection.is_closed:
                connection.close()
            channel = None
            time.sleep(5)
        except pika.exceptions.ConnectionClosedByBroker as e:
            print(f"❌ Connection closed by broker: {e}. Retrying in 5 seconds...")
            health_status["status"] = "connecting"
            channel = None
            time.sleep(5)
        except Exception as e:
            # 🚀 This is where email failures drop out to!
            # The backoff sleep happens safely here without freezing RabbitMQ heartbeats.
            health_status["status"] = "unhealthy"
            
            if connection is not None and not connection.is_closed:
                connection.close()
            channel = None
            
            delay = tracker.get_delay()
            print(f"⚠️ Email processing pipeline failed. Applying backoff safety delay: {delay}s...")
            time.sleep(delay)


if __name__ == "__main__":
    main()