package org.example;

import nu.pattern.OpenCV;

import org.bytedeco.javacv.FFmpegFrameGrabber;
import org.bytedeco.javacv.FFmpegFrameRecorder;
import org.bytedeco.javacv.Frame;
import org.bytedeco.javacv.OpenCVFrameConverter;

import org.opencv.core.*;
import org.opencv.imgcodecs.Imgcodecs;
import org.opencv.imgproc.Imgproc;
import org.opencv.videoio.VideoCapture;
import org.opencv.videoio.VideoWriter;
import org.opencv.videoio.Videoio;

import static org.bytedeco.ffmpeg.global.avcodec.AV_CODEC_ID_MPEG4;


public class AnaglyphTransform {

    public static void main(String[] args) {
        OpenCV.loadLocally();
        // Load an example colored image
//        Mat coloredImage = Imgcodecs.imread("/Users/amansahu/Downloads/DSC_2935.JPG", Imgcodecs.IMREAD_COLOR);
//        Imgproc.cvtColor(coloredImage, coloredImage, Imgproc.COLOR_BGR2RGB);
//
//        // Apply the anaglyph transformation
//        Mat anaglyphImage = applyAnaglyphTransform(coloredImage);
//
//        // Save the anaglyph image to a file
//        Imgproc.cvtColor(anaglyphImage, anaglyphImage, Imgproc.COLOR_RGB2BGR);
//        Imgcodecs.imwrite("/Users/amansahu/COMP 6231/dockerLab/anaglyph_image.jpg", anaglyphImage);

        String inPath = "/Users/amansahu/COMP 6231/projectowrks/sample.mp4";
        String outPath = "/Users/amansahu/COMP 6231/projectowrks/out.mp4";

        // Create FFmpegFrameGrabber
        FFmpegFrameGrabber grabber = new FFmpegFrameGrabber(inPath);
        OpenCVFrameConverter.ToMat converterToCVMat = new OpenCVFrameConverter.ToMat();
        OpenCVFrameConverter.ToOrgOpenCvCoreMat converter2 = new OpenCVFrameConverter.ToOrgOpenCvCoreMat();
//        org.opencv.core.Mat cvmat = converter2.convert(converter1.convert(mat));
//        Mat mat2 = converter2.convert(converter1.convert(cvmat));

        try {
            // Start grabbing
            grabber.start();

            // Get video properties
            int width = grabber.getImageWidth();
            int height = grabber.getImageHeight();
            double frameRate = grabber.getFrameRate();
            int videoCoded = grabber.getVideoCodec();
            int videoBitRate = grabber.getVideoBitrate();
//            int pixelFormat = grabber.getPixelFormat();

            // Create FFmpegFrameRecorder for output video
            FFmpegFrameRecorder recorder = new FFmpegFrameRecorder(outPath, width, height);
            recorder.setFormat("mp4");
            recorder.setFrameRate(frameRate);
            recorder.setVideoCodec(videoCoded);
            recorder.setVideoBitrate(videoBitRate);
//            recorder.setPixelFormat(pixelFormat);
            recorder.setAudioChannels(grabber.getAudioChannels());

            // Start recording
            recorder.start();

            // Grab and process frames until the end of the video
            Frame frame;
            while ((frame = grabber.grab()) != null) {
                // Process the frame (replace this with your actual processing logic)
                // Example: You can apply some image processing to 'frame' here...
                // Write the processed frame to the output video

                Mat mat = converter2.convert(frame);
                if(mat != null){
                    mat = applyAnaglyphTransform(mat);
                    frame = converterToCVMat.convert(mat);
                }
                recorder.record(frame);
            }

            // Stop recording
            recorder.stop();
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            // Stop the grabber when done
            try {
                grabber.stop();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
//
//        VideoCapture videoCapture = new VideoCapture(inPath);
//        VideoWriter videoWriter = null;
//        Mat frame = new Mat();
//        Size frameSize = new Size((int) videoCapture.get(Videoio.CAP_PROP_FRAME_WIDTH),
//                (int) videoCapture.get(Videoio.CAP_PROP_FRAME_HEIGHT));
//
//        if(!videoCapture.isOpened()){
//            System.out.println("Cannot open source video");
//        }
//
//        System.out.println("FPS "+ Math.ceil(videoCapture.get(Videoio.CAP_PROP_FPS)));
//        while(videoCapture.read(frame)){
//            if(videoWriter == null){
//                videoWriter = new VideoWriter(outPath, VideoWriter.fourcc('X', 'V', 'I', 'D'), 30, frameSize);
//            }
//            if(!videoWriter.isOpened()){
//                System.out.println("File not opened");
//                return;
//            }
////            Mat out = Helpers.getFrameFromByteArray(anaglyphTransform(Helpers.frameToByteArray(frame)));
////            videoWriter.write(out);
//            videoWriter.write(frame);
//        }
//        videoWriter.release();
    }

    public static byte[] anaglyphTransform(byte[] value){
        Mat frame = Helpers.getFrameFromByteArray(value);
        return new MatOfByte(applyAnaglyphTransform(frame)).toArray();
    }

    private static Mat applyAnaglyphTransform(Mat coloredImage) {
        // Create transformation matrices
        Mat imgtf1 = new Mat(3, 3, CvType.CV_32FC1);
        imgtf1.put(0, 0, 0.7, 0.3, 0, 0, 0, 0, 0, 0);

        Mat imgtf2 = new Mat(3, 3, CvType.CV_32FC1);
        imgtf2.put(0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1);

        int offset = coloredImage.width() / 90;

        // Convert leftView to the appropriate data type
        Mat leftView = new Mat(coloredImage.size(), CvType.CV_32FC3); // Ensure the correct data type
        coloredImage.convertTo(leftView, CvType.CV_32FC3);
        // Create left-eye view (shifted to the left)
        Rect leftRect = new Rect(offset, 0, coloredImage.width() - offset, coloredImage.height());
        Mat leftROI = leftView.submat(leftRect);

        // Create right-eye view (shifted to the right)
        Mat rightView = new Mat(coloredImage.size(), CvType.CV_32FC3); // Ensure the correct data type
        coloredImage.convertTo(rightView, CvType.CV_32FC3);
        Rect rightRect = new Rect(0, 0, coloredImage.width() - offset, coloredImage.height());
        Mat rightROI = rightView.submat(rightRect);

        // Transform left and right views
        Core.transform(leftROI, leftView, imgtf1);
        Core.transform(rightROI, rightView, imgtf2);

        // Combine left and right views and store on leftView
        Core.addWeighted(leftView, 1, rightView, 1, 1, leftView);

        leftView.convertTo(leftView, CvType.CV_8S);
        return leftView;
    }
}
