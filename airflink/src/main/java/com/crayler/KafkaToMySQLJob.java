package com.crayler;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer;
import org.apache.flink.streaming.api.datastream.DataStreamSource;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.streaming.api.functions.sink.RichSinkFunction;
import org.apache.flink.configuration.Configuration;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;

public class KafkaToMySQLJob {

    public static void main(String[] args) throws Exception {
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        // Kafka Source
        KafkaSource<String> source = KafkaSource.<String>builder()
                .setBootstrapServers("localhost:9092")
                .setTopics("aqi_topic")
                .setGroupId("my-group")
                .setStartingOffsets(OffsetsInitializer.earliest())
                .setValueOnlyDeserializer(new SimpleStringSchema())
                .build();

        DataStreamSource<String> stream = env.fromSource(
                source,
                WatermarkStrategy.noWatermarks(),
                "Kafka Source");

        stream.print();

        stream.addSink(new MySQLSink());

        env.execute("Flink1.16.1 Kafka→MySQL");
    }

    public static class MySQLSink extends RichSinkFunction<String> {
        private Connection conn;
        private PreparedStatement ps;
        private ObjectMapper objectMapper;

        @Override
        public void open(Configuration parameters) throws Exception {
            super.open(parameters);
            Class.forName("com.mysql.cj.jdbc.Driver");
            conn = DriverManager.getConnection(
                    "jdbc:mysql://192.168.1.10:3306/airdata?useSSL=false&serverTimezone=UTC",
                    "root", "12345678");
            ps = conn.prepareStatement(
                    "INSERT INTO aqi_result (city, year, month, avg_month_AQI, updatetime) VALUES (?, ?, ?, ?, ?)");
            objectMapper = new ObjectMapper();
        }

        @Override
        public void invoke(String value, Context ctx) throws Exception {
            try {
                JsonNode jsonNode = objectMapper.readTree(value);
                String city = jsonNode.get("city").asText();
                int year = jsonNode.get("year").asInt();
                int month = jsonNode.get("month").asInt();
                double monthAQI = jsonNode.get("month_AQI").asDouble();
                String formattedAQI = String.format("%.2f", monthAQI);
                double roundedAQI = Double.parseDouble(formattedAQI);
                String updatetime = jsonNode.get("updatetime").asText();
                
                // 每条都删除（性能不佳，慎用）
                try (PreparedStatement deleteStmt = conn.prepareStatement("DELETE FROM aqi_result WHERE city = ?")) {
                    deleteStmt.setString(1, city);
                    deleteStmt.executeUpdate();
                }

                // 插入新数据
                ps.setString(1, city);
                ps.setInt(2, year);
                ps.setInt(3, month);
                ps.setDouble(4, roundedAQI);
                ps.setString(5, updatetime);
                ps.executeUpdate();

            } catch (Exception e) {
                e.printStackTrace();
            }
        }

        @Override
        public void close() throws Exception {
            super.close();
            if (ps != null)
                ps.close();
            if (conn != null)
                conn.close();
        }
    }
}
