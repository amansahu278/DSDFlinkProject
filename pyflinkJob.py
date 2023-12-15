import cv2
import numpy as np
import pickle
from tqdm import tqdm
from moviepy.editor import VideoFileClip

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import StreamingFileSink
from pyflink.datastream import TimeCharacteristic

from pyflink.datastream.functions import ProcessFunction
from pyflink.datastream.functions import SourceFunction, SinkFunction
from pyflink.common import WatermarkStrategy
from pyflink.common.typeinfo import Types


def adjust_gamma(image, gamma=1.0):
    # build a lookup table mapping the pixel values [0, 255] to
    # their adjusted gamma values
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
                      for i in np.arange(0, 256)]).astype("uint8")
    # apply gamma correction using the lookup table
    return cv2.LUT(image, table)


def performAnaglyph(frame, offset=20):
    mono_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Left view
    left_view = np.roll(mono_image, offset, axis=1)
    left_view[:, :offset, :] = 0

    # Right View
    right_view = np.roll(mono_image, -offset, axis=1)
    right_view[:, -offset:, :] = 0

    # Color anaglyph
    imtf1 = np.resize(np.array([1, 0, 0, 0, 0, 0, 0, 0, 0]), (3, 3))
    imtf2 = np.resize(np.array([0, 0, 0, 0, 1, 0, 0, 0, 1]), (3, 3))

    cv2.transform(left_view, imtf1, left_view)
    cv2.transform(right_view, imtf2, right_view)

    processed_frame = left_view + right_view
    cv2.addWeighted(left_view, 1, right_view, 1, 1, processed_frame)

    processed_frame[:, :, 0] = adjust_gamma(processed_frame[:, :, 0], 1.5)

    processed_frame[:, :offset, :] = 0
    processed_frame[:, -offset:, :] = 0

    return left_view, right_view, cv2.cvtColor(processed_frame, cv2.COLOR_RGB2BGR)


def process_video(videoPath):
    cap = cv2.VideoCapture(videoPath)
    fps = cap.get(cv2.CAP_PROP_FPS)

    out = cv2.VideoWriter("output.mp4",
                          int(cap.get(cv2.CAP_PROP_FOURCC)),
                          fps,
                          (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
                          )
    n_frame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    for frame in tqdm(range(n_frame), total=n_frame):
        ret, img = cap.read()
        if ret == False:
            break
        _, _, processedFrame = performAnaglyph(img, img.shape[1] // 100)
        out.write(processedFrame)

    out.release()
    cap.release()
    clip = VideoFileClip("output.mp4")
    clip = clip.set_audio(VideoFileClip(videoPath).audio)
    clip.write_videofile("finalvideoclip.mp4", audio=True)


def encode_frame(frame):
    return pickle.dumps(frame, protocol=pickle.HIGHEST_PROTOCOL)

def decode_frame(serialized_frame):
    return pickle.loads(serialized_frame)

class VideoSourceFunction(SourceFunction):
    def __init__(self, video_path):
        self.video_path = video_path
        self.is_running = True

    def run(self, ctx: 'SourceFunction.SourceContext'):
        cap = cv2.VideoCapture(self.video_path)

        if not cap.isOpened():
            print(f"Error opening video file: {self.video_path}")
            return

        while self.is_running:
            ret, frame = cap.read()
            if not ret:
                break

            # Assuming you have a function to convert the frame to bytes
            frame_bytes = encode_frame(frame)

            # Emit the frame as a string (you may need to adjust the serialization)
            # ctx.collect(frame_bytes)
            ctx.collect(Row.of(frame_bytes))

        cap.release()

    def cancel(self):
        self.is_running = False


class VideoSinkFunction(SinkFunction):
    def __init__(self, video_path, fourcc, fps):
        self.video_path = video_path
        self.video_writer = None
        self.fourcc = fourcc
        self.fps = fps

    def invoke(self, value, context: 'SinkFunction.Context'):
        try:
            frame = decode_frame(value)

            if self.video_writer is None:
                # Initialize the video writer based on the first frame
                height, width, _ = frame.shape
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # You can change the codec based on your requirements
                self.video_writer = cv2.VideoWriter(self.video_path, self.fourcc, self.fps, (width, height))

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


def main():
    def transformation(serialized_frame):
        frame = decode_frame(serialized_frame)
        return encode_frame(performAnaglyph(frame))

    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_stream_time_characteristic(TimeCharacteristic.EventTime)
    env.set_parallelism(1)  # You can adjust the parallelism based on your requirements

    video_in_path = "/Users/amansahu/COMP 6231/projectowrks/sample.mp4"
    video_out_path = "/Users/amansahu/COMP 6231/projectowrks/out.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = 30

    video_stream = env.from_collection(VideoSourceFunction(video_in_path), Types.ROW([Types.BYTE()]))

    # video_stream = env.add_source(VideoSourceFunction(video_in_path), Types.PRIMITIVE_ARRAY(Types.BYTE()))
    video_stream.map(lambda value: transformation(value),  Types.ROW([Types.BYTE()]))  # Your processing logic can be added here
    video_stream.add_sink(VideoSinkFunction(video_out_path, fourcc, fps))



    env.execute("VideoProcessingJob")

if __name__ == '__main__':
    main()
