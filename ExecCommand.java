package com.amazonaws.lambda.image;

import java.io.BufferedReader;
import java.io.InputStreamReader;

import com.amazonaws.services.lambda.runtime.Context;

public class ExecCommand {
    
    public static String execCommand(String commandLine, Context context) {
        context.getLogger().log("Executing: " + commandLine);
        StringBuffer output = new StringBuffer();
        
        try {
            Process p = Runtime.getRuntime().exec(commandLine);
            p.waitFor();
            
            BufferedReader reader = new BufferedReader(new InputStreamReader(p.getInputStream()));
            String line = "";
            while ((line = reader.readLine()) != null) {
                output.append(line + "\n");
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        context.getLogger().log("Command output: " + output.toString());

        return output.toString();
    }
}