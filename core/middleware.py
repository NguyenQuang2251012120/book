from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from urllib.parse import urlunparse

User = get_user_model()

class DomainRestrictionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        full_host = request.get_host().split(":")[0]  # VD: quang123.127.0.0.1.sslip.io
        scheme = "https" if request.is_secure() else "http"
        port = request.get_port()

        # Các URL public (không cần đăng nhập)
        public_paths = ["/login/", "/login1/", "/register/"]

        # Nếu người dùng truy cập "/", mà ở public schema → redirect đến login
        if path == "/" and request.tenant.schema_name == "public":
            return redirect("/login/")

        # Cho phép truy cập các đường dẫn public
        if path in public_paths:
            return self.get_response(request)

        user = request.user
        if user.is_authenticated:
            schema_name = user.schema_name

            # Nếu domain hiện tại không đúng với schema, redirect đến đúng domain
            if schema_name and not full_host.startswith(schema_name):
                corrected_domain = f"{schema_name}.{'.'.join(full_host.split('.')[1:])}"
                netloc = f"{corrected_domain}:{port}" if port != "80" else corrected_domain
                login1_url = urlunparse((scheme, netloc, "/login1/", "", "", ""))
                return redirect(login1_url)

        elif path not in public_paths:
            return HttpResponseForbidden("Bạn cần đăng nhập để truy cập trang này!")

        return self.get_response(request)
