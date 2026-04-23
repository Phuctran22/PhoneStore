from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Order 

@login_required(login_url='client:login')
def my_orders(request):
    """View hiển thị danh sách đơn hàng của người dùng"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'client/my_orders.html', {'orders': orders})

@login_required(login_url='client:login')
def order_detail(request, order_id):
    """View hiển thị chi tiết một đơn hàng cụ thể"""
    # Lấy đơn hàng, đảm bảo đơn hàng đó thuộc về người dùng đang đăng nhập
    order = get_object_or_404(Order, id=order_id, user=request.user)
    # Lấy danh sách sản phẩm trong đơn hàng
    items = order.items.all() 
    
    return render(request, 'client/order_detail.html', {
        'order': order,
        'items': items
    })

@login_required(login_url='client:login')
def cancel_order(request, order_id):
    """View xử lý logic hủy đơn hàng của khách hàng"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Chỉ cho phép hủy nếu đơn hàng đang ở trạng thái chờ xác nhận
    if order.status == 'pending':
        order.status = 'cancelled'
        order.save()
        messages.success(request, f"Đã hủy đơn hàng #{order.id} thành công.")
    else:
        messages.error(request, "Không thể hủy đơn hàng này do đã được xử lý hoặc đã giao.")
        
    return redirect('client:order_detail', order_id=order.id)
