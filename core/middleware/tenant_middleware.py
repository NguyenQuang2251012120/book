# core/middleware/tenant_middleware.py

from core.middleware.threadlocals import set_current_tenant_db

class TenantMiddleware:

    def get_tenant_from_request(self, request):
        # Kiểm tra xem tenant đã được lưu trong session hay chưa
        tenant_name = request.session.get('tenant', None)

        if tenant_name:
            return tenant_name

        # Nếu không có tenant trong session, lấy tenant mặc định hoặc từ cookie
        tenant_name = request.COOKIES.get('tenant', 'default_tenant')
        return tenant_name

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Xác định tenant từ request (ví dụ: từ subdomain, session, hoặc token)
        tenant_db = self.get_tenant_from_request(request)

        # Đảm bảo tenant_db hợp lệ trước khi lưu vào thread-local
        if tenant_db:
            set_current_tenant_db(tenant_db)

        response = self.get_response(request)
        return response
