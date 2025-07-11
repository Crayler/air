# PySpark

## 运行环境

  - CentOS 8.0
  - Python 3.6
  - Java 11
  - Django 3.2
  - Spark 3.5.6
  - Hadoop 3.4.1
  - pyspark 3.2.1

---

## 安装 Java (推荐 OpenJDK 8 或 11)

```bash
sudo dnf install java-11-openjdk-devel
```

### 设置 JAVA_HOME

```bash
sudo alternatives --config java
# 在提示中输入 2 然后回车

# 验证 Java 安装
java -version
update-alternatives --display java
```

## 安装依赖

```bash
pip3 install pyspark pandas requests BeautifulSoup4 -y
dnf install mariadb-connector-c-devel gcc
dnf install redhat-rpm-config python3-devel

pip3 install Django mysqlclient
python xxx.py
```

---

## django 启动命令

```bash
python3 manage.py runserver 0.0.0.0:8000
```

## 创建数据库

```bash
python3 manage.py makemigrations polls
python3 manage.py sqlmigrate polls 0001
python3 manage.py migrate
```

## 初试 API

```bash
python3 manage.py shell
```

## 创建一个管理员账号

```bash
python manage.py createsuperuser

crayler
12345678
```

## hadoop环境
```bash
start-all.sh
service mysqld start  启动 mysql 服务
ps -ef | grep mysql  查看mysql 服务是否启动
hive --service metastore
hiveserver2
启动hive
!connect jdbc:hive2://192.168.100.100:10000/default
用户名hive  密码123456

```

## 数据

```
python3 sparkFir.py
python3 sparkSql.py
python3 sparkHive.py


## 实时
```bash
1、启动Zookeeper服务
    cd  /opt/kafka_2.12-3.4.1/ 
    ./bin/zookeeper-server-start.sh ./config/zookeeper.properties

2、启动Kafka服务
    cd  /opt/kafka_2.12-3.4.1/
    ./bin/kafka-server-start.sh ./config/server.properties
  启动kafka消费者
    bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic aqi_topic --from-beginning

启动flink
  cd /opt/flink-1.16.1
  ./bin/start-cluster.sh
  ./bin/sql-client.sh embedded -f /root/code/air/time/flink.sql -d

```
进入到time 启动 python3 producer.py
进入到airflink 启动 java


