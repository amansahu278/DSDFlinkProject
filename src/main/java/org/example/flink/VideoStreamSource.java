package org.example.flink;

import nu.pattern.OpenCV;
import org.apache.flink.streaming.api.functions.source.SourceFunction;
import org.example.Helpers;
import org.opencv.core.Mat;
import org.opencv.core.MatOfByte;
import org.opencv.imgproc.Imgproc;
import org.opencv.videoio.VideoCapture;
import org.opencv.videoio.VideoWriter;
import org.opencv.videoio.Videoio;

import static org.example.Helpers.convertIntToByteArray;

class VideoStreamSource implements SourceFunction<byte[]> {
    static {
        OpenCV.loadLocally();
    }
    private volatile boolean isRunning = true;
    private final String videoFilePath;

    public VideoStreamSource(String videoFilePath) {
        this.videoFilePath = videoFilePath;
    }

    @Override
    public void run(SourceContext<byte[]> ctx) throws Exception {
        // Implement logic to read video frames from the file
        // Use ctx.collect to emit each frame
        // Replace this with your actual logic
        VideoCapture videoCapture = new VideoCapture(videoFilePath);
        Mat frame = new Mat();
        MatOfByte byteFrame;

        if(!videoCapture.isOpened()){
            System.err.println("Error in opening video file");
            return;
        }
        try{
            while(videoCapture.read(frame)) {
                // Input is of the form BGR, transforming it to RGB
                Imgproc.cvtColor(frame, frame, Imgproc.COLOR_BGR2RGB);
                int fourcc = VideoWriter.fourcc('M', 'J', 'P', 'G');
                int fps = 0;
                videoCapture.set(Videoio.CAP_PROP_FOURCC, fourcc);
                videoCapture.set(Videoio.CAP_PROP_FPS, fps);
                ctx.collect(Helpers.frameToByteArray(frame));
            }
        } catch (Exception ex){
            System.err.println(ex.getMessage());
        }
    }

    @Override
    public void cancel() {
        // Implement cancellation logic if needed
        isRunning = false;
    }
}