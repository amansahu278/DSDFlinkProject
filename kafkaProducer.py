import time
import sys
from kafka import KafkaProducer

import cv2
import base64

def encode_frame(frame):
    _, buffer = cv2.imencode('.png', frame)
    encoded = base64.b64encode(buffer.tobytes())
    return encoded

class VideoSource:
    def __init__(self, video_path):
        self.video_path = video_path

    def run(self, producer: KafkaProducer, topic_name, ):
        cap = cv2.VideoCapture(self.video_path)

        if not cap.isOpened():
            print(f"Error opening video file: {self.video_path}")
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_bytes = encode_frame(frame)
            producer.send(topic_name, frame_bytes)
            # time.sleep(0.2)

        producer.send(topic_name, b"EOF")
        cap.release()


def custom_byte_serializer(data):
    return data


if __name__ == '__main__':
    video_in_path = sys.argv[1]
    producer = KafkaProducer(bootstrap_servers=['kafka-broker:9092'])
    source = VideoSource(video_in_path)
    source.run(producer, "in-topic")
