import json
import time
import sys
from kafka import KafkaProducer

import cv2
import base64

def encode_frame(frame):
    _, buffer = cv2.imencode('.png', frame)
    encoded = base64.b64encode(buffer.tobytes()).decode()
    return encoded

class VideoSource:
    def __init__(self, video_path):
        self.video_path = video_path

    def run(self, producer: KafkaProducer, topic_name, ):
        cap = cv2.VideoCapture(self.video_path)

        if not cap.isOpened():
            print(f"Error opening video file: {self.video_path}")
            return
        frame_number = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_bytes = encode_frame(frame)
            producer.send(topic_name, value={'frame_number': frame_number, 'data': frame_bytes})
            frame_number += 1
            # time.sleep(0.2)

        producer.send(topic_name, value={'data': 'EOF'})
        cap.release()


def custom_byte_serializer(data):
    return data


if __name__ == '__main__':
    video_number = sys.argv[1]
    producer = KafkaProducer(bootstrap_servers=['kafka-broker:9092'],
                             value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    source = VideoSource("video/video" + video_number + ".mp4")
    source.run(producer, "in" + video_number + "-topic")
