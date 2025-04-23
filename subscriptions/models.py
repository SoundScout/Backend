from django.db import models
from users.models import Artist  # import from users app

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=20, unique=True)
    max_upload_rate = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} Plan (${self.price})"

class Subscription(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
    ]

    # Changed to ForeignKey with unique=True for future history
    artist = models.OneToOneField(Artist, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    end_subscription = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    is_active = models.BooleanField(default=True)

    # Cached values (copied from plan at creation)
    max_upload_rate = models.IntegerField(default=4)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        if self.plan:
            self.max_upload_rate = self.plan.max_upload_rate
            self.price = self.plan.price

        # Keep is_active in sync with status
        self.is_active = (self.status == 'active')
        super().save(*args, **kwargs)

    def __str__(self):
        plan_name = self.plan.name if self.plan else 'No Plan'
        return f"{self.artist.user.username} - {plan_name} Subscription"

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['end_subscription']),
        ]