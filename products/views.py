from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import Category, Product, Review
from .serializers import CategorySerializer, ProductSerializer, ReviewSerializer
from django.template.loader import render_to_string
from django.contrib import messages
from django.urls import reverse
from orders.models import Cart, CartItem
import json

def get_unique_values(queryset, field):
    """Helper function to get unique values from a field in a queryset"""
    values = set()
    for item in queryset:
        field_value = getattr(item, field)
        if field_value:
            # Split the string if it contains multiple values
            if ',' in field_value:
                values.update(v.strip() for v in field_value.split(','))
            else:
                values.add(field_value.strip())
    return sorted(list(values))

def product_list(request, category_slug=None):
    categories = Category.objects.select_related().filter(is_active=True)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug, is_active=True)
        products = Product.objects.select_related('category').prefetch_related('images').filter(category=category, is_active=True)
    else:
        category = None
        products = Product.objects.select_related('category').prefetch_related('images').filter(is_active=True)
    
    # Pagination
    paginator = Paginator(products, 12)  # 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'categories': categories,
        'current_category': category,
    }
    return render(request, 'products/product_list.html', context)

def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related('category').prefetch_related('images', 'reviews__user'),
        slug=slug, 
        is_active=True
    )
    
    # Get related products
    related_products = Product.objects.select_related('category').prefetch_related('images').filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    # Get user's review if they're logged in
    user_review = None
    if request.user.is_authenticated:
        user_review = product.reviews.filter(user=request.user).first()
    
    context = {
        'product': product,
        'related_products': related_products,
        'user_review': user_review,
    }
    return render(request, 'products/product_detail.html', context)

@login_required
def add_review(request, slug):
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Invalid request method'
        }, status=405)

    try:
        data = json.loads(request.body)
        product = get_object_or_404(Product, slug=slug)
        
        # Validate rating
        try:
            rating = int(data.get('rating', 0))
            if not 1 <= rating <= 5:
                raise ValueError('Rating must be between 1 and 5')
        except (TypeError, ValueError) as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
        
        # Validate comment
        comment = data.get('comment', '').strip()
        if not comment:
            return JsonResponse({
                'success': False,
                'error': 'Comment is required'
            }, status=400)
        
        # Check if user has already reviewed this product
        review, created = Review.objects.get_or_create(
            product=product,
            user=request.user,
            defaults={
                'rating': rating,
                'comment': comment
            }
        )
        
        if not created:
            review.rating = rating
            review.comment = comment
            review.save()
            message = 'Your review has been updated successfully'
        else:
            message = 'Your review has been added successfully'
        
        return JsonResponse({
            'success': True,
            'message': message,
            'review': {
                'rating': review.rating,
                'comment': review.comment,
                'created_at': review.created_at.strftime('%B %d, %Y'),
                'user_name': review.user.get_full_name() or review.user.username
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def product_search(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.select_related('category').prefetch_related('images').filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__name__icontains=query),
            is_active=True
        )
    else:
        products = Product.objects.none()
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'query': query,
    }
    return render(request, 'products/search_results.html', context)

def product_filter(request):
    category_id = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort_by = request.GET.get('sort', 'name')
    
    products = Product.objects.select_related('category').prefetch_related('images').filter(is_active=True)
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    if min_price:
        products = products.filter(price__gte=min_price)
    
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Sorting
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('name')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.select_related().filter(is_active=True)
    
    context = {
        'products': page_obj,
        'categories': categories,
        'filters': {
            'category_id': category_id,
            'min_price': min_price,
            'max_price': max_price,
            'sort_by': sort_by,
        }
    }
    return render(request, 'products/product_list.html', context)

def product_reviews(request, slug):
    product = get_object_or_404(
        Product.objects.select_related('category').prefetch_related('reviews__user'),
        slug=slug, 
        is_active=True
    )
    
    reviews = product.reviews.select_related('user').order_by('-created_at')
    
    # Pagination for reviews
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'product': product,
        'reviews': page_obj,
    }
    return render(request, 'products/product_reviews.html', context)

# API Views
class ProductListAPI(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = Product.objects.all()
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__slug=category)
        return queryset

class ProductDetailAPI(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

class CategoryListAPI(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

def quick_view(request, product_id):
    product = get_object_or_404(
        Product.objects.select_related('category').prefetch_related('images'),
        id=product_id, 
        is_active=True
    )
    
    context = {
        'product': product,
    }
    return render(request, 'products/quick_view.html', context)

def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'redirect_url': f"{reverse('accounts:login')}?next={request.path}"
        })

    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    size = request.POST.get('size')
    color = request.POST.get('color')

    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        size=size,
        color=color,
        defaults={'quantity': quantity}
    )

    if not item_created:
        cart_item.quantity += quantity
        cart_item.save()

    cart_count = sum(item.quantity for item in cart.items.all())
    
    return JsonResponse({
        'success': True,
        'message': f'Added {quantity} item(s) to cart',
        'cart_count': cart_count
    })

@login_required
def add_to_wishlist(request, product_id):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'redirect_url': f"{reverse('accounts:login')}?next={request.path}"
        })

    product = get_object_or_404(Product, id=product_id)
    wishlist = request.user.wishlist
    
    if product in wishlist.products.all():
        wishlist.products.remove(product)
        added = False
    else:
        wishlist.products.add(product)
        added = True
    
    wishlist_count = wishlist.products.count()
    
    return JsonResponse({
        'success': True,
        'added': added,
        'wishlist_count': wishlist_count
    })

def categories_view(request):
    categories = Category.objects.all().order_by('name')
    return render(request, 'products/categories.html', {
        'categories': categories
    })

def product_list_by_category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug, is_active=True)
    products = Product.objects.select_related('category').prefetch_related('images').filter(
        category=category, 
        is_active=True
    )
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'category': category,
    }
    return render(request, 'products/category_products.html', context)
