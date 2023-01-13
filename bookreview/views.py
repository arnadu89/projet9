from django.shortcuts import render
from django.contrib.auth.views import LoginView as LoginBaseView
from django.views.generic import CreateView, ListView, TemplateView
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin

from bookreview import forms
from bookreview.models import UserFollows


class LoginView(LoginBaseView):
    form_class = forms.LoginForm
    template_name = "bookreview/login.html"
    redirect_authenticated_user = True


class FluxView(LoginRequiredMixin, TemplateView):
    template_name = "bookreview/flux.html"


class SignupView(CreateView):
    form_class = forms.SignupForm
    template_name = "bookreview/signup.html"

    def get_success_url(self):
        return reverse("flux")


class FollowView(LoginRequiredMixin, CreateView):
    model = UserFollows
    form_class = forms.UserFollowsForm
    template_name = "bookreview/follow.html"
    success_url = "follow"

    # def get_initial(self):
    #     self.initial.update({"request": self.request})
    #     return super().get_initial()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["followers"] = user.followed_by.all()
        context["followings"] = user.following.all()
        return context
