import pandas as pd
from pyecharts.charts import Line, Page
from pyecharts import options as opts

# 1. 读取数据
df = pd.read_csv('prediction.csv')
cities = df['city'].unique()

# 2. 创建页面
page = Page()

# 3. 保存每个城市的分析
analysis_texts = {}

# 4. 为每个城市生成图表 + 分析
for city in cities:
    city_data = df[df['city'] == city]

    # 计算指标
    actual = city_data['AQI'].values
    prediction = city_data['prediction'].values
    mae = abs(actual - prediction).mean()
    mean_actual = actual.mean()
    mean_pred = prediction.mean()
    bias = (mean_pred - mean_actual) / mean_actual * 100

    # 人话分析
    analysis = (
        f"{city}：预测的平均AQI为 {mean_pred:.2f}，"
        f"实际平均AQI为 {mean_actual:.2f}，"
        f"平均绝对误差（MAE）为 {mae:.2f}，"
        f"预测偏差约为 {bias:+.2f}%。"
        f"整体来看，预测{'偏高' if bias > 0 else '偏低'}，误差{'较小' if mae < 10 else '较大'}。"
    )
    analysis_texts[city] = analysis

    # 图表
    line = (
        Line()
        .add_xaxis(list(range(len(city_data))))
        .add_yaxis("实际值", actual.tolist(), label_opts=opts.LabelOpts(is_show=False))
        .add_yaxis("预测值", prediction.tolist(), label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(
            title_opts=opts.TitleOpts(title=f"{city} 空气质量预测 vs. 实际"),
            toolbox_opts=opts.ToolboxOpts(is_show=False)
        )
    )
    line.chart_id = f"chart_{city}"
    page.add(line)

# 5. HTML 模板
html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>空气质量预测分析</title>
    <style>
        body {{
            font-family: "Microsoft YaHei", sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        .page-title {{
            text-align: center;
            margin: 3px 0 20px;
            font-size: 28px;
            color: #333;
        }}
        #citySelector {{
            margin: 20px 0;
            padding: 10px;
            font-size: 16px;
            border: 1px solid #ddd;
            border-radius: 4px;
            width: 200px;
        }}
        .chart-card {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            padding: 20px;
            margin-bottom: 30px;
            margin-top:-20px
        }}
        .chart-container {{
            height: 400px;
            margin: 0 auto;
        }}
        .chart-analysis {{
            background: #f9f9f9;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        }}
        .chart-analysis h2 {{
            margin-top: 0;
            color: #444;
        }}
        .chart-analysis p {{
            font-size: 16px;
            line-height: 1.6;
            color: #555;
        }}
    </style>
</head>
<body>
    <h1 class="page-title">空气质量预测分析</h1>

    <select id="citySelector">
        <option value="">--请选择城市--</option>
        {"".join([f'<option value="{city}">{city}</option>' for city in cities])}
    </select>

    <div class="chart-card">
        <!-- PyECharts 图表容器 -->
    </div>

    <div class="chart-analysis">
        <h2>图表分析</h2>
        <p id="analysisText">请选择城市查看该城市的预测与实际对比分析。</p>
    </div>

    <script>
        const analysisTexts = {{
            {"".join([f"'{city}': `{text}`," for city, text in analysis_texts.items()])}
        }};

        document.addEventListener('DOMContentLoaded', function() {{
            document.querySelectorAll('.chart-container').forEach(el => {{
                el.style.display = 'none';
            }});

            const defaultCity = '{cities[0]}';
            const citySelector = document.getElementById('citySelector');

            for (let i = 0; i < citySelector.options.length; i++) {{
                if (citySelector.options[i].value === defaultCity) {{
                    citySelector.selectedIndex = i;
                    break;
                }}
            }}

            if (citySelector.value === defaultCity) {{
                document.getElementById('chart_' + defaultCity).style.display = 'block';
                updateAnalysis(defaultCity);
            }}

            citySelector.addEventListener('change', function() {{
                document.querySelectorAll('.chart-container').forEach(el => {{
                    el.style.display = 'none';
                }});

                const selectedCity = this.value;
                if (selectedCity) {{
                    document.getElementById('chart_' + selectedCity).style.display = 'block';
                    updateAnalysis(selectedCity);
                }}
            }});

            function updateAnalysis(city) {{
                const analysis = analysisTexts[city] || '暂无该城市分析。';
                document.getElementById('analysisText').innerText = analysis;
            }}
        }});
    </script>
</body>
</html>
"""

# 6. 生成临时图表文件
page.render("temp_charts_part.html")

# 7. 合并 HTML
with open("temp_charts_part.html", "r", encoding="utf-8") as f:
    charts_part = f.read()

charts_content = charts_part[charts_part.find("<body>")+6:charts_part.find("</body>")]
full_html = html_template.replace("<!-- PyECharts 图表容器 -->", charts_content)

# 8. 写出
with open("air.html", "w", encoding="utf-8") as f:
    f.write(full_html)

print("✅ 已生成 air.html，可浏览器打开查看！")
