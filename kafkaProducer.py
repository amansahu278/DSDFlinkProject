import time

from kafka import KafkaProducer
import pickle
import cv2


def encode_frame(frame):
    return pickle.dumps(frame, protocol=pickle.HIGHEST_PROTOCOL)


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
            time.sleep(2)
        # producer.send(topic_name, b"EOF")
        cap.release()


def custom_byte_serializer(data):
    return data


producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                         value_serializer=custom_byte_serializer)

if __name__ == '__main__':
    video_in_path = "/Users/amansahu/COMP 6231/projectowrks/sample.mp4"
    source = VideoSource(video_in_path)
    source.run(producer, "my-topic")
