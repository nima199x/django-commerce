from functools import wraps
from django.core.cache import cache
from django.contrib import messages
from django.shortcuts import redirect


def rate_limit(key_prefix, limit=5, period=300, redirect_to=None):
    """
    Limits how many times a view can be called (via POST) from the same IP
    within `period` seconds. Only counts POST requests so page loads (GET)
    are never blocked.

    Usage:
        @rate_limit('login', limit=5, period=300)
        def login_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.method == 'POST':
                ip = request.META.get('REMOTE_ADDR', 'unknown')
                cache_key = f'ratelimit:{key_prefix}:{ip}'
                count = cache.get(cache_key, 0)

                if count >= limit:
                    messages.error(
                        request,
                        'Too many attempts. Please wait a few minutes and try again.'
                    )
                    target = redirect_to or request.META.get('HTTP_REFERER', 'home')
                    return redirect(target)

                cache.set(cache_key, count + 1, period)

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
