package org.example.flink;
import nu.pattern.OpenCV;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.example.AnaglyphTransform;

public class VideoProcessingJob {

    public static void main(String[] args) throws Exception {
        OpenCV.loadLocally();
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        // Replace "path/to/your/video.mp4" with the actual path to your MP4 file
        String videoInPath = "/Users/amansahu/COMP 6231/projectowrks/sample.mp4";
        String videoOutPath = "/Users/amansahu/COMP 6231/projectowrks/output.mp4";

        VideoStreamSource videoSource = new VideoStreamSource(videoInPath);
        // Define the video stream source
        DataStream<byte[]> videoStream = env.addSource(videoSource);

        // Apply your video processing transformations (e.g., OpenCV processing)
        DataStream<byte[]> processedVideoStream = videoStream.map(value -> {
                    return AnaglyphTransform.anaglyphTransform(value);
                });

        // Define the video stream sink
        processedVideoStream.addSink(new StreamSink(videoOutPath));

        // Execute the Flink job
        env.execute("Video Processing Job");
    }
}
