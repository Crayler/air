import pandas as pd
from pyecharts.charts import Line, Page
from pyecharts import options as opts

# 1. 读取数据
df = pd.read_csv('predictions.csv')
cities = df['city'].unique()

# 2. 创建页面
page = Page()

# 3. 为每个城市创建图表
for city in cities:
    city_data = df[df['city'] == city]
    
    line = (
        Line()
        .add_xaxis(list(range(len(city_data))))
        .add_yaxis("实际值", city_data['airQuality'].tolist())
        .add_yaxis("预测值", city_data['prediction'].tolist())
        .set_global_opts(title_opts=opts.TitleOpts(title=f"{city}空气质量"))
    )
    line.chart_id = f"chart_{city}"  # 设置图表ID
    page.add(line)

# 4. 生成包含JavaScript的HTML文件
html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>空气质量预测</title>
    <style>
        #citySelector {{
            margin: 20px;
            padding: 5px;
            font-size: 16px;
        }}
    </style>
</head>
<body>
    <select id="citySelector">
        <option value="">--请选择城市--</option>
        {"".join([f'<option value="{city}">{city}</option>' for city in cities])}
    </select>
    
    <!-- 图表容器将由PyECharts自动插入到这里 -->
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            // 初始隐藏所有图表
            document.querySelectorAll('.chart-container').forEach(el => {{
                el.style.display = 'none';
            }});
            
            // 绑定下拉菜单事件
            document.getElementById('citySelector').addEventListener('change', function() {{
                // 隐藏所有图表
                document.querySelectorAll('.chart-container').forEach(el => {{
                    el.style.display = 'none';
                }});
                
                // 显示选中的图表
                const selectedCity = this.value;
                if (selectedCity) {{
                    document.getElementById('chart_' + selectedCity).style.display = 'block';
                }}
            }});
        }});
    </script>
</body>
</html>
"""

# 5. 先保存基础图表
page.render("temp_charts_part.html")

# 6. 合并模板和图表
with open("temp_charts_part.html", "r", encoding="utf-8") as f:
    charts_part = f.read()

# 找到插入点并替换
full_html = html_template.replace("<!-- 图表容器将由PyECharts自动插入到这里 -->", 
                                charts_part[charts_part.find("<body>")+6:charts_part.find("</body>")])

# 7. 保存最终文件
with open("air.html", "w", encoding="utf-8") as f:
    f.write(full_html)

print("图表已生成，请打开 air.html 查看")