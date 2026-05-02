import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tms_project.settings')
django.setup()

from core.models import User

def create_admin():
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser('admin', 'admin@example.com', 'adminpass123')
        admin.is_admin = True
        admin.save()
        print("Admin user created (username: admin, password: adminpass123)")
    else:
        print("Admin user already exists")

if __name__ == '__main__':
    create_admin()
