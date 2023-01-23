from itertools import chain

from django.shortcuts import render
from django.contrib.auth.views import LoginView as LoginBaseView
from django.views.generic import CreateView, DeleteView, FormView, TemplateView, UpdateView, View
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import CharField, Value

from bookreview import forms
from bookreview.models import Review, Ticket, UserFollows


class LoginView(LoginBaseView):
    form_class = forms.LoginForm
    template_name = "bookreview/login.html"
    redirect_authenticated_user = True


class FluxView(LoginRequiredMixin, TemplateView):
    template_name = "bookreview/flux.html"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        tickets = Ticket.objects.all()
        tickets = tickets.annotate(content_type=Value("TICKET", CharField()))
        reviews = Review.objects.all()
        reviews = reviews.annotate(content_type=Value("REVIEW", CharField()))
        posts = sorted(
            chain(reviews, tickets),
            key=lambda post: post.time_created,
            reverse=True
        )
        kwargs["posts"] = posts

        return kwargs


class PostsView(LoginRequiredMixin, TemplateView):
    template_name = "bookreview/posts.html"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        tickets = Ticket.objects.filter(user=self.request.user)
        tickets = tickets.annotate(content_type=Value("TICKET", CharField()))
        reviews = Review.objects.filter(user=self.request.user)
        reviews = reviews.annotate(content_type=Value("REVIEW", CharField()))
        posts = sorted(
            chain(reviews, tickets),
            key=lambda post: post.time_created,
            reverse=True
        )
        kwargs["posts"] = posts

        return kwargs


class SignupView(CreateView):
    form_class = forms.SignupForm
    template_name = "bookreview/signup.html"

    def get_success_url(self):
        return reverse("flux")


class FollowView(LoginRequiredMixin, FormView):
    model = UserFollows
    form_class = forms.UserFollowsForm
    template_name = "bookreview/follow.html"

    def form_valid(self, form):
        userfollow = UserFollows.objects.create(
            user=self.request.user,
            followed_user=form.cleaned_data["followed_user"]
        )
        userfollow.save()
        
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["followers"] = user.followed_by.all()
        context["followings"] = user.following.all()
        return context

    def get_success_url(self):
        return reverse("follow")


class UnFollowView(LoginRequiredMixin, DeleteView):
    # todo :
    # Ne pas pouvoir supprimer les abonnements qui ne sont pas à nous
    model = UserFollows
    template_name = "bookreview/unfollow.html"

    def get_success_url(self):
        return reverse("follow")

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class TicketCreateView(LoginRequiredMixin, CreateView):
    model = Ticket
    form_class = forms.TicketCreateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get_success_url(self):
        return reverse("flux")


class TicketUpdateView(LoginRequiredMixin, UpdateView):
    model = Ticket
    form_class = forms.TicketUpdateForm

    def get_success_url(self):
        return reverse("posts")


class ReviewExistingTicketCreate(LoginRequiredMixin, CreateView):
    model = Review
    template_name = "bookreview/review_existing_ticket.html"
    form_class = forms.ReviewCreateForm

    def get_success_url(self):
        return reverse("flux")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        ticket_pk = self.request.resolver_match.kwargs["pk"]
        kwargs["ticket_id"] = Ticket.objects.get(pk=ticket_pk)
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ticket_pk = self.request.resolver_match.kwargs["pk"]
        context["post"] = Ticket.objects.get(pk=ticket_pk)
        return context


class ReviewUpdate(LoginRequiredMixin, UpdateView):
    model = Review
    template_name = "bookreview/review_update.html"
    form_class = forms.ReviewUpdateForm

    def get_success_url(self):
        return reverse("posts")


class TicketAndReviewCreate(LoginRequiredMixin, CreateView):
    model = Ticket
    form_class = forms.TicketAndReviewCreateForm
    template_name = "bookreview/ticket_and_review_create.html"

    def get_success_url(self):
        return reverse("flux")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs
