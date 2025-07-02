from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, year, max, min, count, desc, month, avg, lag
from pyspark.sql.window import Window

# 初始化SparkSession
spark = SparkSession.builder \
    .config("spark.jars", "/opt/spark/jars/mysql-connector-j-8.0.33.jar") \
    .master("local") \
    .appName("AirQualityAnalysis") \
    .getOrCreate()

# 数据库连接属性
connectionProperties = {
    "user": "root",
    "password": "12345678",
    "driver": "com.mysql.cj.jdbc.Driver"
}

# 从MySQL中读取数据
df = spark.read.jdbc(
    url="jdbc:mysql://192.168.31.15:3306/airdata",
    table="airdata",
    properties=connectionProperties
)

# 数据预处理
df = df.withColumn("date", to_date(col("data"), "yyyy-MM-dd"))


# 需求分析1：各城市空气质量排名趋势分析
rank_trend = df.select("city", "date", "rank").orderBy("city", "date")
windowSpec = Window.partitionBy("city").orderBy("date")
rank_trend = rank_trend.withColumn("prev_rank", lag("rank").over(windowSpec))
rank_trend = rank_trend.withColumn("rank_change", col("prev_rank").cast("int") - col("rank").cast("int"))
# 填充DataFrame中的null值
rank_trend = rank_trend.fillna({
    "prev_rank": 0,
    "rank_change": 0
})
# 注册为临时视图
rank_trend.createOrReplaceTempView("rank_analysis")

# 写入分析结果到数据库
rank_trend.write.jdbc(
    url="jdbc:mysql://192.168.31.15:3306/airdata",
    table="rank_analysis",
    mode="overwrite",
    properties=connectionProperties
)

# 查询临时视图
spark.sql("SELECT * FROM rank_analysis").show()



# 需求分析2：空气质量等级城市分布分析
quality_dist = df.groupBy("city", "airQuality").agg(count("*").alias("count"))
quality_dist = quality_dist.orderBy("city", desc("count"))

# 注册为临时视图
quality_dist.createOrReplaceTempView("quality_dist_analysis")

# 写入分析结果到数据库
quality_dist.write.jdbc(
    url="jdbc:mysql://192.168.31.15:3306/airdata",
    table="quality_dist_analysis",
    mode="overwrite",
    properties=connectionProperties
)

# 查询临时视图
spark.sql("SELECT * FROM quality_dist_analysis").show()



# 需求分析3：季节性空气质量变化规律分析
df = df.withColumn("month", month("date"))
monthly_avg = df.groupBy("month") \
    .agg(
        avg("PM").alias("avg_PM"),
        avg("PM10").alias("avg_PM10"),
        avg("So2").alias("avg_So2"),
        avg("No2").alias("avg_No2"),
        avg("Co").alias("avg_Co"),
        avg("O3").alias("avg_O3")
    ).orderBy("month")

# 注册为临时视图
monthly_avg.createOrReplaceTempView("monthly_avg_analysis")

# 写入分析结果到数据库
monthly_avg.write.jdbc(
    url="jdbc:mysql://192.168.31.15:3306/airdata",
    table="monthly_avg_analysis",
    mode="overwrite",
    properties=connectionProperties
)

# 查询临时视图
spark.sql("SELECT * FROM monthly_avg_analysis").show()




# 需求分析4：年度空气质量分析
df = df.withColumn("year", year(col("date")))
year_max = df.groupBy("city", year("date").alias("year"), month("date").alias("month")) \
    .agg(
        max("AQI").alias("max_AQI"),
        min("AQI").alias("min_AQI"),
    )

# 注册为临时视图
year_max.createOrReplaceTempView("year_quality")

# 写入数据库
year_max.write.jdbc(
    url="jdbc:mysql://192.168.31.15:3306/airdata",
    table="year_quality",
    mode="overwrite",
    properties=connectionProperties
)

# 查询临时视图
spark.sql("SELECT * FROM year_quality").show()

# 关闭SparkSession
spark.stop()