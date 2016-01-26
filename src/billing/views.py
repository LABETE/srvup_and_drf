from django.contrib import messages
from django.conf import settings
from django.shortcuts import redirect
from django.views.generic.edit import CreateView
from django.views.generic.base import RedirectView
from django.views.generic.list import ListView
from django.utils import timezone

from braces.views import LoginRequiredMixin

from .models import Transaction, Membership, UserMerchantId
from .signals import membership_dates_update

import braintree


def get_or_create_model_transaction(request, braintree_transaction):
    user = request.user
    trans_id = braintree_transaction.id
    try:
        trans = Transaction.objects.get(user=user, transaction_id=trans_id)
    except:
        try:
            credit_card_details = braintree_transaction.credit_card_details
            card_type = credit_card_details.card_type
            last_4 = credit_card_details.last_4
        except:
            card_type = "PayPal"
            last_4 = ""
        try:
            amount = braintree_transaction.amount
            trans = Transaction.objects.create_new(
                user, trans_id, amount,
                card_type, last_four=last_4)
        except:
            messages.error(request, """An error occurred with your Transaction.
                Please Contact us.""")
            return redirect("contact")
    return trans


def update_transactions(request):
    user = request.user
    bt_transactions = braintree.Transaction.search(
            braintree.TransactionSearch.customer_id == user.usermerchantid.customer_id
        )
    print(bt_transactions)
    try:
        django_transactions = user.transaction_set.all()
    except:
        django_transactions = None

    if bt_transactions and django_transactions:
        if bt_transactions.maximum_size > django_transactions.count():
            for bt_tran in bt_transactions.items:
                new_tran = get_or_create_model_transaction(request, bt_tran)


class CancelSubscriptionView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get(self, *args, **kwargs):
        sub_id = self.request.user.usermerchantid.subscription_id
        if sub_id:
            result = braintree.Subscription.cancel(sub_id)
            if result.is_success:
                self.request.user.usermerchantid.subscription_id = None
                self.request.user.usermerchantid.save()
                messages.success(self.request, "Your account has been successfuly cancelled.")
            else:
                messages.error(self.request, "There was an error with your account, please contact us.")
                redirect("contact")
        else:
            messages.error(self.request, "You do not have an active subscription.")
        return redirect("billing:list")


class BillingUpgradeView(LoginRequiredMixin, CreateView):
    template_name = "billing/upgrade.html"
    model = Membership
    fields = ["user"]

    def get_context_data(self, *args, **kwargs):
        context = super(BillingUpgradeView, self).get_context_data(
            *args, **kwargs)
        try:
            merchant_obj = UserMerchantId.objects.get(
                user=self.request.user)
            merchant_customer_id = merchant_obj.customer_id
        except:
            messages.error(self.request,
                """An error occurred with your account.
                Please Contact us.""")
            return redirect("contact")
        try:
            client_token = braintree.ClientToken.generate({
                "customer_id": merchant_customer_id
            })
        except:
            client_token = braintree.ClientToken.generate()

        context["client_token"] = client_token
        return context

    def post(self, *args, **kwargs):
        # context = self.get(self.get_context_data)
        # merchant_customer_id = context.context_data["merchant_customer_id"]
        try:
            merchant_obj = UserMerchantId.objects.get(
                user=self.request.user)
            merchant_customer_id = merchant_obj.customer_id
            current_sub_id = merchant_obj.subscription_id
        except:
            messages.error(self.request,
                """An error occurred with your account.
                Please Contact us.""")
            return redirect("contact")

        nonce = self.request.POST.get("payment_method_nonce", None)
        try:
            payment_method_result = braintree.PaymentMethod.create({
                    "customer_id": merchant_customer_id,
                    "payment_method_nonce": nonce,
                    "options": {
                        "make_default": True
                    }
                })
        except:
            messages.error(self.request,
                    "An error occurred {0}".format(
                        payment_method_result.message)
                    )
            return redirect("contact")
        token = payment_method_result.payment_method.token
        try:
            current_subscription = braintree.Subscription.find(
                current_sub_id)
            status = current_subscription.status
        except:
            status = None
        if status == "Active":
            plan_updated = braintree.Subscription.update(
                current_sub_id, {
                    "payment_method_token": token
                })
            if plan_updated.is_success:
                membership_instance = Membership.objects.get_or_create(
                    user=self.request.user)[0]
                membership_dates_update.send(membership_instance,
                    new_start_date=timezone.now())
                messages.success(self.request,
                    "Your plan has been updated.")
                return redirect("billing:list")
            else:
                messages.error(self.request,
                    "An error occurred, please try again later.")
                redirect("contact")
        subscription_result = braintree.Subscription.create({
                "payment_method_token": token,
                "plan_id": settings.PLAN_ID
            })
        if subscription_result.is_success:
            merchant_obj.subscription_id = subscription_result.subscription.id
            merchant_obj.plan_id = subscription_result.subscription.plan_id
            merchant_obj.save()
            trans = get_or_create_model_transaction(self.request,
                subscription_result.subscription.transactions[0])
            try:
                membership_instance = Membership.objects.get_or_create(
                    user=self.request.user)[0]
                membership_dates_update.send(membership_instance, new_start_date=trans.timestamp)
                messages.success(self.request,
                	"""Your have successfuly registered as member.
                    Welcome""")
                return redirect("billing:list")
            except:
                messages.error(self.request, """An error occurred with your membership.
                    Please Contact us.""")
                return redirect("contact")
        else:
            messages.error(self.request, "An error occurred: {0}".format(
                subscription_result.message))
            return redirect("billing:upgrade")


class BillingHistoryTransactionListView(LoginRequiredMixin, ListView):
    model = Transaction

    def get_queryset(self, *args, **kwargs):
        update_transactions(self.request)
        qs = Transaction.objects.filter(user=self.request.user)
        return qs
