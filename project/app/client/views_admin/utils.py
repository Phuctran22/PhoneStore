from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

ITEMS_PER_PAGE = 15

def paginate_qs(request, queryset, per_page=ITEMS_PER_PAGE):
    """Phân trang queryset. Trả về (page_obj, preserved_filters)"""
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    # Preserve existing GET params (trừ 'page') cho pagination links
    params = request.GET.copy()
    if 'page' in params:
        del params['page']
    preserved = params.urlencode()
    
    return page_obj, preserved
