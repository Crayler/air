-- Kafka 源表
CREATE TABLE source_kafka (
    city STRING,
    `year` INT,
    `month` INT,
    month_AQI DOUBLE,
    `ts` AS PROCTIME()
) WITH (
    'connector' = 'kafka',
    'topic' = 'aqi_topic',
    'properties.bootstrap.servers' = 'localhost:9092',
    'scan.startup.mode' = 'earliest-offset',
    'format' = 'json'
);

-- MySQL 目标表
CREATE TABLE sink_mysql (
    city STRING,
    `year` INT,
    `month` INT,
    avg_month_AQI DOUBLE,
    PRIMARY KEY (city, `year`, `month`) NOT ENFORCED
) WITH (
    'connector' = 'jdbc',
    'url' = 'jdbc:mysql://192.168.31.15:3306/airdata',
    'table-name' = 'aqi_result',
    'username' = 'root',
    'password' = '12345678'
);

-- 实时聚合写入 MySQL
INSERT INTO sink_mysql
SELECT
    city,
    `year`,
    `month`,
    AVG(month_AQI) AS avg_month_AQI
FROM source_kafka
GROUP BY city, `year`, `month`;
