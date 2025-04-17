import psycopg2
from django.conf import settings
# core/utils.py

def get_current_tenant(request):
    # Kiểm tra xem session có tồn tại không và lấy tên tenant từ session
    tenant_name = request.session.get('tenant', None)
    return tenant_name


# core/utils.py


def create_tenant_database(tenant_name):
    # Kết nối tới database chính để tạo database mới cho tenant
    connection = psycopg2.connect(
        dbname='quanlysach',  # Đây là database chính, nơi lưu thông tin các tenant
        user=settings.DATABASES['default']['USER'],
        password=settings.DATABASES['default']['PASSWORD'],
        host=settings.DATABASES['default']['HOST'],
        port=settings.DATABASES['default']['PORT'],
    )
    connection.autocommit = True
    cursor = connection.cursor()

    # Tạo database cho tenant
    cursor.execute(f"CREATE DATABASE {tenant_name};")
    connection.close()

