from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('store-locations/', views.store_locations, name='store_locations'),
    path('promotions/', views.promotions, name='promotions'),
    
    # Health check endpoints
    path('health/', views.health_check, name='health_check'),
    path('status/', views.status_check, name='status_check'),
    
    # Admin views
    path('admin/newsletter/', views.admin_newsletter, name='admin_newsletter'),
    path('admin/newsletter/delete/<int:subscriber_id>/', views.delete_subscriber, name='delete_subscriber'),
    path('admin/newsletter/send/', views.send_newsletter, name='send_newsletter'),
    
    # User views
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    
    # Newsletter subscription
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    
    # Error logging
    path('log-error/', views.log_javascript_error, name='log_javascript_error'),
] 