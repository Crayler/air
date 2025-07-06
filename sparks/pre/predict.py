import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from datetime import datetime, timedelta

# 数据库连接配置
db_config = {
    'user': 'your_username',
    'password': 'your_password',
    'host': 'your_host',
    'port': 'your_port',
    'database': 'your_database'
}

# 创建数据库连接
engine = create_engine(f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}")

try:
    # 读取数据
    query = "SELECT * FROM air_quality_data"
    df = pd.read_sql(query, engine)
    
    # 数据预处理
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    
    # 处理缺失值
    df = df.fillna(df.mean())
    
    # 特征工程
    df['month'] = df.index.month
    df['day_of_week'] = df.index.dayofweek
    
    # 可视化分析
    plt.figure(figsize=(15, 10))
    
    # 1. AQI趋势图
    plt.subplot(2, 2, 1)
    df['AQI'].plot(title='AQI趋势图')
    plt.xlabel('日期')
    plt.ylabel('AQI')
    
    # 2. 污染物相关性热图
    plt.subplot(2, 2, 2)
    pollutants = ['PM', 'PM10', 'So2', 'No2', 'Co', 'O3']
    corr_matrix = df[pollutants].corr()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm')
    plt.title('污染物相关性热图')
    
    # 3. 月度AQI分布
    plt.subplot(2, 2, 3)
    sns.boxplot(x='month', y='AQI', data=df.reset_index())
    plt.title('月度AQI分布')
    plt.xlabel('月份')
    plt.ylabel('AQI')
    
    # 4. 污染物与AQI的关系
    plt.subplot(2, 2, 4)
    for pollutant in pollutants:
        sns.regplot(x=pollutant, y='AQI', data=df, scatter_kws={'alpha': 0.3}, line_kws={'label': f'{pollutant}拟合线'})
    plt.title('污染物与AQI的关系')
    plt.xlabel('污染物浓度')
    plt.ylabel('AQI')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('air_quality_analysis.png')
    plt.close()
    
    # 预测模型 - 以预测AQI为例
    # 准备特征和目标变量
    X = df[['month', 'day_of_week'] + pollutants]
    y = df['AQI']
    
    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 训练随机森林回归模型
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # 模型评估
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f'模型评估: MSE = {mse:.2f}, R² = {r2:.2f}')
    
    # 特征重要性分析
    feature_importance = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False)
    print("\n特征重要性:")
    print(feature_importance)
    
    # 未来7天的AQI预测
    last_date = df.index.max()
    future_dates = [last_date + timedelta(days=i) for i in range(1, 8)]
    
    future_features = pd.DataFrame({
        'date': future_dates,
        'month': [date.month for date in future_dates],
        'day_of_week': [date.dayofweek for date in future_dates]
    })
    
    # 假设未来污染物浓度保持最近一周的平均水平
    recent_pollutant_avg = df[pollutants].iloc[-7:].mean()
    for pollutant in pollutants:
        future_features[pollutant] = recent_pollutant_avg[pollutant]
    
    future_features.set_index('date', inplace=True)
    
    # 进行预测
    future_predictions = model.predict(future_features)
    
    # 保存预测结果到CSV文件
    forecast_df = pd.DataFrame({
        'date': future_dates,
        'predicted_AQI': future_predictions
    })
    
    # 添加污染物预测值
    for pollutant in pollutants:
        forecast_df[pollutant] = recent_pollutant_avg[pollutant]
    
    forecast_df.to_csv('air_quality_forecast.csv', index=False)
    print("预测结果已保存到 air_quality_forecast.csv")
    
    # 绘制预测结果
    plt.figure(figsize=(12, 6))
    plt.plot(df.index[-30:], df['AQI'].iloc[-30:], label='历史数据')
    plt.plot(future_dates, future_predictions, 'r--', label='预测数据')
    plt.title('未来7天AQI预测')
    plt.xlabel('日期')
    plt.ylabel('AQI')
    plt.legend()
    plt.grid(True)
    plt.savefig('aqi_forecast.png')
    plt.close()
    
    print("\n数据分析和预测已完成，图表和预测结果已保存。")

except Exception as e:
    print(f"发生错误: {e}")
finally:
    # 关闭数据库连接
    if 'engine' in locals():
        engine.dispose()
        print("数据库连接已关闭。")    