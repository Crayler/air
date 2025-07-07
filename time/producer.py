# producer.py
# pip install kafka-python pymysql

from kafka import KafkaProducer
import pymysql
import json
import time
import datetime

# 创建 Kafka Producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# 数据库连接配置
DB_CONFIG = {
    'host': '192.168.31.15',
    'user': 'root',
    'password': '12345678',
    'db': 'airdata',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

while True:
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 查询未处理的数据
    cursor.execute("SELECT id, city, year, month, month_AQI FROM nine WHERE processed = 0 LIMIT 10")
    rows = cursor.fetchall()

    if not rows:
        print("没有新数据，等待中...")
        # 如果没有新数据，重置所有已处理的数据标记
        cursor.execute("UPDATE nine SET processed = 0")
        conn.commit()
        print("已重置所有数据标记为未处理")
    else:
        for row in rows:
            # 发送到 Kafka
            updatetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            row['updatetime'] = updatetime
            producer.send('aqi_topic', row)
            print('Produced:', row)
            # 标记为已处理
            cursor.execute("UPDATE nine SET processed = 1 WHERE id = %s", (row['id'],))
        conn.commit()

    cursor.close()
    conn.close()

    time.sleep(10)  # 每 5 秒轮询一次
