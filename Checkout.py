# Checkout.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# LƯU Ý: Hãy điều chỉnh lại đường dẫn import các models và Cart 
# sao cho khớp với cấu trúc ứng dụng của bạn.
from .models import Coupon, ShippingAddress, Store, StoreStock, Order, OrderItem, Notification
from .cart import Cart 


@login_required(login_url='client:login')
def checkout(request):
    cart = Cart(request)
    # Nếu giỏ hàng trống, không cho vào trang thanh toán
    if cart.get_total_price() == 0:
        return redirect('client:home')

    # ==========================================
    # 1. LOGIC TÍNH TOÁN MÃ GIẢM GIÁ
    # ==========================================
    cart_total = cart.get_total_price()
    discount_amount = 0
    coupon = None
    coupon_id = request.session.get('coupon_id')

    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id)
            if coupon.is_valid() and cart_total >= coupon.min_purchase:
                if coupon.discount_type == 'percent':
                    discount_amount = (cart_total * coupon.discount_value) / 100
                else:
                    discount_amount = coupon.discount_value
                discount_amount = min(discount_amount, cart_total)
            else:
                coupon = None
                if 'coupon_id' in request.session:
                    del request.session['coupon_id']
        except Coupon.DoesNotExist:
            coupon = None
            if 'coupon_id' in request.session:
                del request.session['coupon_id']
            
    final_total = cart_total - discount_amount

    # ==========================================
    # 2. XỬ LÝ LƯU ĐƠN HÀNG (KHI NGƯỜI DÙNG SUBMIT FORM)
    # ==========================================
    if request.method == 'POST':
        name = request.POST.get('fullname')
        phone = request.POST.get('phone')
        
        # Xử lý phương thức giao hàng
        delivery_method = request.POST.get('delivery_method', 'delivery')
        
        final_address = ""
        store_pickup = None
        shipping_fee = 0
        
        if delivery_method == 'delivery':
            address_id = request.POST.get('address_id', 'new')
            province_str = ""
            
            if address_id == 'new':
                province_str = request.POST.get('province', '')
                district = request.POST.get('district', '')
                ward = request.POST.get('ward', '')
                detail = request.POST.get('address_detail', '')
                final_address = f"{detail}, {ward}, {district}, {province_str}".strip(", ")
            else:
                try:
                    addr = ShippingAddress.objects.get(id=address_id, user=request.user)
                    province_str = addr.area_info or ""
                    final_address = f"{addr.address_detail}, {addr.area_info}".strip(", ")
                except ShippingAddress.DoesNotExist:
                    final_address = ""
            
            # Tính phí giao hàng
            province_lower = province_str.lower()
            is_hcm = any(x in province_lower for x in ['hcm', 'hồ chí minh', 'ho chi minh', 'hcmc'])
            nearby = ['bình dương', 'binh duong', 'đồng nai', 'dong nai', 'long an', 'bà rịa', 'ba ria', 'tây ninh', 'tay ninh', 'tiền giang', 'tien giang']
            is_nearby = any(x in province_lower for x in nearby)

            if is_hcm:
                if cart_total >= 500000:
                    shipping_fee = 0
                else:
                    shipping_fee = 30000
            elif is_nearby:
                shipping_fee = 30000
            else:
                shipping_fee = 50000
                
            final_total += shipping_fee
            
            # TỰ ĐỘNG GÁN KHO TỔNG LÀM CỬA HÀNG XUẤT KHO CHO ĐƠN GIAO TẬN NƠI
            store_pickup = Store.objects.filter(is_main_warehouse=True).first()
            
        elif delivery_method == 'pickup':
            # Nếu nhận tại cửa hàng, lưu ID cửa hàng khách chọn
            store_id = request.POST.get('store_id')
            if store_id:
                store_pickup = Store.objects.filter(id=store_id).first()
                final_address = f"Nhận tại cửa hàng: {store_pickup.name} ({store_pickup.address})"

        # Lấy hình thức thanh toán
        payment_method = request.POST.get('payment_method', 'cod')

        # Tạo Đơn hàng
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            full_name=name,
            phone=phone,
            address=final_address,
            total_price=final_total,             # Lưu giá ĐÃ TRỪ tiền giảm (cộng phí gửi)
            shipping_fee=shipping_fee,
            coupon=coupon,                       # Lưu ID mã giảm giá
            discount_amount=discount_amount,     # Lưu số tiền được giảm
            fulfillment_store=store_pickup,      # LƯU CỬA HÀNG CHỊU TRÁCH NHIỆM XUẤT KHO (Rất quan trọng)
            payment_method=payment_method,       # Hình thức thanh toán
            payment_status='unpaid'              # Khởi tạo mặc định
        )
        
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                variation=item.get('variation'),
                price=item['price'],
                quantity=item['quantity']
            )
            
        # Tăng lượt dùng của mã lên 1 và xóa mã khỏi session
        if coupon:
            coupon.used_count += 1
            coupon.save()
            del request.session['coupon_id']
            
        cart.clear()

        # ==================================================
        # TẠO THÔNG BÁO & GỬI EMAIL KHI ĐẶT HÀNG THÀNH CÔNG
        # ==================================================
        if request.user.is_authenticated:
            Notification.objects.create(
                user=request.user,
                notif_type='order_placed',
                order=order,
                message=f'Đơn hàng #{order.id} của bạn đã được đặt thành công! Chúng tôi đang xác nhận đơn hàng.'
            )
            # Gửi email xác nhận đặt hàng
            try:
                items_with_total = [
                    {
                        'name': item.product.name,
                        'quantity': item.quantity,
                        'price': item.price,
                        'subtotal': item.price * item.quantity,
                    }
                    for item in order.items.all()
                ]
                html_order = render_to_string('client/emails/order_placed_email.html', {
                    'order': order,
                    'items': items_with_total,
                    'username': request.user.username,
                })
                send_mail(
                    subject=f'✅ Đặt hàng thành công - Đơn #{order.id} | Phone Store',
                    message=strip_tags(html_order),
                    from_email='noreply@phonestore.vn',
                    recipient_list=[request.user.email],
                    html_message=html_order,
                    fail_silently=True,
                )
            except Exception:
                pass

        messages.success(request, f"🎉 Đặt hàng thành công! Đơn hàng <strong>#{order.id}</strong> đang được xử lý.")
        if payment_method == 'bank_transfer':
            return redirect('client:payment_instruction', order_id=order.id)
            
        return redirect('client:notifications')

    # ==========================================
    # 3. TRUYỀN DỮ LIỆU RA GIAO DIỆN (GET)
    # ==========================================
    saved_addresses = ShippingAddress.objects.filter(user=request.user).order_by('-is_default')
    
    # KHO TỔNG: Kiểm tra xem có đủ hàng để ship tận nhà không
    main_warehouse = Store.objects.filter(is_main_warehouse=True).first()
    can_home_delivery = True
    
    if main_warehouse:
        for item in cart:
            product = item['product']
            quantity_needed = item['quantity']
            inventory = StoreStock.objects.filter(store=main_warehouse, product=product).first()
            if not inventory or inventory.quantity < quantity_needed:
                can_home_delivery = False
                break
    else:
        can_home_delivery = False

    # CHI NHÁNH: Kiểm tra tồn kho từng cửa hàng để Nhận tại quán
    stores = Store.objects.all()
    for store in stores:
        store.has_stock = True 
        for item in cart:
            product = item['product']
            quantity_needed = item['quantity']
            inventory = StoreStock.objects.filter(store=store, product=product).first()
            if not inventory or inventory.quantity < quantity_needed:
                store.has_stock = False
                break

    context = {
        'cart': cart,
        'cart_total': cart_total,
        'discount_amount': discount_amount,
        'final_total': final_total,
        'coupon': coupon,
        'saved_addresses': saved_addresses,
        'stores': stores,
        'can_home_delivery': can_home_delivery,
    }
    return render(request, 'client/checkout.html', context)
