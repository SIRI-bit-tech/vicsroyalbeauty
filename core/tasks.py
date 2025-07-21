from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
from django.contrib.sessions.models import Session
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_email_task(subject, message, from_email, recipient_list, fail_silently=True):
    """Send email asynchronously"""
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=fail_silently
        )
        logger.info(f"Email sent successfully to {recipient_list}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False

@shared_task
def send_contact_notification(name, email, subject, message):
    """Send contact form notification to admin"""
    admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@vicsroyalbeauty.com')
    
    email_subject = f'New Contact Message: {subject}'
    email_message = f"""
    New contact form submission:
    
    From: {name} ({email})
    Subject: {subject}
    Message:
    {message}
    """
    
    return send_email_task.delay(
        subject=email_subject,
        message=email_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[admin_email]
    )

@shared_task
def send_order_confirmation(order_id):
    """Send order confirmation email"""
    from orders.models import Order
    
    try:
        order = Order.objects.select_related('user').get(id=order_id)
        
        subject = f'Order Confirmation - Order #{order.id}'
        message = f"""
        Thank you for your order!
        
        Order Details:
        Order ID: {order.id}
        Total Amount: ₦{order.total_amount}
        Status: {order.get_status_display()}
        
        We'll keep you updated on your order status.
        """
        
        return send_email_task.delay(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.user.email]
        )
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found")
        return False

@shared_task
def cleanup_expired_sessions():
    """Clean up expired sessions"""
    try:
        expired_sessions = Session.objects.filter(expire_date__lt=timezone.now())
        count = expired_sessions.count()
        expired_sessions.delete()
        logger.info(f"Cleaned up {count} expired sessions")
        return count
    except Exception as e:
        logger.error(f"Failed to cleanup sessions: {str(e)}")
        return 0

@shared_task
def send_newsletter_digest():
    """Send daily newsletter digest"""
    from core.models import NewsletterSubscriber
    
    try:
        active_subscribers = NewsletterSubscriber.objects.filter(is_active=True)
        
        # Get today's promotions or news
        from core.models import Promotion
        today_promotions = Promotion.objects.filter(
            is_active=True,
            created_at__date=timezone.now().date()
        )
        
        if today_promotions.exists():
            subject = "Today's Special Offers - Vics Royal Beauty"
            message = "Check out today's special offers!\n\n"
            
            for promotion in today_promotions:
                message += f"- {promotion.title}: {promotion.description}\n"
            
            # Send to all active subscribers
            for subscriber in active_subscribers:
                send_email_task.delay(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[subscriber.email]
                )
            
            logger.info(f"Newsletter digest sent to {active_subscribers.count()} subscribers")
            return active_subscribers.count()
        else:
            logger.info("No promotions today, skipping newsletter digest")
            return 0
            
    except Exception as e:
        logger.error(f"Failed to send newsletter digest: {str(e)}")
        return 0

@shared_task
def clear_expired_cache():
    """Clear expired cache entries"""
    try:
        # This is handled automatically by Redis, but we can log cache stats
        cache_stats = cache.client.info()
        logger.info(f"Cache stats: {cache_stats}")
        return True
    except Exception as e:
        logger.error(f"Failed to clear cache: {str(e)}")
        return False

@shared_task
def update_product_cache():
    """Update product-related cache"""
    from products.models import Product, Category
    
    try:
        # Cache popular products
        popular_products = Product.objects.filter(
            is_active=True
        ).order_by('-views')[:10]
        
        cache.set('popular_products', list(popular_products), 1800)  # 30 minutes
        
        # Cache categories with product counts
        categories = Category.objects.filter(is_active=True)
        for category in categories:
            product_count = category.products.filter(is_active=True).count()
            cache.set(f'category_{category.id}_count', product_count, 3600)  # 1 hour
        
        logger.info("Product cache updated successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to update product cache: {str(e)}")
        return False

@shared_task
def process_image_upload(image_path):
    """Process uploaded images asynchronously"""
    try:
        # This would handle image processing tasks
        # For now, just log the task
        logger.info(f"Processing image: {image_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to process image {image_path}: {str(e)}")
        return False 