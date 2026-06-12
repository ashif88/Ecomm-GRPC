from kafka import KafkaProducer
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

producer = None

try:
    kafka_broker_url = os.getenv("KAFKA_BROKER_URL", "")
    if kafka_broker_url:
        # Kafka producer setup
        producer = KafkaProducer(
            bootstrap_servers=kafka_broker_url,  # Get Kafka broker URL from environment variables
            value_serializer=lambda v: v.encode('utf-8')  # Ensures messages are sent as UTF-8 encoded strings
        )
        logger.info("Kafka producer connected successfully!")
    else:
        logger.warning("KAFKA_BROKER_URL is empty. Kafka producer is disabled.")
except Exception as e:
    logger.error(f"Error connecting to Kafka: {e}")

def send_message(topic, message):
    if producer is None:
        logger.warning(f"Kafka producer not connected. Message to topic '{topic}' skipped: {message}")
        return
    try:
        producer.send(topic, message)  # Send message to Kafka topic
        logger.info(f"Message sent to topic '{topic}' successfully!")
    except Exception as e:
        logger.error(f"Error sending message to topic '{topic}': {e}")
