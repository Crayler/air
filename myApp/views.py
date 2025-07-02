from django.shortcuts import render, redirect
def index(request):
    return render(request,'index.html',{})

def login(request):
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