# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Air Quality Monitoring and Analysis System - A full-stack data pipeline application for processing, analyzing, and visualizing air quality data across Chinese cities. The system combines batch processing (PySpark), real-time streaming (Kafka + Flink), and web visualization (Django).

## Architecture

### Three-Layer Data Pipeline

1. **Batch Processing Layer** (PySpark)
   - `/sparks/sparkFir.py` - Initial data ingestion from CSV to MySQL
   - `/sparks/sparkSql.py` - Batch analysis writing to MySQL
   - `/sparks/sparkHive.py` - Analysis results writing to Hive

2. **Real-time Streaming Layer** (Kafka + Flink)
   - `/time/producer.py` - Python Kafka producer reading from MySQL `nine` table, publishing to `aqi_topic`
   - `/airflink/src/main/java/com/crayler/KafkaToMySQLJob.java` - Flink job consuming from Kafka, writing to MySQL `aqi_result` table

3. **Web Presentation Layer** (Django)
   - `/myApp/views.py` - Core request handlers and database queries
   - `/myApp/models.py` - ORM models mapping to MySQL tables
   - `/templates/` - Frontend HTML pages with data visualizations

### Database Schema (MySQL)

Primary tables:
- `airdata` - Main air quality data (city, date, AQI, PM2.5, PM10, So2, No2, Co, O3)
- `user` - User authentication
- `rank_day_data` - City ranking by excellent air quality days
- `year_data` - Monthly aggregated PM2.5/PM10 averages by city
- `o3_category_data` / `co_category_data` - Pollutant category statistics
- `nine` - Staging table for real-time processing (producer reads from here)
- `aqi_result` - Real-time AQI results (Flink writes here)

### Key Technology Integration

**Database Configuration**: All components connect to MySQL at IP address specified in:
- Django: `air/settings.py:78-84` (host: `192.168.1.7`)
- PySpark jobs: hardcoded connection strings
- Kafka producer: `time/producer.py:17-24`
- Flink job: `KafkaToMySQLJob.java:53-55`

**IMPORTANT**: When switching environments (lab vs dorm), update the database IP address in ALL these locations. Common IPs: `172.20.10.2` (lab), `192.168.31.15` (dorm), `192.168.1.7` (current).

## Development Commands

### Django Web Server
```bash
# Start development server
python3 manage.py runserver 0.0.0.0:8000

# Database migrations
python3 manage.py makemigrations
python3 manage.py migrate

# Create admin user
python3 manage.py createsuperuser
# Default credentials: crayler / 12345678
```

### PySpark Data Processing
```bash
# Run in this order for initial data setup:
cd /root/code/air/sparks
python3 sparkFir.py      # Load raw CSV data into MySQL
python3 sparkSql.py      # Generate analysis tables in MySQL
python3 sparkHive.py     # Generate analysis tables in Hive
```

### Real-time Streaming Pipeline

**Prerequisites** (start in this order):
```bash
# 1. Start MySQL
service mysqld start
systemctl status mysqld

# 2. Start Zookeeper
cd /opt/kafka_2.12-3.4.1/
./bin/zookeeper-server-start.sh ./config/zookeeper.properties

# 3. Clear Kafka data and start Kafka
rm -rf /opt/kafka-data/*
cd /opt/kafka_2.12-3.4.1/
./bin/kafka-server-start.sh ./config/server.properties
```

**Start streaming pipeline**:
```bash
# 4. Start Python Kafka producer (publishes AQI data)
cd /root/code/air/time
python3 producer.py

# 5. Run Flink consumer job (consumes and writes to MySQL)
cd /root/code/air/airflink
# Either run in IDE or:
mvn clean package -DskipTests
java -jar target/flink-kafka-mysql-demo-1.0-SNAPSHOT.jar
```

**Optional monitoring**:
```bash
# Monitor Kafka topic
cd /opt/kafka_2.12-3.4.1/
./bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic aqi_topic --from-beginning
```

### Java/Maven (Flink)
```bash
cd /root/code/air/airflink

# Build
mvn clean package -DskipTests

# Run packaged JAR
java -jar target/flink-kafka-mysql-demo-1.0-SNAPSHOT.jar
```

## Code Patterns and Conventions

### Django Views Pattern
Views follow a consistent pattern:
1. Query database using ORM models from `myApp/models.py`
2. Process/transform data as needed
3. Pass data to template via context dictionary
4. Template renders using data for charts/tables

Example: `myApp/views.py:21-38` (gas view)

### PySpark Analysis Pattern
All PySpark scripts follow:
1. Create SparkSession with MySQL JDBC driver (`/opt/spark/jars/mysql-connector-j-8.0.33.jar`)
2. Define connection properties (user: root, password: 12345678)
3. Read from MySQL `airdata` table
4. Apply transformations/aggregations using Spark SQL
5. Write results back to MySQL or Hive

### Kafka Producer Polling Pattern
The producer in `time/producer.py` uses a continuous polling mechanism:
1. Query `nine` table for unprocessed records (`processed = 0`)
2. Publish to Kafka topic `aqi_topic`
3. Mark records as processed (`processed = 1`)
4. When no new data, reset all records to unprocessed (creates a loop)
5. Sleep 5 seconds between polls

### Flink Sink Pattern
The Flink job implements `RichSinkFunction` for MySQL writes:
- Opens JDBC connection in `open()` method
- Processes each Kafka message in `invoke()` method
- Deletes existing city data before inserting (upsert pattern)
- Formats AQI to 2 decimal places before insertion

## Important Notes

### Environment-Specific Configuration
- Database host IP hardcoded in multiple locations - must be updated when changing environments
- No environment variables or config files for database credentials
- All passwords hardcoded as `12345678` (development only)

### Django Settings
- `DEBUG = True` - Development mode enabled
- `ALLOWED_HOSTS = ['*']` - Accepts all hosts
- Language: `zh-hans` (Simplified Chinese)
- Timezone: `Asia/Shanghai`
- CommonMiddleware is commented out at `air/settings.py:47`

### Data Flow
1. Raw data starts in `/sparks/data_new.csv`
2. `sparkFir.py` loads into `airdata` table
3. `sparkSql.py` and `sparkHive.py` create analysis tables
4. Producer reads from `nine` table continuously
5. Flink processes Kafka stream and writes to `aqi_result`
6. Django queries various tables for real-time and historical views

### URL Routes
All application URLs are defined in `myApp/urls.py`:
- `/myApp/index/` - Homepage
- `/myApp/login/` - Login page
- `/myApp/realtime/` - Real-time monitoring
- `/myApp/predict/` - AQI prediction
- `/myApp/rank/` - City rankings
- `/myApp/year/` - Annual analysis
- `/myApp/gas/` - O3/CO pollutant analysis
- `/myApp/table/` - Data overview table
- `/myApp/AI/` - AI features page

## Dependencies

### Python
```bash
pip3 install pyspark pandas requests BeautifulSoup4 Django mysqlclient kafka-python pymysql
```

### System
```bash
dnf install mariadb-connector-c-devel gcc redhat-rpm-config python3-devel java-11-openjdk-devel
```

### Java
- Java 11
- Maven for building Flink application
- Dependencies managed in `airflink/pom.xml`

## Runtime Environment
- CentOS 8.0
- Python 3.6 (though code may work with 3.11 based on `__pycache__` presence)
- Java 11
- Django 5.2.3 (note: readme.md states 3.2 but settings.py shows 5.2.3)
- Spark 3.5.6
- Hadoop 3.4.1
- Kafka 2.12-3.4.1
- Flink 1.16.1
