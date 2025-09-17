from django.core.management.base import BaseCommand
from core.models import Product, Customer

class Command(BaseCommand):
    help = 'Loads initial data for the application'

    def handle(self, *args, **options):
        self.stdout.write('Loading initial product data...')
        Product.objects.all().delete()
        products_to_create = [
            # ... product data from before ...
            {
                'code': 'ACE500', 'name': 'Acetaminofén 500mg', 'description': 'Tabletas recubiertas',
                'composition': 'Acetaminofén 500mg', 'line': 'MAGISTRAL', 'price': 2500.00, 'status': 'DISPONIBLE'
            },
            {
                'code': 'IBU400', 'name': 'Ibuprofeno 400mg', 'description': 'Cápsulas blandas',
                'composition': 'Ibuprofeno 400mg', 'line': 'ORAL', 'price': 3200.00, 'status': 'DISPONIBLE'
            },
            {
                'code': 'AMX500', 'name': 'Amoxicilina 500mg', 'description': 'Suspensión oral',
                'composition': 'Amoxicilina 500mg/5ml', 'line': 'TERMINADO', 'price': 4800.00, 'status': 'AGOTADO'
            },
            {
                'code': 'MUE001', 'name': 'Muestra Vitamina C', 'description': 'Muestra médica',
                'composition': 'Ácido Ascórbico 1000mg', 'line': 'MUESTRAS', 'price': 0.00, 'status': 'DISPONIBLE'
            }
        ]
        for data in products_to_create:
            Product.objects.create(**data)
        self.stdout.write(self.style.SUCCESS('Successfully loaded product data.'))

        self.stdout.write('Loading initial customer data...')
        Customer.objects.all().delete()
        customers_to_create = [
            {
                'name': 'Hospital San Juan de Dios', 'nit': '890.123.456-1', 'address': 'Calle 45 # 23-67',
                'city': 'Bogotá D.C.', 'customer_type': 'HOSPITAL'
            },
            {
                'name': 'Clínica del Norte', 'nit': '890.987.654-3', 'address': 'Carrera 15 # 85-32',
                'city': 'Medellín', 'customer_type': 'CLINICA'
            },
            {
                'name': 'Farmacia Central', 'nit': '890.555.777-9', 'address': 'Avenida 68 # 12-45',
                'city': 'Cali', 'customer_type': 'FARMACIA'
            },
            {
                'name': 'Distribuidora Salud Total', 'nit': '890.333.888-2', 'address': 'Zona Industrial Km 5',
                'city': 'Barranquilla', 'customer_type': 'DISTRIBUIDOR'
            }
        ]
        for data in customers_to_create:
            Customer.objects.create(**data)
        self.stdout.write(self.style.SUCCESS('Successfully loaded customer data.'))
