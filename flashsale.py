from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

# Import models
from apps.core.models import FlashSale, Product

# Import decorator phân quyền
from .decorators import role_required


# =========================================
# QUẢN LÝ FLASH SALE
# =========================================
@role_required(['super_admin'])
def admin_flash_sale(request):
    flash_sales = FlashSale.objects.all().select_related('product').order_by('-id')
    available_products = Product.objects.filter(flash_sale__isnull=True)

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        flash_price = request.POST.get('flash_price')
        end_time = request.POST.get('end_time')

        try:
            product = get_object_or_404(Product, id=product_id)
            FlashSale.objects.create(
                product=product,
                flash_price=flash_price,
                end_time=end_time,
                is_active=True
            )
            messages.success(request, f"Đã thiết lập Flash Sale cho '{product.name}'!")
        except Exception as e:
            messages.error(request, f"Có lỗi xảy ra: {str(e)}")
            
        return redirect('client:admin_flash_sale')

    return render(request, 'admin_custom/flash_sale_management.html', {
        'flash_sales': flash_sales,
        'available_products': available_products
    })


@role_required(['super_admin'])
def delete_flash_sale(request, pk):
    fs = get_object_or_404(FlashSale, pk=pk)
    fs.delete()
    messages.warning(request, "Đã gỡ bỏ chương trình Flash Sale của sản phẩm này.")
    return redirect('client:admin_flash_sale')
