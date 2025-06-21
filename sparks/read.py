from pyspark.sql import SQLContext, SparkSession

if __name__ == '__main__':
    # spark 初始化
    spark = SparkSession. \
        Builder(). \
        appName('sql'). \
        master('local'). \
        getOrCreate()
    # mysql 配置(需要修改)
    prop = {'user': 'root', 
            'password': '12345678', 
            'driver': 'com.mysql.cj.jdbc.Driver'}
    # database 地址(需要修改)
    url = 'jdbc:mysql://192.168.31.15:3306/airdata'
    # 读取表
    data = spark.read.jdbc(url=url, table='django_migrations', properties=prop)
    # 打印data数据类型
    print(type(data))
    # 展示数据
    data.show()
    # 关闭spark会话
    spark.stop()