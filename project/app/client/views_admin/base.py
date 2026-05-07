from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Q
from django.db.models.functions import TruncDate, TruncMonth
from django.utils.text import slugify
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ObjectDoesNotExist

from apps.core.models import (
    Region, Store, Product, Order, Category, OrderItem, StockTransaction,
    ProductImage, Coupon, FlashSale, StoreStock, Notification,
    StockTransfer, StockTransferItem, Stocktaking, StocktakingItem, ProductVariation
)
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings as django_settings

# Import models bổ sung (Try/Except để tránh lỗi không tìm thấy bảng)
try:
    from apps.core.models import UserProfile, DefectiveProductStock, ReturnRequest, NewsArticle, NewsCategory
except ImportError:
    try:
        from ..models import UserProfile, DefectiveProductStock, ReturnRequest, NewsArticle, NewsCategory
    except ImportError:
        pass

# Import Decorator bảo mật tự làm (nằm ở thư mục cha)
from ..decorators import role_required

# Import utilities
from .utils import paginate_qs, ITEMS_PER_PAGE
