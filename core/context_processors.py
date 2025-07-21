from django.conf import settings

def error_tracking_settings(request):
    return {
        'GLITCHTIP_DSN': settings.GLITCHTIP_DSN if hasattr(settings, 'GLITCHTIP_DSN') else None,
    }

def breadcrumbs(request):
    """
    Adds breadcrumb data to the context.
    Only shows breadcrumbs on specific pages.
    """
    # List of URL patterns where breadcrumbs should be shown
    breadcrumb_paths = [
        '/products/',
        '/checkout/',
        '/orders/',
        '/cart/',
    ]
    
    # Check if current path should show breadcrumbs
    show_breadcrumbs = any(request.path.startswith(path) for path in breadcrumb_paths)
    
    if not show_breadcrumbs:
        return {'show_breadcrumbs': False, 'breadcrumbs': []}
    
    path_parts = [p for p in request.path.split('/') if p]
    breadcrumbs = []
    current_path = ''
    
    # Add home as first breadcrumb
    breadcrumbs.append({
        'name': 'Home',
        'url': '/'
    })
    
    # Add subsequent breadcrumbs
    for i, part in enumerate(path_parts):
        current_path += f'/{part}'
        name = part.replace('-', ' ').title()
        
        # Customize names for specific sections
        if part == 'products':
            name = 'Shop'
        elif part == 'checkout':
            name = 'Checkout'
        elif part == 'orders':
            name = 'Orders'
        elif part == 'cart':
            name = 'Cart'
        elif part.isdigit() and i > 0 and path_parts[i-1] == 'orders':
            # This is an order ID, show it as "Order #X"
            name = f'Order #{part}'
        
        breadcrumbs.append({
            'name': name,
            'url': current_path
        })
    
    return {
        'show_breadcrumbs': True,
        'breadcrumbs': breadcrumbs
    } 