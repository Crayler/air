from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler, OneHotEncoder, StringIndexer
from pyspark.ml.regression import RandomForestRegressor
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml import Pipeline

# 1. SparkSession
spark = SparkSession.builder.appName("AirQuality_RF_by_city").getOrCreate()

# 2. 读数据
data = spark.read.csv("/root/code/air/sparks/data.csv", header=True, inferSchema=True)
data.show(5)
data.printSchema()

# 3. 索引和编码
indexer = StringIndexer(inputCol='city', outputCol='city_index')
encoder = OneHotEncoder(inputCol='city_index', outputCol='city_encoded')

# 4. 特征列
feature_cols = ['PM', 'PM10', 'So2', 'No2', 'Co', 'O3', 'city_encoded']
assembler = VectorAssembler(inputCols=feature_cols, outputCol='features')

pipeline = Pipeline(stages=[indexer, encoder, assembler])

# ⚠️ 保留原始 city 列
data_prepared = pipeline.fit(data).transform(data).select('features', 'AQI', 'city')

# 5. 划分
train_data, test_data = data_prepared.randomSplit([0.8, 0.2], seed=42)

# 6. 随机森林
rf = RandomForestRegressor(labelCol='AQI', featuresCol='features', numTrees=100)
model = rf.fit(train_data)

# 7. 预测
predictions = model.transform(test_data)

# ⚠️ 保留 city 列一起输出
predictions.select('city', 'AQI', 'prediction').show(10)

# 8. 评估
evaluator = RegressionEvaluator(labelCol='AQI', predictionCol='prediction', metricName='rmse')
rmse = evaluator.evaluate(predictions)
print(f"RMSE: {rmse}")

# 9. 保存
predictions.select('city', 'AQI', 'prediction').toPandas().to_csv("prediction.csv", index=False)

spark.stop()
