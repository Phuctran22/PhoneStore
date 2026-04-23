# cart_views.py

from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Coupon
from .cart import Cart


def cart_detail(request):
    """View hiển thị chi tiết giỏ hàng và xử lý mã giảm giá"""
    cart = Cart(request)
    # Ép về Decimal ngay từ đầu cho chuẩn tiền tệ
    cart_total = Decimal(sum(item['price'] * item['quantity'] for item in cart))
    
    discount_amount = Decimal(0)
    final_total = cart_total
    coupon = None
    coupon_id = request.session.get('coupon_id')

    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id)
            if coupon.is_valid() and cart_total >= coupon.min_purchase:
                if coupon.discount_type == 'percent':
                    # Tính phần trăm trên kiểu Decimal
                    discount_amount = (cart_total * coupon.discount_value) / 100
                else:
                    discount_amount = coupon.discount_value
                
                discount_amount = min(discount_amount, cart_total)
                final_total = cart_total - discount_amount
            else:
                if 'coupon_id' in request.session:
                    del request.session['coupon_id']
                coupon = None
        except Coupon.DoesNotExist:
            if 'coupon_id' in request.session:
                del request.session['coupon_id']

    context = {
        'cart': cart,
        'cart_total': cart_total,
        'discount_amount': discount_amount,
        'final_total': final_total,
        'coupon': coupon
    }
    return render(request, 'client/cart.html', context)


def cart_add(request, product_id):
    """View xử lý thêm sản phẩm vào giỏ hàng"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    qty = 1
    if request.method == 'POST':
        try: 
            qty = int(request.POST.get('quantity', 1))
        except ValueError: 
            qty = 1
            
    variation_id = request.POST.get('variation_id') if request.method == 'POST' else request.GET.get('variation_id')
    cart.add(product=product, quantity=qty, variation_id=variation_id)
    return redirect('client:cart')


def cart_remove(request, product_id):
    """View xử lý xóa sản phẩm khỏi giỏ hàng"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    variation_id = request.POST.get('variation_id') if request.method == 'POST' else request.GET.get('variation_id')
    cart.remove(product, variation_id=variation_id)
    return redirect('client:cart')
