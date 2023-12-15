package org.example;

import nu.pattern.OpenCV;
import org.apache.flink.shaded.guava31.com.google.common.primitives.Bytes;
import org.opencv.core.Mat;
import org.opencv.core.MatOfByte;
import org.opencv.core.MatOfInt;
import org.opencv.imgcodecs.Imgcodecs;

import java.util.Arrays;

public class Helpers {
    public static byte[] convertIntToByteArray(int value) {
        return new byte[] {
                (byte)(value >> 24),
                (byte)(value >> 16),
                (byte)(value >> 8),
                (byte)value
        };
    }

    public static int convertByteArrayToInt(byte[] bytes) {
        return ((bytes[0] & 0xFF) << 24) |
                ((bytes[1] & 0xFF) << 16) |
                ((bytes[2] & 0xFF) << 8) |
                ((bytes[3] & 0xFF) << 0);
    }

    public static byte[] frameAndInfoToByteArray(int fourcc, int fps, Mat frame){
        return Bytes.concat(convertIntToByteArray(fourcc), convertIntToByteArray(fps), frameToByteArray(frame));
    }


    public static int getFpsFromByteArray(byte[] array){
        byte[] subarr = new byte[4];
        for(int i = 4; i<8; i++){
            subarr[i - 4] = array[i];
        }
        return convertByteArrayToInt(subarr);
    }

    public static int getFourCCFromByteArray(byte[] array){
        byte[] subarr = new byte[4];
        for(int i = 0; i<4; i++){
            subarr[i] = array[i];
        }
        return convertByteArrayToInt(subarr);
    }

    public static byte[] frameToByteArray(Mat frame){
        MatOfByte matOfByte = new MatOfByte();
        Imgcodecs.imencode(".png", frame, matOfByte);
        return matOfByte.toArray();
    }

    public static Mat getFrameFromByteArray(byte[] array){
        return getFrameFromSubarray(Arrays.copyOfRange(array, 8, array.length));
    }

    private static Mat getFrameFromSubarray(byte[] array){
        MatOfByte matOfByte = new MatOfByte(array);
        return Imgcodecs.imdecode(matOfByte, Imgcodecs.IMREAD_UNCHANGED);
    }
}
