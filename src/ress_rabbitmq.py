import pika

from log import log


class RessRabbitMQ:
    """Utility helper to send messages to RabbitMQ"""

    def __init__(self):
        credentials = pika.PlainCredentials("fold", "wrappass")
        self.parameters = pika.ConnectionParameters("localhost", 5672, "/", credentials)

    def ping(self):
        try:
            # Establish a connection to RabbitMQ server (adjust the hostname and port as needed)
            connection = pika.BlockingConnection(self.parameters)
            connection.close()
            return True
        except pika.exceptions.ConnectionClosedByBroker:
            # Connection closed by RabbitMQ, which indicates that RabbitMQ is available
            return True
        except Exception:
            log("Error connecting to RabbitMQ", level="error")
            # Any other exception, including connection failure, indicates that RabbitMQ is not available
            return False

    def send(self, payload, queue_name="generic"):
        try:
            connection = pika.BlockingConnection(self.parameters)
            channel = connection.channel()

            # Declare a queue (if it doesn't exist, it will be created)
            queue_name = queue_name
            channel.queue_declare(queue=queue_name)

            # Publish the event/message to the queue
            channel.basic_publish(exchange="", routing_key=queue_name, body=payload)

            log(f"Sent event to RabbitMQ {payload}")
            # Close the connection
            connection.close()

        except Exception:
            log("Error sending event to RabbitMQ", level="error")
