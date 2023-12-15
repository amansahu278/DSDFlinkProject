from kafka import KafkaConsumer
import cv2
import pickle


def decode_frame(serialized_frame):
    return pickle.loads(serialized_frame)


class VideoSinkFunction:
    def __init__(self, video_path):
        self.video_path = video_path
        self.video_writer = None
        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.fps = 30

    def invoke(self, value):
        try:
            frame = decode_frame(value)

            if self.video_writer is None:
                # Initialize the video writer based on the first frame
                height, width, _ = frame.shape
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # You can change the codec based on your requirements
                self.video_writer = cv2.VideoWriter(self.video_path, fourcc, self.fps, (width, height))

            # Write the frame to the video file
            self.video_writer.write(frame)

        except Exception as e:
            print(f"Error processing frame: {e}")

    def close(self):
        try:
            if self.video_writer is not None:
                self.video_writer.release()

        except Exception as e:
            print(f"Error closing video writer: {e}")


if __name__ == "__main__":
    video_out_path = "/Users/amansahu/COMP 6231/projectowrks/out.mp4"
    sink = VideoSinkFunction(video_out_path)

    consumer = KafkaConsumer(
        'numtest',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        group_id='my-group')

    for value in consumer:
        print("Recieved a frame")
        sink.invoke(value)

    sink.close()
