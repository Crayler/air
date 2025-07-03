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


def dist(request):
    return render(request,'dist.html',{})

    
def monthly(request):
    return render(request,'monthly.html',{})


def year(request):
    return render(request,'year.html',{})


from .models import AirQuality

def rank(request):
    # 从数据库取最近一天的数据，并按 rank 排序
    latest_date = AirQuality.objects.latest('date').date
    rankings = AirQuality.objects.filter(date=latest_date).order_by('rank')
    return render(request, 'rank.html', {'rankings': rankings, 'latest_date': latest_date})