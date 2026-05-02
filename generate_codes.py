import os
import django
import random
import string

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tms_project.settings')
django.setup()

from core.models import SchoolRegistrationCode

def generate_codes(count=10):
    for _ in range(count):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        # Ensure uniqueness
        while SchoolRegistrationCode.objects.filter(code=code).exists():
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        
        SchoolRegistrationCode.objects.create(code=code)
        print(f"Generated Code: {code}")

if __name__ == '__main__':
    generate_codes()
    print("Registration codes generated successfully!")
