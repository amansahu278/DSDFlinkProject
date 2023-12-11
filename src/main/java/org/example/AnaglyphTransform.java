package org.example;

import nu.pattern.OpenCV;
import org.opencv.core.*;
import org.opencv.imgcodecs.Imgcodecs;
import org.opencv.imgproc.Imgproc;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.sql.Array;
import java.util.ArrayList;
import java.util.List;

import static org.opencv.imgproc.Imgproc.COLOR_BGR2RGB;

public class AnaglyphTransform {

    public static void main(String[] args) {
        OpenCV.loadLocally();
        // Load an example colored image
        Mat coloredImage = Imgcodecs.imread("/Users/amansahu/Downloads/DSC_2935.JPG", Imgcodecs.IMREAD_COLOR);
        Imgproc.cvtColor(coloredImage, coloredImage, Imgproc.COLOR_BGR2RGB);

        // Apply the anaglyph transformation
        Mat anaglyphImage = applyAnaglyphTransform(coloredImage);

        // Save the anaglyph image to a file
        Imgproc.cvtColor(anaglyphImage, anaglyphImage, Imgproc.COLOR_RGB2BGR);
        Imgcodecs.imwrite("/Users/amansahu/COMP 6231/dockerLab/anaglyph_image.jpg", anaglyphImage);
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
        Mat newLeftView = new Mat();
        Core.transform(leftROI, newLeftView, imgtf1);

        Mat newRightView = new Mat();
        Core.transform(rightROI, newRightView, imgtf2);

        // Combine left and right views
        Mat anaglyph = new Mat();
        Core.addWeighted(newLeftView, 1, newRightView, 1, 1, anaglyph);

        return anaglyph;
    }
}
