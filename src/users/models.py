from django.contrib import messages
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.contrib.auth.signals import user_logged_in
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.shortcuts import redirect
from django.utils import timezone


import braintree

from billing.models import Membership, UserMerchantId
from notifications.signals import notify

braintree.Configuration.configure(braintree.Environment.Sandbox,
                                  merchant_id=settings.MERCHANT_ID,
                                  public_key=settings.PUBLIC_KEY,
                                  private_key=settings.PRIVATE_KEY)


class UserManager(BaseUserManager):

    def create_user(self, username=None, email=None, password=None):
        """
        Creates and saves a User with the given username, email and password.
        """
        if not username:
            raise ValueError('Users must have an username')
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            username=username,
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        """
        Creates and saves a superuser with the given username,
        email and password.
        """
        user = self.create_user(
            username=username,
            email=email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    username = models.CharField(
        max_length=255,
        unique=True,
    )
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    first_name = models.CharField(max_length=120, null=True, blank=True)
    last_name = models.CharField(max_length=120, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_member = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def get_full_name(self):
        # The user is identified by their frist and last name
        return "{0} {1}".format(self.first_name, self.last_name)

    def get_short_name(self):
        # The user is identified by their first name
        return self.first_name

    def __str__(self):              # __unicode__ on Python 2
        return self.username

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


def user_logged_in_signal(sender, signal, user, **kwargs):
    membership_obj, created = Membership.objects.get_or_create(user=user)
    if created:
        membership_obj.start_date = timezone.now()
        membership_obj.save()
        user.is_member = True
        user.save()
    user.membership.update_status()


user_logged_in.connect(user_logged_in_signal)


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    bio = models.TextField(null=True, blank=True)
    facebook_link = models.CharField(
        max_length=320, null=True, blank=True,
        verbose_name='Facebook profile url')
    twitter_handle = models.CharField(
        max_length=320, null=True, blank=True, verbose_name='Twitter handle')

    def __str__(self):
        return self.user.username


def new_user_receiver(sender, instance, created, *args, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
        notify.send(instance,
                    recipient=User.objects.get(username="labete"),
                    verb="New User created.")
    try:
        merchant_obj = UserMerchantId.objects.get(user=instance)
    except UserMerchantId.DoesNotExist:
        new_customer_result = braintree.Customer.create({
            "email": instance.email
        })
        if new_customer_result.is_success:
            merchant_obj, created = UserMerchantId.objects.\
                get_or_create(user=instance)
            merchant_obj.customer_id = new_customer_result.customer.id
            merchant_obj.save()
            print("Customer created with id = {0}".format(
                new_customer_result.customer.id))
        else:
            messages.error(instance, "Error: {0}. Please Contact us.".format(
                new_customer_result.message))
            return redirect("contact")


post_save.connect(new_user_receiver, sender=User)
