from django.shortcuts import render
from django.contrib.auth.views import LoginView as LoginBaseView
from django.views.generic import CreateView, ListView, TemplateView
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin

from . import forms


class LoginView(LoginBaseView):
    form_class = forms.LoginForm
    template_name = "bookreview/login.html"


class FluxView(LoginRequiredMixin, TemplateView):
    template_name = "bookreview/flux.html"


class SignupView(CreateView):
    form_class = forms.SignupForm
    template_name = "bookreview/signup.html"

    # def form_valid(self, form):
    #     form.cleaned_data
    #     return super().form_valid(form)

    def get_success_url(self):
        return reverse("flux")
