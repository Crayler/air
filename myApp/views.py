from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password,make_password
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from .models import User
from django.views import generic

class IndexView(generic.ListView):
    template_name = 'index.html'

    def get_queryset(self):
        return None

def index(request):
    return render(request,'index.html',{})

def air(request):
    return render(request,'air.html',{})

from .models import O3Category, CoCategory
def gas(request):
    """处理空气质量数据并渲染图表"""
    # 获取O3分类数据
    o3_data = O3Category.objects.all()
    o3_categories = [item.O3_category for item in o3_data]
    o3_counts = [item.O3_count for item in o3_data]
    
    # 获取CO分类数据
    co_data = CoCategory.objects.all()
    co_categories = [item.Co_category for item in co_data]
    co_counts = [item.Co_count for item in co_data]
    
    return render(request, 'gas.html', {
        'o3_categories': o3_categories,
        'o3_counts': o3_counts,
        'co_categories': co_categories,
        'co_counts': co_counts,
    })  

from .models import TableData
from django.core.paginator import Paginator
def table(request):
    data_list = TableData.objects.all().order_by('id')  # 按ID排序确保结果稳定
    paginator = Paginator(data_list, 20)  # 每页显示20条数据
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'table.html', {'data_list': page_obj})

    

def login(request):
    if request.session.get('is_login',None):
        return render(request,'login.html',{})
    if request.method == 'GET':
        return render(request, 'login.html')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # 验证必填字段
        if not all([username, password]):
            message = '请输入用户名和密码'
            return render(request, 'login.html', {"message": message})
        try:
            # 尝试获取用户
            user = User.objects.get(username=username)
            
            # 验证密码
            if check_password(password, user.password):
                # 密码正确，登录用户
                request.session['is_login'] = True
                messages.success(request, f'欢迎回来，{username}！')
                # 重定向到首页或之前访问的页面
                return render(request,'index.html', {"username": username})
            else:
                print("login error")
                message =  '密码错误，请重新输入' 
                return render(request, 'login.html', {"message": message})
                
        except User.DoesNotExist:
            message= '用户名不存在，请检查后重试'
            return render(request, 'login.html', {"message": message})
        except Exception as e:
            messages.error(request, f'登录失败: {str(e)}')
            return render(request, 'login.html')
    
    # GET请求时显示登录页面
    return render(request,'login.html',{})


def logout(request):
    if not request.session.get('is_login', None):
        return render(request,'logout.html',{})
    request.session.flush()
    return render(request,'logout.html',{})


def register(request):  
    """处理用户注册请求"""
    if request.method == 'POST':
        # 从POST请求中获取注册数据
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(f"e:{email},u:{username},p:{password}")
        
        # 简单验证数据完整性
        if not all([email, username, password]):
            message='请填写完整注册信息'
            return render(request, 'register.html', {"message": message})
        
        # 验证邮箱是否已被注册
        if User.objects.filter(email=email).exists():
            message='该邮箱已被注册'
            return render(request, 'register.html', {"message": message})
        
        # 验证用户名是否已存在
        if User.objects.filter(username=username).exists():
            message='该用户名已存在'
            return render(request, 'register.html', {"message": message})
        try:
            # 加密密码
            hashed_password = make_password(password)
            print(hashed_password)
            # 创建用户
            user = User(
                email=email,
                username=username,
                password=hashed_password
            )
            print("save user")
            user.save()
            
            # 注册成功，重定向到登录页面并显示成功消息
            messages.success(request, '注册成功，请登录')
            return redirect('myApp:login')
        except Exception as e:
            print("register failed")
            messages.error(request, f'注册失败: {str(e)}')
            return render(request, 'register.html')
    
    # GET请求时显示注册页面
    return render(request, 'register.html')


    
from django.http import JsonResponse
from django.db import connection

def realtime(request):
    # 页面初次渲染只需要把模板返回，前端 JS 自己 fetch 数据
    return render(request, 'realtime.html')

