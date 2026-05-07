from .dashboard import dashboard, export_monthly_revenue_excel
from .regions import region_list, region_add, region_edit, region_delete
from .stores import store_list, store_add, store_edit, store_delete
from .products import product_list, product_add, product_edit, product_delete, category_edit, category_delete, delete_product_image
from .orders import order_list, order_detail, print_invoice_view
from .stock import admin_stock_management, stock_transaction_create, print_stock_transaction, store_detail
from .transfers import transfer_list, transfer_create, transfer_detail, transfer_action
from .stocktaking import stocktaking_list, stocktaking_create, stocktaking_detail, stocktaking_action
from .employees import admin_employee_list
from .flash_sales import admin_flash_sale, delete_flash_sale
from .coupons import admin_coupon_list, admin_coupon_delete
from .excel import export_products_excel, import_products_excel, export_orders_excel, download_product_template
from .returns import admin_return_list, admin_return_detail
from .news import admin_news_list, admin_news_create, admin_news_edit, admin_news_delete, admin_news_category
