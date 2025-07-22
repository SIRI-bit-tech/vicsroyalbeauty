// Quick view functionality
function quickView(productId) {
    fetch(`/products/quick-view/${productId}/`)
        .then(response => response.text())
        .then(html => {
            const modal = document.getElementById('quickViewModal');
            modal.innerHTML = html;
            // Show modal using Bootstrap
            new bootstrap.Modal(modal).show();
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error loading product details', 'error');
        });
}

// Add to wishlist functionality
function toggleWishlist(productId) {
    if (!isAuthenticated) {
        window.location.href = '/accounts/login/';
        return;
    }

    fetch(`/products/add-to-wishlist/${productId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const wishlistIcon = document.querySelector(`[data-wishlist-product="${productId}"] i`);
                if (data.added) {
                    wishlistIcon.classList.remove('far');
                    wishlistIcon.classList.add('fas');
                    showNotification('Added to wishlist!', 'success');
                } else {
                    wishlistIcon.classList.remove('fas');
                    wishlistIcon.classList.add('far');
                    showNotification('Removed from wishlist!', 'success');
                }
                updateWishlistCount(data.wishlist_count);
            } else if (data.redirect_url) {
                window.location.href = data.redirect_url;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error updating wishlist', 'error');
        });
}

// Add to cart functionality
function addToCart(productId, quantity = 1, size = null, color = null) {
    if (!isAuthenticated) {
        window.location.href = '/accounts/login/';
        return;
    }

    const formData = new FormData();
    formData.append('quantity', quantity);
    if (size) formData.append('size', size);
    if (color) formData.append('color', color);

    fetch(`/products/add-to-cart/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                updateCartCount(data.cart_count);
            } else if (data.redirect_url) {
                window.location.href = data.redirect_url;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error adding to cart', 'error');
        });
}

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Helper function to show notifications
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);

    // Show notification
    setTimeout(() => notification.classList.add('show'), 100);

    // Hide and remove notification after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Update cart count in the UI
function updateCartCount(count) {
    const cartCountElement = document.getElementById('cart-count');
    if (cartCountElement) {
        cartCountElement.textContent = count;
    }
}

// Update wishlist count in the UI
function updateWishlistCount(count) {
    const wishlistCountElement = document.getElementById('wishlist-count');
    if (wishlistCountElement) {
        wishlistCountElement.textContent = count;
    }
}
