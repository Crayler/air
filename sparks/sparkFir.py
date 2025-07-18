from pyspark.sql import SparkSession
import pandas as pd
from pyspark.sql.types import StructType,IntegerType,StringType,FloatType
from pyspark.sql.functions import monotonically_increasing_id

# Create a SparkSession
spark  = SparkSession.builder.config("spark.jars", "/opt/spark/jars/mysql-connector-j-8.0.33.jar") \
                .master("local").appName("PySpark_MySQL").getOrCreate()

connectionProperties = {
    "user": "root",
    "password": "12345678",
    "driver": "com.mysql.cj.jdbc.Driver"
}

# Read the data from the MySQL table
schema = StructType().add("city",StringType(),nullable=True).\
        add("date",StringType(),nullable=True). \
        add("airQuality",StringType(),nullable=True). \
        add("AQI",StringType(),nullable=True). \
        add("rank",IntegerType(),nullable=True).\
        add("PM",IntegerType(),nullable=True). \
        add("PM10",IntegerType(),nullable=True). \
        add("So2",IntegerType(),nullable=True). \
        add("No2",IntegerType(),nullable=True). \
        add("Co",FloatType(),nullable=True). \
        add("O3",IntegerType(),nullable=True)

df = spark.read.format("csv").\
    option("sep",",").\
    option("header","true").\
    option("encoding","utf-8").\
    schema(schema=schema).\
    load("/root/code/air/sparks/data.csv")

df = df.withColumn("id",monotonically_increasing_id())

#数据去重
# df = df.drop_duplicates()

# #处理空值
# df = df.na.drop()

# Show the data in the DataFrame

df.write.jdbc(url="jdbc:mysql://192.168.31.15:3306/airdata"
                "?user=root&password=12345678&useUnicode=true&characterEncoding=UTF-8",
            mode="overwrite",
            table="airdata",
            properties={"driver": 'com.mysql.cj.jdbc.Driver'})
df.write.mode("overwrite").format("parquet").saveAsTable("airdata")
spark.sql("select * from airdata").show()
