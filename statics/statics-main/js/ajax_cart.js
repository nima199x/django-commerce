(function() {
    function showToast(message, isError) {
        var existing = document.getElementById('ajax-cart-toast');
        if (existing) existing.remove();

        var toast = document.createElement('div');
        toast.id = 'ajax-cart-toast';
        toast.textContent = message;
        toast.style.cssText = [
            'position:fixed',
            'top:20px',
            'right:20px',
            'z-index:9999',
            'padding:12px 20px',
            'border-radius:6px',
            'font-size:14px',
            'font-weight:600',
            'color:#fff',
            'box-shadow:0 2px 10px rgba(0,0,0,0.2)',
            'background:' + (isError ? '#c0392b' : '#27ae60'),
            'transition:opacity 0.3s'
        ].join(';');
        document.body.appendChild(toast);

        setTimeout(function() {
            toast.style.opacity = '0';
            setTimeout(function() { toast.remove(); }, 300);
        }, 2500);
    }

    function updateCartHeader(count, total) {
        var cartTotalEl = document.getElementById('cart-total');
        if (cartTotalEl) {
            cartTotalEl.innerHTML = count + ' item(s) - ' + total;
        }
    }

    function handleAddToCart(e) {
        var link = e.currentTarget;
        if (link.classList.contains('disabled') || link.style.pointerEvents === 'none') {
            return;
        }
        e.preventDefault();

        var url = link.getAttribute('href');
        if (!url || url === '#') return;

        fetch(url, {
            method: 'GET',
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            credentials: 'same-origin'
        })
        .then(function(response) {
            return response.json().then(function(data) {
                return { ok: response.ok, data: data };
            });
        })
        .then(function(result) {
            if (result.ok && result.data.success) {
                showToast(result.data.message, false);
                updateCartHeader(result.data.cart_count, result.data.cart_total);
            } else {
                showToast(result.data.message || 'Something went wrong.', true);
            }
        })
        .catch(function() {
            showToast('Network error. Please try again.', true);
        });
    }

    document.addEventListener('DOMContentLoaded', function() {
        document.querySelectorAll('.ajax-add-to-cart').forEach(function(link) {
            link.addEventListener('click', handleAddToCart);
        });
    });
})();
