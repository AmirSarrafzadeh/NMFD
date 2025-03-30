from django.core import signing
from django.contrib.auth import get_user_model, login


class AutoLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            token = request.COOKIES.get('login_token')
            if token:
                try:
                    signer = signing.TimestampSigner()
                    email = signer.unsign(token, max_age=300)
                    User = get_user_model()
                    user = User.objects.get(email=email)
                    login(request, user)
                except Exception as e:
                    print("Auto-login failed:", e)

        response = self.get_response(request)
        return response
