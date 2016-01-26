from django.shortcuts import render
from django.views.generic.base import TemplateView


class AccountTemplateView(TemplateView):
    template_name = "users/account_profile.html"
