from .home import home
from .search import search_view, api_search_autocomplete
from .cart import cart_detail, cart_add, cart_remove, cart_update, apply_coupon, remove_coupon
from .products import product_detail
from .store_locator import store_locator
from .checkout import checkout, payment_instruction_view, client_print_receipt
from .auth import register_view, verification_pending, verify_email, forgot_password, resend_verification, reset_password, login_view, logout_view
from .account import user_account, my_orders, order_detail, cancel_order, request_return_view, return_history_view, feedback_view
from .notifications import notifications_list, mark_notification_read, mark_all_notifications_read
from .policies import policy_warranty, policy_return, policy_guide
from .api import ai_chat_api, api_search_stock
from .news import news_list, news_detail
from .errors import error_404
