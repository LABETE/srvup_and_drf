import datetime
import random

from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone

from .signals import membership_dates_update
from .utils import update_braintree_membership


def user_logged_in_receiver(sender, user, **kwargs):
    update_braintree_membership(user)

user_logged_in.connect(user_logged_in_receiver)


class UserMerchantId(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    customer_id = models.CharField(max_length=120)
    subscription_id = models.CharField(max_length=120, null=True, blank=True)
    plan_id = models.CharField(max_length=120, null=True, blank=True)
    merchant_name = models.CharField(max_length=120, default="Braintree")

    def __str__(self):
        return self.customer_id


class Membership(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.user.username)

    def update_status(self):
        if self.end_date >= timezone.now() and not self.user.is_member:
            self.user.is_member = True
            self.user.save()
        elif self.end_date <= timezone.now() and self.user.is_member:
            self.user.is_member = False
            self.user.save()


def update_membership_status(sender, instance, created, *args, **kwargs):
    if not created:
        instance.update_status()


post_save.connect(update_membership_status, sender=Membership)


def update_membership_dates(sender, new_start_date, **kwargs):
    membership = sender
    current_end_date = membership.end_date
    if current_end_date >= new_start_date:
        membership.end_date = current_end_date + \
            datetime.timedelta(days=30, hours=10)
        membership.save()
    else:
        membership.start_date = new_start_date
        membership.end_date = new_start_date + \
            datetime.timedelta(days=30, hours=10)
        membership.save()

membership_dates_update.connect(update_membership_dates)


class TransactionManager(models.Manager):

    def create_new(self, user, transaction_id, amount, card_type,
                   success=None, last_four=None, transaction_status=None):
        if not user:
            raise ValueError("Must be a user.")
        if not transaction_id:
            raise ValueError("Must complete a transaction to add new.")
        new_order_id = "{0}{1}{2}".format(
            transaction_id[:2], random.randint(1, 9), transaction_id[2:])
        new_trans = self.model(
            user=user,
            transaction_id=transaction_id,
            amount=amount,
            order_id=new_order_id,
            card_type=card_type
        )
        if success:
            new_trans.success = success
        if last_four:
            new_trans.last_four = last_four
        if transaction_status:
            new_trans.transaction_status = transaction_status
        new_trans.save(using=self._db)
        return new_trans


class Transaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    transaction_id = models.CharField(max_length=120)
    order_id = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=100, decimal_places=2)
    success = models.BooleanField(default=True)
    transaction_status = models.CharField(
        max_length=220, null=True, blank=True)
    card_type = models.CharField(max_length=120)
    last_four = models.PositiveIntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

    objects = TransactionManager()

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return self.order_id
