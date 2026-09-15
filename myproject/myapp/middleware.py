from django.shortcuts import redirect

class BlockSellerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and hasattr(request.user, "seller_profile"):
            allowed_prefixes = [
                '/seller',
                '/all_sell_books',
                '/all_exchange_books',
                '/logout',
                '/media',
                '/static',
                '/admin',
                '/login',
                '/registration'
            ]
            if not any(request.path.startswith(prefix) for prefix in allowed_prefixes):
                return redirect('seller_profile')
        
        response = self.get_response(request)
        return response
