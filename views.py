import json
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render, redirect, get_object_or_404
from apps.core.models import Product, Category, Store, Order, OrderItem
from .cart import Cart 
from .utils import haversine_distance 
from django.utils import timezone 
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models import Sum

# =========================================
# 1. TRANG CHỦ & DANH MỤC
# =========================================

def home(request):
    # 1. Lấy dữ liệu cơ bản từ request
    category_id = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    price_range = request.GET.get('price_range')
    
    categories = Category.objects.all().order_by('name')
    
    # 2. Logic lọc sản phẩm theo danh mục (Đã sửa lỗi ghi đè)
    if category_id:
        # Lọc sản phẩm theo danh mục
        products = Product.objects.filter(category_id=category_id).order_by('-id')
        current_category = get_object_or_404(Category, id=category_id)
    else:
        # Mặc định lấy tất cả sản phẩm mới nhất
        products = Product.objects.all().order_by('-id')
        current_category = None
    
    # 3. THÊM MỚI: Logic lọc theo mức giá (price_range hoặc min/max)
    # Chú ý: Chúng ta tiếp tục dùng biến 'products' ở trên để lọc tiếp, 
    # giúp khách hàng có thể vừa chọn Hãng vừa chọn Giá cùng lúc.
    if price_range:
        # Nếu người dùng chọn các mức giá có sẵn (Radio button)
        if price_range == '1-3':
            products = products.filter(price__gte=1000000, price__lte=3000000)
        elif price_range == '3-5':
            products = products.filter(price__gte=3000000, price__lte=5000000)
        elif price_range == '5-10':
            products = products.filter(price__gte=5000000, price__lte=10000000)
        elif price_range == '10-15':
            products = products.filter(price__gte=10000000, price__lte=15000000)
        elif price_range == '15-20':
            products = products.filter(price__gte=15000000, price__lte=20000000)
        elif price_range == '20-25':
            products = products.filter(price__gte=20000000, price__lte=25000000)
        elif price_range == '25-30':
            products = products.filter(price__gte=25000000, price__lte=30000000)
        elif price_range == '30-50':
            products = products.filter(price__gte=30000000, price__lte=50000000)
        elif price_range == '50-85':
            products = products.filter(price__gte=50000000, price__lte=85000000)
        elif price_range == '85+':
            products = products.filter(price__gte=85000000)
    else:
        # Nếu không chọn khoảng giá sẵn, kiểm tra xem có kéo thanh trượt không
        if min_price and min_price.isdigit():
            products = products.filter(price__gte=int(min_price))
        if max_price and max_price.isdigit():
            products = products.filter(price__lte=int(max_price))

    # 4. LOGIC Lấy Top 5 sản phẩm bán chạy nhất
    best_selling_products = Product.objects.filter(
        orderitem__order__status='completed'
    ).annotate(
        total_sold=Sum('orderitem__quantity')
    ).order_by('-total_sold')[:5]

    # 5. Truyền dữ liệu ra template
    context = {
        'products': products,
        'categories': categories,
        'best_selling_products': best_selling_products,
        'current_category': current_category,
    }
    return render(request, 'client/home.html', context)

# =========================================
# 2. TÌM KIẾM SẢN PHẨM
# =========================================

def search_view(request):
    query = request.GET.get('q')
    results = []
    if query:
        # Tìm kiếm theo tên hoặc mô tả
        results = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).distinct().order_by('-id')
    
    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'client/search_results.html', context)

# =========================================

# 4. CHI TIẾT SẢN PHẨM
# =========================================

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Gợi ý sản phẩm cùng danh mục
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    
    return render(request, 'client/product_detail.html', {
        'product': product,
        'related_products': related_products
    })

# =========================================
