from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# ==========================================
# 1. QUẢN LÝ SẢN PHẨM & DANH MỤC
# ==========================================

class Category(models.Model):
    """
    Bảng Danh mục: Phân loại sản phẩm (VD: iPhone, Samsung, Xiaomi...)
    """
    name = models.CharField(max_length=100, verbose_name="Tên danh mục")
    slug = models.SlugField(unique=True, verbose_name="Đường dẫn thân thiện (URL)")

    def __str__(self):
        return self.name

class Product(models.Model):
    """
    Bảng Sản phẩm: Lưu trữ thông tin chi tiết của từng chiếc điện thoại
    """
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Danh mục")
    name = models.CharField(max_length=200, verbose_name="Tên điện thoại")
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Giá bán")
    description = models.TextField(verbose_name="Mô tả tóm tắt (Thông số kỹ thuật)")
    content = models.TextField(null=True, blank=True, verbose_name="Bài viết giới thiệu chi tiết")
    image = models.ImageField(upload_to='products/', null=True, blank=True, verbose_name="Ảnh đại diện (Bìa)")
    stock = models.IntegerField(default=0, verbose_name="Số lượng tồn kho hiện tại")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")

    def __str__(self):
        return self.name
    
class ProductImage(models.Model):
    """
    Bảng Album Ảnh bổ sung: Một sản phẩm có thể có nhiều ảnh phụ (Quan hệ 1-N)
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name="Sản phẩm")
    image = models.ImageField(upload_to='products/gallery/', verbose_name="Hình ảnh")

    def __str__(self):
        return f"Ảnh phụ của {self.product.name}"


# ==========================================
# 2. QUẢN LÝ BẢN ĐỒ (GIS) & CỬA HÀNG
# ==========================================

class Store(models.Model):
    """
    Bảng Cửa Hàng: Lưu thông tin và tọa độ để hiển thị lên bản đồ (Store Locator)
    """
    name = models.CharField(max_length=100, verbose_name="Tên cửa hàng")
    address = models.CharField(max_length=255, verbose_name="Địa chỉ chi tiết")
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Hotline")
    image = models.ImageField(upload_to='stores/', null=True, blank=True, verbose_name="Hình ảnh cửa hàng")
    
    # Tọa độ GPS phục vụ thuật toán tìm đường và tính khoảng cách
    latitude = models.FloatField(verbose_name="Vĩ độ (Latitude)")
    longitude = models.FloatField(verbose_name="Kinh độ (Longitude)")
    
    # Giờ hoạt động
    opening_time = models.TimeField(default="08:00:00", verbose_name="Giờ mở cửa")
    closing_time = models.TimeField(default="21:00:00", verbose_name="Giờ đóng cửa")

    def __str__(self):
        return self.name


# ==========================================
# 3. QUẢN LÝ GIAO DỊCH ĐƠN HÀNG (E-COMMERCE)
# ==========================================

class Order(models.Model):
    """
    Bảng Đơn Hàng: Lưu thông tin tổng quan khi khách hàng Checkout
    """
    STATUS_CHOICES = (
        ('pending', 'Chờ xử lý'),
        ('processing', 'Đang đóng gói'),
        ('shipped', 'Đang giao hàng'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Đã hủy'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', null=True, blank=True, verbose_name="Khách hàng")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Trạng thái đơn")

    # Thông tin giao hàng
    full_name = models.CharField(max_length=100, verbose_name="Họ và tên người nhận")
    address = models.CharField(max_length=255, verbose_name="Địa chỉ giao hàng")
    phone = models.CharField(max_length=20, verbose_name="Số điện thoại")
    total_price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Tổng tiền hóa đơn")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đặt hàng")

    def __str__(self):
        return f"Đơn hàng #{self.id} - {self.full_name}"

class OrderItem(models.Model):
    """
    Bảng Chi tiết Đơn hàng: Ghi lại từng món hàng nằm trong một Đơn hàng cụ thể
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Thuộc đơn hàng")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Sản phẩm")
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Giá lúc mua")
    quantity = models.IntegerField(default=1, verbose_name="Số lượng")

    def __str__(self):
        return f"{self.product.name} (SL: {self.quantity})"


# ==========================================
# 4. QUẢN LÝ KHO HÀNG (INVENTORY/STOCK)
# ==========================================

class StockTransaction(models.Model):
    """
    Bảng Nhật Ký Kho: Ghi lại mọi biến động tăng/giảm số lượng của sản phẩm để chống thất thoát
    """
    TRANSACTION_TYPES = (
        ('in', 'Nhập kho'),
        ('out', 'Xuất kho'),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_history', verbose_name="Sản phẩm giao dịch")
    quantity = models.IntegerField(verbose_name="Số lượng thay đổi")
    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_TYPES, verbose_name="Loại giao dịch (Nhập/Xuất)")
    price = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="Giá nhập đơn vị (Nếu là Nhập kho)")
    
    # Chỉ áp dụng nếu xuất kho đi cửa hàng khác
    store_destination = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Cửa hàng nhận (Nếu là Xuất kho)")
    
    note = models.TextField(blank=True, null=True, verbose_name="Ghi chú/Lý do")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Nhân viên thực hiện")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian thực hiện")

    class Meta:
        verbose_name = "Giao dịch kho"
        verbose_name_plural = "Lịch sử giao dịch kho"
        ordering = ['-created_at'] # Sắp xếp giảm dần (Mới nhất lên đầu)

    def __str__(self):
        return f"#{self.id} | {self.get_transaction_type_display()} - {self.product.name} (SL: {self.quantity})"

    def get_total_value(self):
        """Hàm tính tổng giá trị của một lần nhập kho"""
        return self.quantity * self.price