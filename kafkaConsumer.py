import base64

from kafka import KafkaConsumer
import cv2
import numpy as np


def decode_frame(serialized_frame):
    try:
        raw_img = base64.b64decode(serialized_frame)
        image = np.frombuffer(raw_img, dtype=np.uint8)
        frame = cv2.imdecode(image, cv2.IMREAD_COLOR)
        return frame
    except Exception as e:
        print(f"Error during deserialization: {e}")
        return None


class VideoSinkFunction:
    def __init__(self, video_path):
        self.video_path = video_path
        self.video_writer = None
        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.fps = 30
        self.eof_received = False

    def invoke(self, paramValue):
        try:
            if paramValue.value == b"EOF":
                self.eof_received = True
                self.close()
                return
            frame = decode_frame(paramValue.value)
            if frame is not None and frame.shape[0] > 0 and frame.shape[1] > 0:
                if self.video_writer is None:
                    # Initialize the video writer based on the first frame
                    height, width, _ = frame.shape
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # You can change the codec based on your requirements
                    self.video_writer = cv2.VideoWriter(self.video_path, fourcc, self.fps, (width, height))
                if self.video_writer.isOpened():
                    self.video_writer.write(frame)
                    print("Frame successfully written to the video file.")
                else:
                    print("Error opening video writer.")
            else:
                print("Invalid frame. Skipping writing frame to file")
        except Exception as e:
            print(f"Error processing frame: {e}")

    def close(self):
        try:
            if self.video_writer is not None:
                self.video_writer.release()

        except Exception as e:
            print(f"Error closing video writer: {e}")


if __name__ == "__main__":
    video_out_path = "output.mp4"
    sink = VideoSinkFunction(video_out_path)

    consumer = KafkaConsumer(
        'in-topic',
        bootstrap_servers=['kafka-broker:9092'],
        auto_offset_reset='earliest',
        group_id='my-group')

    for value in consumer:
        print("Received a frame")
        if value is None:
            continue
        sink.invoke(value)
        if sink.eof_received:
            print("EOF recieved")
            break

    sink.close()