def get_latest_aqi(request):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT city, year, month, avg_month_AQI FROM aqi_result WHERE updatetime = (SELECT MAX(updatetime) FROM aqi_result) LIMIT 1;"
        )
        row = cursor.fetchone()

    print('==== Latest AQI row:', row)  # 加这个！

    if row:
        data = {
            'city': row[0],
            'year': row[1],
            'month': row[2],
            'avg_month_AQI': float(row[3])
        }
    else:
        data = {
            'city': '',
            'year': '',
            'month': '',
            'avg_month_AQI': 0
        }

    return JsonResponse(data)



def predict(request):
    return render(request,'predict.html',{})




from .models import YearAirQuality
import json

def year(request):
    selected_year = request.GET.get('year', 2025)
    selected_city = request.GET.get('city', '北京')

    data = YearAirQuality.objects.filter(year=selected_year, city=selected_city).order_by('month')

    months = [f"{item.month}月" for item in data]
    max_PM = [item.max_PM for item in data]
    min_PM10 = [item.min_PM10 for item in data]

    context = {
        'selected_year': selected_year,
        'selected_city': selected_city,
        'months': json.dumps(months),       # ✅ 用 json.dumps
        'max_PM': json.dumps(max_PM),
        'min_PM10': json.dumps(min_PM10),
    }

    return render(request, 'year.html', context)



from django.db.models import Sum
from .models import AirQuality

def rank(request):
    # 获取可选的年月列表
    years = AirQuality.objects.values_list('year', flat=True).distinct().order_by('-year')
    months = AirQuality.objects.values_list('month', flat=True).distinct().order_by('month')
    
    # 默认显示最新年月数据
    latest_data = AirQuality.objects.order_by('-year', '-month').first()
    selected_year = request.GET.get('year', latest_data.year if latest_data else None)
    selected_month = request.GET.get('month', latest_data.month if latest_data else None)
    
    rankings = []
    latest_date = "暂无数据"
    total_days = 0
    max_days = 0

    if selected_year and selected_month:
        # 筛选指定年月的数据
        queryset = AirQuality.objects.filter(
            year=selected_year,
            month=selected_month
        ).order_by('-count_grate')
        
        # 添加排名和百分比信息
        total_days = queryset.aggregate(total=Sum('count_grate'))['total'] or 0
        max_days = queryset.first().count_grate if queryset else 0
        
        for i, item in enumerate(queryset, 1):
            item.rank = i
            item.percentage = (item.count_grate / max_days * 100) if max_days > 0 else 0
            rankings.append(item)
        
        latest_date = f"{selected_year}年{selected_month}月"

    return render(request, 'rank.html', {
        'rankings': rankings,
        'latest_date': latest_date,
        'years': years,
        'months': months,
        'selected_year': selected_year,
        'selected_month': selected_month,
        'total_days': total_days,
        'max_days': max_days,
    })

# AI空气质量对话页面
@ensure_csrf_cookie
def AI(request):
    """AI对话页面 - 智能空气质量助手"""
    # 获取所有城市列表
    cities = TableData.objects.values_list('city', flat=True).distinct().order_by('city')

    # 获取最新的实时数据用于初始化
    latest_aqi = None
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT city, year, month, avg_month_AQI, updatetime FROM aqi_result "
            "WHERE updatetime = (SELECT MAX(updatetime) FROM aqi_result) LIMIT 1"
        )
        row = cursor.fetchone()
        if row:
            latest_aqi = {
                'city': row[0],
                'year': row[1],
                'month': row[2],
                'aqi': float(row[3]),
                'updatetime': row[4]
            }

    return render(request, 'AI.html', {
        'cities': list(cities),
        'latest_aqi': latest_aqi
    })


@require_http_methods(["GET"])
def get_trend_data(request):
    """获取近7天AQI趋势数据"""
    city = request.GET.get('city', '北京')

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT DATE_FORMAT(date, '%m-%d') as day, AQI "
                "FROM airdata "
                "WHERE city = %s "
                "ORDER BY date DESC LIMIT 7",
                [city]
            )
            rows = cursor.fetchall()

            # 反转数据，使其从旧到新排列
            rows = list(reversed(rows))

            labels = [row[0] for row in rows]
            values = [int(row[1]) if row[1] else 0 for row in rows]

            return JsonResponse({
                'labels': labels,
                'values': values
            })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


