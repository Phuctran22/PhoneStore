from django.shortcuts import get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils.text import slugify
from apps.core.models import Category


# =========================
# THÊM DANH MỤC
# =========================
@staff_member_required(login_url='client:login')
def category_add(request):
    if request.method == 'POST':
        name = request.POST.get('cat_name')

        if not name:
            messages.error(request, "Tên danh mục không được để trống!")
        elif Category.objects.filter(name=name).exists():
            messages.error(request, "Danh mục đã tồn tại!")
        else:
            Category.objects.create(
                name=name,
                slug=slugify(name)
            )
            messages.success(request, f"Đã thêm danh mục: {name}")

    return redirect('client:admin_product_list')


# =========================
# SỬA DANH MỤC
# =========================
@staff_member_required(login_url='client:login')
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        new_name = request.POST.get('cat_name')

        if new_name:
            category.name = new_name
            category.slug = slugify(new_name)
            category.save()
            messages.success(request, f"Đã cập nhật danh mục thành: {new_name}")

    return redirect('client:admin_product_list')


# =========================
# XÓA DANH MỤC
# =========================
@staff_member_required(login_url='client:login')
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if category.products.exists():
        messages.error(
            request,
            f"Không thể xóa '{category.name}' vì vẫn còn sản phẩm thuộc danh mục này!"
        )
    else:
        category.delete()
        messages.warning(request, f"Đã xóa danh mục '{category.name}' thành công.")

    return redirect('client:admin_product_list')
