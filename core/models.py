from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        SALES = 'SALES', 'Ventas'
        CALLCENTER = 'CALLCENTER', 'Callcenter'
        PRODUCTION = 'PRODUCTION', 'Producción'
        LOGISTICS = 'LOGISTICS', 'Logística'

    role = models.CharField(
        max_length=50,
        choices=Role.choices,
        default=Role.ADMIN,
    )


class Product(models.Model):
    class Line(models.TextChoices):
        MAGISTRAL = 'MAGISTRAL', 'Magistral'
        ORAL = 'ORAL', 'Oral'
        TERMINADO = 'TERMINADO', 'Terminado'
        MUESTRAS = 'MUESTRAS', 'Muestras'

    class Status(models.TextChoices):
        DISPONIBLE = 'DISPONIBLE', 'Disponible'
        AGOTADO = 'AGOTADO', 'Agotado'
        DESCONTINUADO = 'DESCONTINUADO', 'Descontinuado'

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True)
    composition = models.CharField(max_length=255)
    line = models.CharField(max_length=50, choices=Line.choices)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.DISPONIBLE)

    def __str__(self):
        return f'{self.name} ({self.code})'


class Customer(models.Model):
    class CustomerType(models.TextChoices):
        HOSPITAL = 'HOSPITAL', 'Hospital'
        CLINICA = 'CLINICA', 'Clínica'
        FARMACIA = 'FARMACIA', 'Farmacia'
        DISTRIBUIDOR = 'DISTRIBUIDOR', 'Distribuidor'

    name = models.CharField(max_length=200)
    nit = models.CharField(max_length=50, unique=True)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    customer_type = models.CharField(max_length=50, choices=CustomerType.choices)

    def __str__(self):
        return self.name


class Order(models.Model):
    class OrderStatus(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        EN_PROCESO = 'EN_PROCESO', 'En Proceso'
        ENTREGADO = 'ENTREGADO', 'Entregado'
        CANCELADO = 'CANCELADO', 'Cancelado'

    order_number = models.CharField(max_length=50, unique=True, editable=False)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='orders')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=50, choices=OrderStatus.choices, default=OrderStatus.PENDIENTE)
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            last_order = Order.objects.all().order_by('id').last()
            new_id = (last_order.id + 1) if last_order else 1
            self.order_number = f'ORD-{timezone.now().strftime("%Y%m%d")}-{new_id:04d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.quantity} x {self.product.name} in order {self.order.order_number}'
