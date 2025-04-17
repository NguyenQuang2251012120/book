# core/middleware/threadlocals.py

import threading

# Tạo một thread-local để lưu thông tin về tenant
_thread_locals = threading.local()

def set_current_tenant_db(db_name):
    """Gán tên database của tenant vào thread-local"""
    _thread_locals.current_tenant_db = db_name

def get_current_tenant_db():
    """Lấy tên database của tenant từ thread-local"""
    return getattr(_thread_locals, 'current_tenant_db', None)


def get_current_tenant():
    return getattr(_thread_locals, 'tenant_name', None)

