from decimal import Decimal
from apps.core.models import Product 

class Cart(object):
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False, variation_id=None):
        """
        Thêm sản phẩm vào giỏ hàng hoặc cập nhật số lượng của nó.
        """
        var_str = str(variation_id) if variation_id else "0"
        item_key = f"{product.id}_{var_str}"
        
        if item_key not in self.cart:
            price_to_save = product.flash_sale.flash_price if hasattr(product, 'flash_sale') and product.flash_sale.is_valid() and product.flash_sale.flash_price else product.price
            
            self.cart[item_key] = {
                'product_id': str(product.id),
                'variation_id': var_str,
                'quantity': 0,
                'price': str(price_to_save)
            }
            
        if override_quantity:
            self.cart[item_key]['quantity'] = quantity
        else:
            self.cart[item_key]['quantity'] += quantity
            
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product, variation_id=None):
        """Xóa sản phẩm khỏi giỏ."""
        var_str = str(variation_id) if variation_id else "0"
        item_key = f"{product.id}_{var_str}"

        if item_key in self.cart:
            del self.cart[item_key]
            self.save()

    def __iter__(self):
        """
        Lặp qua các item trong giỏ hàng và lấy object Product từ Database.
        """
        product_ids = []
        var_ids = []
        for key, item in self.cart.items():
            if 'product_id' not in item: continue
            product_ids.append(int(item['product_id']))
            if item.get('variation_id', '0') != '0':
                try: var_ids.append(int(item['variation_id']))
                except: pass

        products = Product.objects.filter(id__in=product_ids)
        product_dict = {str(p.id): p for p in products}

        from apps.core.models import ProductVariation
        variations = ProductVariation.objects.filter(id__in=var_ids)
        var_dict = {str(v.id): v for v in variations}

        cart_copy = {}
        for key, value in self.cart.items():
            if 'product_id' in value:
                cart_copy[key] = value.copy()

        for key in list(cart_copy.keys()):
            item = cart_copy[key]
            pid = str(item['product_id'])
            if pid in product_dict:
                item['product'] = product_dict[pid]
                try:
                    price_val = Decimal(str(item['price']))
                except:
                    price_val = Decimal(0)

                vid = item.get('variation_id', '0')
                if vid != '0' and vid in var_dict:
                    var_obj = var_dict[vid]
                    item['variation'] = var_obj
                    if 'price_var_added' not in item:
                        price_val += Decimal(str(var_obj.additional_price or 0)) 
                else:
                    item['variation'] = None
                
                item['price'] = price_val
                item['total_price'] = item['price'] * item['quantity']
                yield item
            else:
                if key in self.cart:
                    del self.cart[key]
                    self.save()

    def __len__(self):
        """Đếm số lượng tất cả item trong giỏ."""
        return sum(item['quantity'] for item in self.cart.values())

    def clear(self):
        """Xóa sạch giỏ hàng."""
        del self.session['cart']
        self.save()

    def get_total_price(self):
        """Tính tổng số tiền của toàn bộ giỏ hàng."""
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())
