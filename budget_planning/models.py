from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from money_management.models import Account, Transaction

User = get_user_model()

PLAN_TYPE_CHOICES = (
    ('income', 'Доход'),
    ('expense', 'Расход'),
)


class Plan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50)
    note = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField()
    is_completed = models.BooleanField(default=False)
    is_failed = models.BooleanField(default=False)
    previous_balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    current_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    limit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f'{self.category} - {self.amount}'


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} - {self.message}'

    @staticmethod
    def create_notification(user, message):
        Notification.objects.create(user=user, message=message)

