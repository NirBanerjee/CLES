package com.amazonaws.lambda.image;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.rekognition.AmazonRekognition;
import com.amazonaws.services.rekognition.AmazonRekognitionClientBuilder;
import com.amazonaws.AmazonClientException;
import com.amazonaws.auth.AWSCredentials;
import com.amazonaws.auth.AWSCredentialsProvider;
import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.DefaultAWSCredentialsProviderChain;
import com.amazonaws.auth.profile.ProfileCredentialsProvider;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.rekognition.model.AmazonRekognitionException;
import com.amazonaws.services.rekognition.model.DetectLabelsRequest;
import com.amazonaws.services.rekognition.model.DetectLabelsResult;
import com.amazonaws.services.rekognition.model.Image;
import com.amazonaws.services.rekognition.model.Label;
import com.amazonaws.services.rekognition.model.S3Object;
import java.util.List;

import org.json.JSONObject;

public class DetectLabels {

    public static String rekogImage(String bucketName, String fileName, Context context) {
        JSONObject recognitionResult = new JSONObject();
        
        // Connect to the rekognition client.
        AWSCredentialsProvider credentialsProvider = new DefaultAWSCredentialsProviderChain();
        
        AmazonRekognition rekognitionClient = AmazonRekognitionClientBuilder
                   .standard()
                   .withRegion(Regions.US_EAST_1)
                   .withCredentials(credentialsProvider)
                   .build();
        
        // Send recognition request to rekcognition.
        DetectLabelsRequest request = new DetectLabelsRequest()
                .withImage(new Image()
                .withS3Object(new S3Object()
                .withName(fileName).withBucket(bucketName)))
                .withMaxLabels(5)
                .withMinConfidence(75F);

        try {
           DetectLabelsResult result = rekognitionClient.detectLabels(request);
           List <Label> labels = result.getLabels();

           System.out.println("Detected labels for " + fileName);
           context.getLogger().log("Detected labels for " + fileName);
           for (Label label: labels) {
               recognitionResult.put(label.getName(), label.getConfidence());
              System.out.println(label.getName() + ": " + label.getConfidence());
              context.getLogger().log(label.getName() + ": " + label.getConfidence());
           }
        } catch(AmazonRekognitionException e) {
           e.printStackTrace();
        }
        
        
        return recognitionResult.toString();
    }
    
//    public static void main(String[] args) {
//        String result = DetectLabelsExample.rekogImage("team2_image_in", "fruits-and-vegetables.jpg");
//        System.out.println(result);
//    }
    
    
//    public static void main(String[] args) throws Exception {
//
//      String photo = "fruits-and-vegetables.jpg";
//      String bucket = "team2_image_in";
//
////      AWSCredentials credentials;
////      try {
////          credentials = new ProfileCredentialsProvider("AdminUser").getCredentials();
////      } catch(Exception e) {
////         throw new AmazonClientException("Cannot load the credentials from the credential profiles file. "
////          + "Please make sure that your credentials file is at the correct "
////          + "location (/Users/jiemin/.aws/credentials), and is in a valid format.", e);
////      }
//
//      AWSCredentialsProvider credentialsProvider = new DefaultAWSCredentialsProviderChain();
//      
//      AmazonRekognition rekognitionClient = AmazonRekognitionClientBuilder
//                 .standard()
//                 .withRegion(Regions.US_EAST_1)
//                 .withCredentials(credentialsProvider)
//                 .build();
//
//      DetectLabelsRequest request = new DetectLabelsRequest()
//              .withImage(new Image()
//              .withS3Object(new S3Object()
//              .withName(photo).withBucket(bucket)))
//              .withMaxLabels(10)
//              .withMinConfidence(75F);
//
//      try {
//         DetectLabelsResult result = rekognitionClient.detectLabels(request);
//         List <Label> labels = result.getLabels();
//
//         System.out.println("Detected labels for " + photo);
//         for (Label label: labels) {
//            System.out.println(label.getName() + ": " + label.getConfidence().toString());
//         }
//      } catch(AmazonRekognitionException e) {
//         e.printStackTrace();
//      }
//   }
}