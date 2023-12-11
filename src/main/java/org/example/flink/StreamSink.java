package org.example.flink;

import nu.pattern.OpenCV;
import org.apache.flink.streaming.api.functions.sink.SinkFunction;
import org.example.Helpers;
import org.opencv.core.Mat;
import org.opencv.imgproc.Imgproc;
import org.opencv.videoio.VideoWriter;

public class StreamSink implements SinkFunction<byte[]> {
    static {
        OpenCV.loadLocally();
    }
    private final String outPath;
    private VideoWriter writer;
    public StreamSink(String outPath) {
        this.outPath = outPath;
    }

    @Override
    public void invoke(byte[] value, Context ctx){
        if(value != null && value.length != 0){
            int fourcc = Helpers.getFourCCFromByteArray(value);
            int fps = Helpers.getFpsFromByteArray(value);
            Mat frame = Helpers.getFrameFromByteArray(value);

            if(writer == null){
                writer = new VideoWriter(outPath, fourcc, fps, frame.size(), true);
            }
            try {
                Imgproc.cvtColor(frame, frame, Imgproc.COLOR_RGB2BGR);
                writer.write(frame);
            } catch (Exception e) {
                System.err.println(e.getMessage());
            }
        } else {
            if(writer != null && writer.isOpened()){
                writer.release();
            }
        }
    }

}
