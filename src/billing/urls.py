from django.conf.urls import url

from .views import (BillingUpgradeView,
                    BillingHistoryTransactionListView,
                    CancelSubscriptionView)

urlpatterns = [
    url(r'^$', BillingUpgradeView.as_view(), name='upgrade'),
    url(r'^history/$', view=BillingHistoryTransactionListView.as_view(), name="list"),
    url(r'^cancel/$', view=CancelSubscriptionView.as_view(), name="cancel"),
]
