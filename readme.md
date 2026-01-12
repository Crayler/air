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
    cd /opt/kafka_2.12-3.4.1/ 
    ./bin/zookeeper-server-start.sh ./config/zookeeper.properties

2、启动Kafka服务
    cd  /opt/kafka_2.12-3.4.1/
    ./bin/kafka-server-start.sh ./config/server.properties

要先删除kafka-data
[root@xi001 opt]# rm -rf kafka-data/

  启动kafka消费者
    bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic aqi_topic --from-beginning

<!-- 启动flink
  cd /opt/flink-1.16.1
  ./bin/start-cluster.sh
  ./bin/sql-client.sh embedded -f /root/code/air/time/flink.sql -d -->

```
进入到time 启动 python3 producer.py
进入到airflink 启动 java
# 页面效果
## 注册页面
<img width="502" height="254" alt="image" src="https://github.com/user-attachments/assets/1febf8a0-b27a-4378-bfc0-d4622dc38394" />

## 登录页面
<img width="510" height="259" alt="image" src="https://github.com/user-attachments/assets/a16b3ce0-1594-4036-8b4b-ea35387c100e" />

## 首页
<img width="555" height="282" alt="image" src="https://github.com/user-attachments/assets/074beb0d-4d26-4d87-b512-79fe9dcd43e6" />

## 数据概览页面
<img width="555" height="282" alt="image" src="https://github.com/user-attachments/assets/be7a0f7c-be10-49c1-99e5-b11e6dc9276b" />

## 城市空气质量排行页面
<img width="502" height="254" alt="image" src="https://github.com/user-attachments/assets/b1554408-d238-4d66-b755-87d524843f5b" />

## O3 与 CO 污染物分类统计页面
<img width="476" height="242" alt="image" src="https://github.com/user-attachments/assets/18870b77-a080-4014-b48e-c040bf676823" />

## 年度污染分析页面
<img width="555" height="282" alt="image" src="https://github.com/user-attachments/assets/6f112e01-f3f8-4f8d-931b-88c8be6243b8" />

## 实时监控页面
<img width="555" height="282" alt="image" src="https://github.com/user-attachments/assets/9e6bfce5-36ec-48a4-a1ed-011e798fea9f" />

## 预测页面
<img width="555" height="282" alt="image" src="https://github.com/user-attachments/assets/69587e12-386a-422d-8d63-0e69d7a0af7b" />


## 启动步骤


根据位置要修改数据库IP地址
实验楼：172.20.10.2
寝室：192.168.31.15

---

1、**不用启动** hadoop 启动 已经配置了环境变量，任意地方可以启动

```bash
start-all.sh
```

2、启动 mysql 服务
```bash
service mysqld start
systemctl status mysqld
```

3、**不用启动** 启动hive

```bash
  hive --service metastore
  hiveserver2
  hive
    或者(!connect jdbc:hive2://192.168.100.100:10000/default
    用户名hive  密码123456)
```

4、启动Zookeeper服务

```bash
cd /opt/kafka_2.12-3.4.1/ 
./bin/zookeeper-server-start.sh ./config/zookeeper.properties
```

5、要先删除 kafka-data

```bash
rm -rf /opt/kafka-data/*

# 启动Kafka服务
cd /opt/kafka_2.12-3.4.1/
./bin/kafka-server-start.sh ./config/server.properties
```

6、django 启动命令

```bash
python3 manage.py runserver 0.0.0.0:8000
```

7、启用实时更新数据：进入到 time 启动

```bash
python3 producer.py
```

8.运行KafkaToMySQLJob.java程序  右键KafkaToMySQLJob.java 点击run 或者打包运行

```bash
cd /root/code/air/airflink/
mvn clean package -DskipTests
java -jar target/flink-kafka-mysql-demo-1.0-SNAPSHOT.jar 
```

# 项目结构
## 数据爬取
  爬取数据的代码：/spiders/spiderAQL.py 
  爬取的数据：data_new.csv
## 数据清洗
  /sparks/sparkHive.py 分析的数据写入hive
  /sparks/sparkSql.py  分析的数据写入navicate
  /sparks/sparkFir.py  爬取的初始数据写入数据库

## 
 /myApp/models.py 核心作用是将 MySQL 数据库中的表（如 user、five、year_data、eight、seven、airdata）映射为 Python 类，通过 Django 的 ORM（对象关系映射）语法便捷地操作数据库，无需编写原生 SQL。
 /myApp/views.py 核心功能是处理用户请求（登录 / 注册 / 退出）、读取数据库中的空气质量分析数据，并将数据传递给前端模板渲染页面
 /myApp/templates/air.html
 /myApp/templates/gas.html   O3 与 CO 污染物分类统计页面
 /myApp/templates/register.html 注册页面
 /myApp/templates/login.html 登录页面
 /myApp/templates/logout.html 登出页面
 /myApp/templates/index.html首页
 /myApp/templates/table.html 数据概览表页面
 /myApp/templates/rank.html 城市空气质量排行页面
 /myApp/templates/realtime.html 实时页面
  /myApp/templates/predict.html 预测页面
 /myApp/templates/year.html 年度污染分析页面
