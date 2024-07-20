from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=30, decimal_places=2)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    ACCOUNT_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=ACCOUNT_TYPES)
    amount = models.DecimalField(max_digits=30, decimal_places=2)
    category = models.CharField(max_length=100)
    date = models.DateField()
    note = models.TextField(blank=True, null=True)
    previous_balance = models.DecimalField(max_digits=30, decimal_places=2, default=0)
    current_balance = models.DecimalField(max_digits=30, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.previous_balance = self.account.balance
        if self.type == 'income':
            self.account.balance += self.amount
        else:
            self.account.balance -= self.amount
        self.current_balance = self.account.balance
        self.account.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.account.name} - {self.type} - {self.amount}'
