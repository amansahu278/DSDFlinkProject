from pyflink.datastream.connectors import StreamingFileSink
from pyflink.datastream import TimeCharacteristic

import sys
from pyflink.datastream.functions import ProcessFunction, RuntimeContext
from pyflink.datastream.functions import SourceFunction, SinkFunction
from pyflink.common import WatermarkStrategy, RestartStrategies
from pyflink.common.typeinfo import Types
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream.connectors import FlinkKafkaConsumer
import cv2
import numpy as np
import json
import base64


def adjust_gamma(image, gamma=1.0):
    # build a lookup table mapping the pixel values [0, 255] to
    # their adjusted gamma values
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
                      for i in np.arange(0, 256)]).astype("uint8")
    # apply gamma correction using the lookup table
    return cv2.LUT(image, table)


def perform_anaglyph(consumer_value, offset=20):
    data = json.loads(consumer_value)
    if data["data"] == "EOF":
        return "EOF"

    raw_img = base64.b64decode(data["data"])
    frame_image = cv2.imdecode(np.frombuffer(raw_img, dtype=np.uint8), cv2.IMREAD_COLOR)
    mono_image = cv2.cvtColor(frame_image, cv2.COLOR_BGR2RGB)

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

    return cv2.cvtColor(processed_frame, cv2.COLOR_RGB2BGR)


class VideoWriterProcessFunction(ProcessFunction):
    def __init__(self, video_path, fps):
        self.video_path = video_path
        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.fps = fps
        self.video_writer = None

    def open(self, runtime_context: RuntimeContext):
        self.video_writer = None

    def process_element(self, value, ctx: 'ProcessFunction.Context'):
        frame = perform_anaglyph(value)
        if frame == "EOF":
            self.close()
            raise Exception("EOF")

        if self.video_writer is None:
            height, width, _ = frame.shape
            self.video_writer = cv2.VideoWriter(self.video_path, self.fourcc, self.fps, (width, height))
        if self.video_writer is not None:
            self.video_writer.write(frame)
        else:
            raise Exception("Videowriter not open")

    def close(self):
        print("Closing...")
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None


def main():
    file_num = sys.argv[1]
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_restart_strategy(RestartStrategies.fixed_delay_restart(
        3,  # number of restart attempts
        10000  # delay(millisecond)
    ))

    kafka_consumer = FlinkKafkaConsumer(
        topics='in'+file_num+'-topic',
        deserialization_schema=SimpleStringSchema(),
        properties={'bootstrap.servers': 'kafka-broker:9092', 'group.id': 'my-group',
                    'auto.offset.reset': 'earliest'})

    video_stream = env.add_source(kafka_consumer)

    video_out_path = "/data/output" + file_num + ".mp4"
    fps = 30

    processFunction = VideoWriterProcessFunction(video_out_path, fps);

    video_stream.process(processFunction)

    try:
        env.execute("Kafka Flink Video Processing")
    except Exception as ex:
        if ex.args[0] == "EOF":
            print("End of job")


if __name__ == '__main__':
    main()