from django.views.decorators.csrf import csrf_exempt
import random
from datetime import datetime, timedelta
import requests

# 城市名称到高德城市编码的映射
CITY_ADCODE_MAP = {
    '北京': '110000',
    '上海': '310000',
    '广州': '440100',
    '深圳': '440300',
    '成都': '510100',
    '杭州': '330100',
    '武汉': '420100',
    '西安': '610100',
    '重庆': '500000',
    '天津': '120000',
    '南京': '320100',
    '苏州': '320500',
    '长沙': '430100',
    '郑州': '410100',
    '沈阳': '210100',
    '青岛': '370200',
    '济南': '370100',
    '哈尔滨': '230100',
    '福州': '350100',
    '厦门': '350200',
}

def get_weather_data(city):
    """获取高德天气数据"""
    amap_key = '0b71692c73f6823579bb0fb7616c3181'
    city_code = CITY_ADCODE_MAP.get(city, '110000')  # 默认北京

    try:
        # 获取实况天气
        url = 'https://restapi.amap.com/v3/weather/weatherInfo'
        params = {
            'key': amap_key,
            'city': city_code,
            'extensions': 'base'
        }
        response = requests.get(url, params=params, timeout=3)
        data = response.json()

        if data.get('status') == '1' and data.get('lives'):
            live = data['lives'][0]
            return {
                'weather': live.get('weather', ''),
                'temperature': live.get('temperature', ''),
                'winddirection': live.get('winddirection', ''),
                'windpower': live.get('windpower', ''),
                'humidity': live.get('humidity', ''),
                'reporttime': live.get('reporttime', '')
            }
    except Exception as e:
        print(f"获取天气数据失败: {e}")

    return None

