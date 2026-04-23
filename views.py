# apps/users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test

# =============================
# ĐĂNG KÝ
# =============================
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Tên đăng nhập đã tồn tại")
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            login(request, user)
            messages.success(request, "Đăng ký thành công")
            return redirect('home')

    return render(request, 'users/register.html')


# =============================
# ĐĂNG NHẬP
# =============================
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Sai tài khoản hoặc mật khẩu")

    return render(request, 'users/login.html')


# =============================
# ĐĂNG XUẤT
# =============================
def logout_view(request):
    logout(request)
    return redirect('login')


# =============================
# USER (PHẢI LOGIN)
# =============================
@login_required(login_url='login')
def profile_view(request):
    return render(request, 'users/profile.html')


# =============================
# ADMIN (PHÂN QUYỀN)
# =============================
def is_admin(user):
    return user.is_staff


@user_passes_test(is_admin, login_url='login')
def admin_dashboard(request):
    return render(request, 'admin/dashboard.html')
