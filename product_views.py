from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum
from django.http import JsonResponse
from apps.core.models import Product, Category, Review
from django.contrib import messages
from django.utils import timezone

def home(request):
    category_id = request.GET.get('category')
    products = Product.objects.all().order_by('-id')

    if category_id:
        products = products.filter(category_id=category_id)

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.page(page_number)
    except:
        page_obj = paginator.page(1)

    categories = Category.objects.all()

    return render(request, 'client/home.html', {
        'products': page_obj,
        'categories': categories
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all()

    return render(request, 'client/product_detail.html', {
        'product': product,
        'reviews': reviews
    })


def search_view(request):
    query = request.GET.get('q', '')
    results = Product.objects.filter(name__icontains=query)

    paginator = Paginator(results, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'client/search_results.html', {
        'results': page_obj,
        'query': query
    })


def api_search_autocomplete(request):
    q = request.GET.get('q', '')
    products = Product.objects.filter(name__icontains=q)[:8]

    data = [{
        'id': p.id,
        'name': p.name,
        'price': int(p.price),
    } for p in products]

    return JsonResponse({'suggestions': data})
