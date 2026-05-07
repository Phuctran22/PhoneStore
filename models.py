class ProductImage(models.Model):
    """
    Bảng Album Ảnh bổ sung: Một sản phẩm có thể có nhiều ảnh phụ (Quan hệ 1-N)
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name="Sản phẩm")
    image = models.ImageField(upload_to='products/gallery/', verbose_name="Hình ảnh")

    def __str__(self):
        return f"Ảnh phụ của {self.product.name}"