@require_http_methods(["POST"])
@csrf_exempt
def ai_chat(request):
    """处理AI聊天请求"""
    import json

    try:
        data = json.loads(request.body)
        question = data.get('question', '').strip()
        city = data.get('city', '北京')

        if not question:
            return JsonResponse({'error': '问题不能为空'}, status=400)

        # 获取城市当前空气质量数据
        city_data = TableData.objects.filter(city=city).order_by('-date').first()

        # 获取城市历史统计
        with connection.cursor() as cursor:
            # 获取城市平均AQI
            cursor.execute(
                "SELECT AVG(AQI) as avg_aqi FROM airdata WHERE city = %s",
                [city]
            )
            avg_row = cursor.fetchone()
            avg_aqi = float(avg_row[0]) if avg_row and avg_row[0] else 0

            # 获取最近7天趋势
            cursor.execute(
                "SELECT date, AQI, PM, PM10, O3, Co FROM airdata "
                "WHERE city = %s ORDER BY date DESC LIMIT 7",
                [city]
            )
            trend_data = cursor.fetchall()

        # 获取实时天气数据
        weather_info = get_weather_data(city)

        # AI回复逻辑
        reply = generate_ai_reply(question, city, city_data, avg_aqi, trend_data, weather_info)

        return JsonResponse({
            'reply': reply,
            'city': city,
            'current_aqi': city_data.AQI if city_data else None,
            'weather': weather_info,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的JSON格式'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'处理请求时出错: {str(e)}'}, status=500)


def generate_ai_reply(question, city, city_data, avg_aqi, trend_data, weather_info=None):
    """生成AI回复内容"""
    q = question.lower()

    if not city_data:
        return f"抱歉，暂无{city}的空气质量数据。请选择其他城市或稍后再试。"

    # 空气质量等级判断 - 确保AQI是整数类型
    try:
        aqi = int(city_data.AQI) if isinstance(city_data.AQI, str) else city_data.AQI
    except (ValueError, TypeError):
        return f"抱歉，{city}的空气质量数据格式有误。"

    if aqi <= 50:
        level, color, advice = "优", "绿色", "空气质量令人满意，适宜各类人群进行户外活动"
    elif aqi <= 100:
        level, color, advice = "良", "黄色", "空气质量可接受，敏感人群需适当减少户外活动"
    elif aqi <= 150:
        level, color, advice = "轻度污染", "橙色", "儿童、老年人及心脏病、呼吸系统疾病患者应减少长时间户外锻炼"
    elif aqi <= 200:
        level, color, advice = "中度污染", "红色", "儿童、老年人及心脏病、呼吸系统疾病患者避免户外活动，一般人群减少户外活动"
    elif aqi <= 300:
        level, color, advice = "重度污染", "紫色", "儿童、老年人和病人应停留在室内，一般人群减少户外活动，外出建议佩戴口罩"
    else:
        level, color, advice = "严重污染", "褐红色", "所有人群应避免户外活动，必须外出时需佩戴专业防护口罩"

    # 关键词匹配生成回复
    if any(kw in q for kw in ['空气质量', '空气怎么样', '空气状况', '今天', '现在']):
        reply = (
            f"📊 {city}当前空气质量状况:\n\n"
            f"🔹 AQI指数：{aqi} ({level})\n"
            f"🔹 首要污染物：PM2.5 ({city_data.PM} μg/m³)\n"
            f"🔹 其他指标：PM10 {city_data.PM10}、O3 {city_data.O3}、CO {city_data.Co}\n"
        )

        # 添加天气信息
        if weather_info:
            reply += (
                f"\n🌤️ 实时天气：\n"
                f"🔹 天气状况：{weather_info['weather']}\n"
                f"🔹 温度：{weather_info['temperature']}℃\n"
                f"🔹 风向风力：{weather_info['winddirection']}风 {weather_info['windpower']}级\n"
                f"🔹 湿度：{weather_info['humidity']}%\n"
            )

        reply += f"\n💡 健康建议：{advice}"
        return reply

    elif 'pm2.5' in q or 'pm25' in q:
        pm25 = city_data.PM
        status = "优秀" if pm25 <= 35 else "良好" if pm25 <= 75 else "超标"
        return (
            f"📈 {city}当前PM2.5浓度为 {pm25} μg/m³\n\n"
            f"参考标准：优秀≤35，良好≤75，当前状态为{status}。\n"
            f"PM2.5是空气中直径小于等于2.5微米的颗粒物，能够深入肺部，对健康影响较大。"
        )

    elif 'pm10' in q:
        pm10 = city_data.PM10
        status = "优秀" if pm10 <= 50 else "良好" if pm10 <= 150 else "超标"
        return (
            f"📈 {city}当前PM10浓度为 {pm10} μg/m³\n\n"
            f"参考标准：优秀≤50，良好≤150，当前状态为{status}。\n"
            f"PM10是直径小于等于10微米的可吸入颗粒物。"
        )

    elif any(kw in q for kw in ['预测', '预报', '明天', '未来', '趋势']):
        # 基于历史数据分析趋势
        if len(trend_data) >= 3:
            recent_aqis = [row[1] for row in trend_data[:3]]
            trend = "上升" if recent_aqis[0] > recent_aqis[-1] else "下降" if recent_aqis[0] < recent_aqis[-1] else "平稳"

            # 简单预测：基于平均值和趋势
            predicted_aqi = int(sum(recent_aqis) / len(recent_aqis) * (1.05 if trend == "上升" else 0.95 if trend == "下降" else 1.0))

            return (
                f"🔮 {city}空气质量预测：\n\n"
                f"📊 近期趋势：{trend}（近3日AQI：{' → '.join(map(str, recent_aqis))}）\n"
                f"🔹 明日预测AQI：约{predicted_aqi}\n"
                f"🔹 预测等级：{get_aqi_level(predicted_aqi)}\n\n"
                f"💡 建议：{'注意防护，减少户外活动' if predicted_aqi > 100 else '适宜户外活动'}"
            )
        else:
            return f"抱歉，{city}的历史数据不足，暂时无法进行准确预测。"

    elif any(kw in q for kw in ['防护', '建议', '注意', '口罩', '健康']):
        reply = (
            f"🏥 {city}当前空气质量为{level}，健康防护建议：\n\n"
            f"✅ {advice}\n\n"
            f"其他建议：\n"
            f"• {'建议佩戴N95或以上级别口罩' if aqi > 150 else '一般不需要佩戴口罩' if aqi <= 50 else '敏感人群可佩戴口罩'}\n"
            f"• {'关闭门窗，使用空气净化器' if aqi > 100 else '适度开窗通风'}\n"
            f"• {'避免户外运动' if aqi > 150 else '可适度进行户外活动'}"
        )

        # 结合天气给建议
        if weather_info:
            temp = int(weather_info['temperature'])
            weather = weather_info['weather']
            reply += (
                f"\n\n🌤️ 天气状况：{weather}，{temp}℃\n"
                f"• {'天气较冷，注意保暖' if temp < 10 else '天气炎热，注意防暑' if temp > 30 else '温度适宜'}\n"
                f"• {'雨天湿度大，有助于降低污染物浓度' if '雨' in weather else '晴天紫外线较强，注意防晒' if '晴' in weather else ''}\n"
            )

        return reply

    elif any(kw in q for kw in ['天气', '温度', '下雨', '刮风']):
        if weather_info:
            return (
                f"🌤️ {city}实时天气：\n\n"
                f"🔹 天气状况：{weather_info['weather']}\n"
                f"🔹 温度：{weather_info['temperature']}℃\n"
                f"🔹 风向风力：{weather_info['winddirection']}风 {weather_info['windpower']}级\n"
                f"🔹 湿度：{weather_info['humidity']}%\n"
                f"🔹 更新时间：{weather_info['reporttime']}\n\n"
                f"📊 当前AQI：{aqi}（{level}）\n"
                f"💡 建议：{'天气与空气质量良好，适宜户外活动' if aqi <= 100 else '空气质量较差，减少户外活动'}"
            )
        else:
            return f"抱歉，暂时无法获取{city}的天气数据。"

    elif any(kw in q for kw in ['对比', '比较', '排名', '哪个城市']):
        # 查询多个城市数据进行对比
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT city, AVG(AQI) as avg_aqi FROM airdata "
                "GROUP BY city ORDER BY avg_aqi LIMIT 5"
            )
            top_cities = cursor.fetchall()

        ranking = "\n".join([f"{i+1}. {row[0]}：AQI {int(row[1])}" for i, row in enumerate(top_cities)])
        return (
            f"🏆 全国空气质量最佳城市TOP5：\n\n{ranking}\n\n"
            f"{city}的平均AQI为{int(avg_aqi)}。"
        )

    elif any(kw in q for kw in ['污染源', '为什么', '原因', '哪里来']):
        return (
            f"🏭 空气污染主要来源：\n\n"
            f"1. 工业排放：工厂生产过程中排放的废气\n"
            f"2. 机动车尾气：汽车尾气是城市PM2.5的重要来源\n"
            f"3. 扬尘：建筑工地、道路扬尘\n"
            f"4. 燃煤：冬季供暖燃煤会增加污染物排放\n"
            f"5. 气象条件：不利的气象条件会导致污染物累积\n\n"
            f"{city}当前首要污染物为PM2.5，建议关注工业和交通污染防治。"
        )

    elif '历史' in q or '过去' in q or '之前' in q:
        if trend_data:
            history = "\n".join([
                f"• {row[0]}：AQI {row[1]} (PM2.5: {row[2]}, PM10: {row[3]})"
                for row in trend_data[:7]
            ])
            return f"📅 {city}近7日空气质量历史：\n\n{history}"
        else:
            return f"暂无{city}的历史数据记录。"

    else:
        # 默认回复
        return (
            f"🤖 您好！我是空气质量智能助手。\n\n"
            f"当前{city}的AQI为{aqi}（{level}）。您可以询问：\n\n"
            f"• 今天空气质量怎么样？\n"
            f"• PM2.5浓度是多少？\n"
            f"• 明天空气质量预测\n"
            f"• 健康防护建议\n"
            f"• 城市空气质量对比\n"
            f"• 空气污染来源"
        )


def get_aqi_level(aqi):
    """获取AQI等级"""
    if aqi <= 50:
        return "优"
    elif aqi <= 100:
        return "良"
    elif aqi <= 150:
        return "轻度污染"
    elif aqi <= 200:
        return "中度污染"
    elif aqi <= 300:
        return "重度污染"
    else:
        return "严重污染"
