package com.amazonaws.lambda.image;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

public class JdbcCURD {

    private Connection connection;
    private Statement statement;
    private ResultSet resultSet;

    public int update(String sql) {
        int autoGenerateId = 0;
        try {
            connection = JdbcUtils.getConnection();
            statement = connection.createStatement();
            statement.executeUpdate(sql, Statement.RETURN_GENERATED_KEYS);
            ResultSet execResult = statement.getGeneratedKeys();
            if (execResult.next()) {
                autoGenerateId = execResult.getInt(1);
            }
        } catch (SQLException e) {
            e.printStackTrace();
            autoGenerateId = -1;
        } finally {
            JdbcUtils.releaseResources(resultSet, statement, connection);
        }
        return autoGenerateId;
    }
    
    public void Query(String sql) {
        try {
            connection = JdbcUtils.getConnection();
            statement = connection.createStatement();
            resultSet = statement.executeQuery(sql);
            
            while(resultSet.next()){
                System.out.println("name:"+resultSet.getString("name"));
                System.out.println("id:"+resultSet.getString("Tid"));
            }
            
        } catch (SQLException e) {
            e.printStackTrace();
        } finally {
            JdbcUtils.releaseResources(resultSet, statement, connection);
        }
    }
    
    public int addElement(String sql) {
        return update(sql);
    }
    
    public void removeElement(String sql) {
        update(sql);
    }

    public void createTable(String sql){
        update(sql);
    }
    
    public void dropTable(String sql){
        update(sql);
    }

}