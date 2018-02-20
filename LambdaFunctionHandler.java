package com.amazonaws.lambda.image;

import java.text.SimpleDateFormat;
import java.util.Set;

import org.json.JSONObject;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.S3Event;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.amazonaws.services.s3.model.GetObjectRequest;
import com.amazonaws.services.s3.model.S3Object;

public class LambdaFunctionHandler implements RequestHandler<S3Event, String> {

    private AmazonS3 s3 = AmazonS3ClientBuilder.standard().build();

    public LambdaFunctionHandler() {}

    // Test purpose only.
    LambdaFunctionHandler(AmazonS3 s3) {
        this.s3 = s3;
    }

    @Override
    public String handleRequest(S3Event event, Context context) {
        context.getLogger().log("Received event: " + event);

        // Get the object from the event and show its content type
        String bucket = event.getRecords().get(0).getS3().getBucket().getName();
        String key = event.getRecords().get(0).getS3().getObject().getKey();
        String contentType = "";
        
        // Get uploaded file info from s3
        try {
            S3Object response = s3.getObject(new GetObjectRequest(bucket, key));
            contentType = response.getObjectMetadata().getContentType();
            context.getLogger().log("CONTENT TYPE: " + contentType);
        } catch (Exception e) {
            e.printStackTrace();
            throw e;
        }
        
        // If the file is image, recognize it and save results.
        if (contentType.contains("image")) {
            // Database connection.
            JdbcCURD curd=new JdbcCURD(); // Connect to database.
            String sql = null;
            
            // Insert image input information.
            SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
            String input_time = sdf.format(event.getRecords().get(0).getEventTime().toDate());
            int image_id, user_id = 0;
            sql = String.format("INSERT INTO `images` (`image_name`, `input_time`, `user_id`) "
                    + "VALUES ('%s', '%s', '%s');", key, input_time, user_id);    // INSERT INTO `images` (`id`, `image_name`, `input_time`, `user_id`) VALUES (NULL, NULL, NULL, '0');
            image_id = curd.addElement(sql);
            
            // Get image labels, ignore if not image.
            String result = "0";
            context.getLogger().log("Try to read image labels: " + bucket + key);
            result = DetectLabels.rekogImage(bucket, key, context);
            context.getLogger().log("Read image labels result: " + result);
            
            
            // Insert label result to AWS RDS database.
            String platform = "aws";
            JSONObject resultJson = new JSONObject(result);
            Set<String> labelSet = resultJson.keySet();
            for (String label : labelSet) {
                Double confidence = resultJson.getDouble(label);
                // INSERT INTO `image_labels` (`id`, `input_time`, `image_name`, `label`, `confidence`, `platform`) VALUES ('1', '9/20/2017 22:13:36', 'salad.jpeg', 'Salad', '95.759926', 'aws');
                sql = String.format("INSERT INTO `image_labels` (`image_id`, `image_name`, `label`, `confidence`, `platform`) "
                        + "VALUES ('%s', '%s', '%s', '%s', '%s');", image_id, key, label, confidence, platform);
                curd.addElement(sql);
            }
            
            // TODO
            // Assign an random score, simulation of grading algorithm
            double score = Math.random() * 90 + 10;
            sql = String.format("UPDATE `images` SET `score` = '%s' WHERE `id` = '%s'", score, image_id); // UPDATE `images` SET `score` = '5' WHERE `id` = '2';
            curd.addElement(sql);
            
            
        } else {
            context.getLogger().log("This file is not a image, ignore it.");
        }
        
        return contentType;
    }
    
//    public static void insertResult(String result) {
//     // Insert label result to AWS RDS database.
//        JdbcCURD curd=new JdbcCURD(); 
//        
//        String sql = null;
//        String input_time = null;
//        String image_name = null;
//        String platform = "aws";
//        
//        JSONObject resultJson = new JSONObject(result);
//        Set<String> labelSet = resultJson.keySet();
//        for (String label : labelSet) {
//            Double confidence = resultJson.getDouble(label);
//            
//            // /*INSERT INTO `image_labels` (`id`, `input_time`, `image_name`, `label`, `confidence`, `platform`) VALUES ('1', '9/20/2017 22:13:36', 'salad.jpeg', 'Salad', '95.759926', 'aws');
//            sql = String.format("INSERT INTO `image_labels` (`input_time`, `image_name`, `label`, `confidence`, `platform`) "
//                    + "VALUES ('%s', '%s', '%s', '%s', '%s');", input_time, image_name, label, confidence, platform);
//            curd.addElement(sql);
//        }
//    }
}