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
        print("xxx")
        
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
            hashed_password = make_password(password)
            
            # 创建用户
            user = User(
                email=email,
                username=username,
                password=hashed_password
            )
            user.save()
            
            # 注册成功，重定向到登录页面并显示成功消息
            messages.success(request, '注册成功，请登录')
            return redirect('myApp:login')
            
        except Exception as e:
            messages.error(request, f'注册失败: {str(e)}')
            return render(request, 'register.html')
    
    # GET请求时显示注册页面
    return render(request, 'register.html')


    
def realtime(request):
    return render(request,'realtime.html',{})


def predict(request):
    return render(request,'predict.html',{})

def rank(request):
    return render(request,'rank.html',{})




import json
from django.shortcuts import render
from django.db.models import F
from .models import dituAirQuality
def dist(request):
    year = 2025
    month = int(request.GET.get('month', 1))
    
    # 验证月份是否有效
    if month not in range(1, 13):
        month = 1
    
    try:
        # 使用数据库函数计算平均AQI
        data_qs = dituAirQuality.objects.filter(year=year, month=month).annotate(
            avg_aqi=(F('max_AQI') + F('min_AQI')) / 2
        ).order_by('city')

        cities = [item.city for item in data_qs]
        avg_aqis = [item.avg_aqi for item in data_qs]

        # 当没有数据时显示默认值
        if not cities:
            cities = ["北京", "上海", "广州", "深圳", "成都", "杭州", "武汉", "西安", "南京"]
            avg_aqis = [120, 80, 90, 75, 100, 70, 95, 110, 85]
            no_data = True
        else:
            no_data = False

    except Exception as e:
        # 错误处理
        print(f"Error fetching AQI data: {e}")
        cities = ["北京", "上海", "广州"]
        avg_aqis = [100, 100, 100]
        no_data = True

    months = list(range(1, 13))

    print('DEBUG cities:', cities)
    print('DEBUG avg_aqis:', avg_aqis)

    context = {
        'year': year,
        'month': month,
        'cities': json.dumps(cities, ensure_ascii=False),
        'avg_aqis': json.dumps(avg_aqis, ensure_ascii=False),
        'months': months,
        'no_data': no_data,
    }

    return render(request, 'dist.html', context)




    
def monthly(request):
    return render(request,'monthly.html',{})


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



from .models import AirQuality

def rank(request):
    # 从数据库取最近一天的数据，并按 rank 排序
    latest_date = AirQuality.objects.latest('date').date
    rankings = AirQuality.objects.filter(date=latest_date).order_by('rank')
    return render(request, 'rank.html', {'rankings': rankings, 'latest_date': latest_date})

def dist(request):
    return render(request,'dist.html',{})


