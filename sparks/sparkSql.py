from pyspark.sql import SparkSession
from pyspark.sql.functions import row_number,mean,when, col, to_date, year, max, min, count, desc, month, avg, lag,monotonically_increasing_id
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



# 需求分析1：城市平均AQI
result1 = df.groupBy("city")\
    .agg(mean("AQI").alias("avg_AQI"))\
    .orderBy("avg_AQI",ascending=False)

# 写入分析结果到数据库
result1.write.jdbc(
    url="jdbc:mysql://192.168.31.15:3306/airdata",
    table="one",
    mode="overwrite",
    properties=connectionProperties
)



# 需求分析2：个气体
result2 = df.groupBy("city")\
    .agg(
        mean("PM").alias("avg_PM"),
        mean("PM10").alias("avg_PM10"),
        mean("So2").alias("avg_So2"),
        mean("No2").alias("avg_No2"),
        mean("Co").alias("avg_Co"),
        mean("O3").alias("O3"),
        )

# 写入分析结果到数据库
result2.write.jdbc(
    url="jdbc:mysql://192.168.31.15:3306/airdata",
    table="two",
    mode="overwrite",
    properties=connectionProperties
)

# 需求分析3:年度空气质量分析
df = df.withColumn("date", df["date"].cast("date"))
result3 = df.groupBy("city",year("date").alias("year"),month("date").alias("month")) \
    .agg(
        max("AQI").alias("max_AQI"),
        min("AQI").alias("min_AQI")
    )

# 写入分析结果到数据库
result3.write.jdbc(
    url="jdbc:mysql://192.168.31.15:3306/airdata",
    table="three",
    mode="overwrite",
    properties=connectionProperties
)


# 需求分析4:年度空气质量分析
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
    url="jdbc:mysql://192.168.31.15:3306/airdata",
    table="four",
    mode="overwrite",
    properties=connectionProperties
)



# 需求分析5:
result5 = df.groupBy("city",year("date").alias("year"),month("date").alias("month")) \
    .agg(
        count(when(df["AQI"]<50,True).alias("greatAir")).alias("count_grate")
    )

# 写入分析结果到数据库
result5.write.jdbc(
    url="jdbc:mysql://192.168.31.15:3306/airdata",
    table="five",
    mode="overwrite",
    properties=connectionProperties
)



# 需求分析6:
result6 = df.groupBy("city") \
    .agg(
        max("So2").alias("max_So2"),
        max("No2").alias("max_No2")
    )

# 写入分析结果到数据库
result6.write.jdbc(
    url="jdbc:mysql://192.168.31.15:3306/airdata",
    table="six",
    mode="overwrite",
    properties=connectionProperties
)


# 需求分析7:
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
    url="jdbc:mysql://192.168.31.15:3306/airdata",
    table="seven",
    mode="overwrite",
    properties=connectionProperties
)


# 需求分析8:
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
    url="jdbc:mysql://192.168.31.15:3306/airdata",
    table="eight",
    mode="overwrite",
    properties=connectionProperties
)


# 需求分析9:
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

# 写入 MySQL
result9.write.jdbc(
    url="jdbc:mysql://192.168.31.15:3306/airdata",
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
    url="jdbc:mysql://192.168.31.15:3306/airdata",
    table="rank_analysis",
    mode="overwrite",
    properties=connectionProperties
)