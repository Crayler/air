# PySpark

## 运行环境

  - CentOS 8.0
  - Python 3.6
  - Java 11
  - Django 3.2
  - Spark 3.5.6
  - Hadoop 3.4.1

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
