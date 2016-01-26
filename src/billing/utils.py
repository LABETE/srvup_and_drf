import datetime

from django.utils import timezone

import braintree

from .signals import membership_dates_update


def check_membership_status(subscription_id):
    sub = braintree.Subscription.find(subscription_id)
    if sub.status == "Active":
        status = True
        next_billing_date = sub.next_billing_date
    else:
        status = False
        next_billing_date = None
    return status, next_billing_date


def update_braintree_membership(user):
    membership = user.membership
    subscription_id = user.usermerchantid.subscription_id
    if membership.end_date <= timezone.now() and subscription_id:
        status, next_billing_date = check_membership_status(subscription_id)
        if status:
            small_time = datetime.time(0, 0, 0, 1)
            datetime_obj = datetime.datetime.combine(
                next_billing_date, small_time)
            datetime_aware = timezone.make_aware(
                datetime_obj, timezone.get_current_timezone())
            membership_dates_update.send(
                membership, new_start_date=datetime_aware)
        else:
            membership.update_status()
    else:
        membership.update_status()
