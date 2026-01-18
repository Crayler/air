from pyspark.sql import SparkSession
from pyspark.sql.functions import row_number,mean,when, col,lit, to_date, year, max, min, count, desc, month, avg, lag,monotonically_increasing_id
from pyspark.sql.window import Window

# 初始化SparkSession
spark = SparkSession.builder \
    .config("spark.jars", "/opt/spark/jars/mysql-connector-j-8.0.33.jar") \
    .master("local") \
    .appName("AirQualityAnalysis") \
    .getOrCreate()

mysql_url="jdbc:mysql://192.168.1.7:3306/airdata",
# 数据库连接属性
connectionProperties = {
    "user": "root",
    "password": "12345678",
    "driver": "com.mysql.cj.jdbc.Driver"
}

# 从MySQL中读取数据
df = spark.read.jdbc(
    url=mysql_url,
    table="airdata",
    properties=connectionProperties
)


# 需求分析4:年度空气质量分析（各城市分年月的 PM/PM10 均值（加自增 ID)）
result4 = df.groupBy(
    "city",
    year("date").alias("year"),
    month("date").alias("month")
).agg(
    avg("PM").alias("max_PM"),
    avg("PM10").alias("min_PM10")
)

# 添加自增 id
window = Window.orderBy("city", "year", "month")
result4 = result4.withColumn("id", row_number().over(window))

# 写入分析结果到数据库
result4.write.jdbc(
    url=mysql_url,
    table="year_data",
    mode="overwrite",
    properties=connectionProperties
)



# 需求分析5:各城市分年月 AQI<50 的天数（优级天数）
result5 = df.groupBy("city",year("date").alias("year"),month("date").alias("month")) \
    .agg(
        count(when(df["AQI"]<50,True).alias("greatAir")).alias("count_grate")
    )

# 写入分析结果到数据库
result5.write.jdbc(
    url=mysql_url,
    table="rank_day_data",
    mode="overwrite",
    properties=connectionProperties
)

# 需求分析7:CO 浓度分类统计（按区间计数）
df = df.withColumn(
    "Co_category",
    when((col("Co") >= 0) & (col("Co") < 0.25), '0-0.25')
    .when((col("Co") >= 0.25) & (col("Co") < 0.5), '0.25-0.5')
    .when((col("Co") >= 0.5) & (col("Co") < 0.75), '0.5-0.75')
    .when((col("Co") >= 0.75) & (col("Co") < 1), '0.75-1')
    .otherwise("1以上")
)

result7 = df.groupBy("Co_category").agg(count('*').alias('Co_count'))

# 添加自增 id
window = Window.orderBy("Co_category")
result7 = result7.withColumn("id", row_number().over(window))

# 写入分析结果到数据库
result7.write.jdbc(
    url=mysql_url,
    table="co_category_data",
    mode="overwrite",
    properties=connectionProperties
)


# 需求分析8: O3浓度分类统计（同 CO 逻辑）
df = df.withColumn(
    "O3_category",
    when((col("O3") >= 0) & (col("O3") < 25), '0-25')
    .when((col("O3") >= 25) & (col("O3") < 50), '25-50')
    .when((col("O3") >= 50) & (col("O3") < 75), '50-75')
    .when((col("O3") >= 75) & (col("O3") < 100), '75-100')
    .otherwise("100以上")
)

result8 = df.groupBy("O3_category").agg(count('*').alias('O3_count'))

# 添加自增id列
window = Window.orderBy("O3_category")  # 可以按分类列排序
result8 = result8.withColumn("id", row_number().over(window))

# 写入MySQL
result8.write.jdbc(
    url=mysql_url,
    table="o3_category_data",
    mode="overwrite",
    properties=connectionProperties
)


# 需求分析9:各城市分年月的 AQI 均值（加标识列）
result9 = df.groupBy(
    "city",
    year("date").alias("year"),
    month("date").alias("month")
).agg(
    avg('AQI').alias('month_AQI')
)

# 添加自增id列
window = Window.orderBy("city", "year", "month")
result9 = result9.withColumn("id", row_number().over(window))
result9 = result9.withColumn("processed", lit(0))
# 写入 MySQL
result9.write.jdbc(
    url=mysql_url,
    table="nine",
    mode="overwrite",
    properties=connectionProperties
)


# 需求分析10：各城市空气质量排名趋势分析
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
    url=mysql_url,
    table="rank_analysis",
    mode="overwrite",
    properties=connectionProperties
)