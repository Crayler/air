from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password
from .models import User
from django.views import generic

class IndexView(generic.ListView):
    template_name = 'index.html'

    def get_queryset(self):
        return None

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
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # 验证必填字段
        if not all([username, password]):
            messages.error(request, '请输入用户名和密码')
            return render(request, 'login.html')
        
        try:
            # 尝试获取用户
            user = User.objects.get(username=username)
            
            # 验证密码
            if check_password(password, user.password):
                # 密码正确，登录用户
                login(request, user)
                messages.success(request, f'欢迎回来，{username}！')
                # 重定向到首页或之前访问的页面
                return redirect(request.GET.get('next') or 'myApp:index')
            else:
                messages.error(request, '密码错误，请重新输入')
                return render(request, 'login.html')
                
        except User.DoesNotExist:
            messages.error(request, '用户名不存在，请检查后重试')
            return render(request, 'login.html')
        except Exception as e:
            messages.error(request, f'登录失败: {str(e)}')
            return render(request, 'login.html')
    
    # GET请求时显示登录页面
    return render(request,'login.html',{})


def logout(request):
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
            messages.error(request, '请填写完整注册信息')
            return render(request, 'register.html')
        
        # 验证邮箱是否已被注册
        if User.objects.filter(email=email).exists():
            messages.error(request, '该邮箱已被注册')
            return render(request, 'register.html')
        
        # 验证用户名是否已存在
        if User.objects.filter(username=username).exists():
            messages.error(request, '该用户名已存在')
            return render(request, 'register.html')
        try:
            # 加密密码
            #hashed_password = make_password(password)
            #print(hashed_password)
            # 创建用户
            user = User(
                email=email,
                username=username,
                password=password
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
            "SELECT city, year, month, avg_month_AQI FROM aqi_result ORDER BY year DESC, month DESC LIMIT 1"
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



