from itertools import chain

from django.contrib.auth.views import LoginView as LoginBaseView
from django.views.generic import CreateView, DeleteView, FormView, TemplateView, UpdateView
from django.urls import reverse_lazy
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
        context_data = super().get_context_data(**kwargs)

        # Get tickets
        tickets = self.request.user.get_tickets_from_subscriptions()
        tickets = tickets.annotate(content_type=Value("TICKET", CharField()))
        for ticket in tickets:
            if ticket.has_user_already_reviewed(self.request.user):
                ticket.user_already_reviewed = True

        # Get reviews
        reviews = self.request.user.get_reviews_from_subscriptions()
        reviews = reviews.annotate(content_type=Value("REVIEW", CharField()))

        # Sorting posts
        posts = set(chain(reviews, tickets))
        posts = sorted(
            posts,
            key=lambda post: post.time_created,
            reverse=True
        )
        context_data["posts"] = posts

        return context_data


class PostsView(LoginRequiredMixin, TemplateView):
    template_name = "bookreview/posts.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        tickets = Ticket.objects.filter(user=self.request.user)
        tickets = tickets.annotate(content_type=Value("TICKET", CharField()))
        reviews = Review.objects.filter(user=self.request.user)
        reviews = reviews.annotate(content_type=Value("REVIEW", CharField()))
        posts = sorted(
            chain(reviews, tickets),
            key=lambda post: post.time_created,
            reverse=True
        )
        context_data["posts"] = posts

        return context_data


class SignupView(CreateView):
    form_class = forms.SignupForm
    template_name = "bookreview/signup.html"
    success_url = reverse_lazy("flux")


class FollowView(LoginRequiredMixin, FormView):
    model = UserFollows
    form_class = forms.UserFollowsForm
    template_name = "bookreview/follow.html"
    success_url = reverse_lazy("follow")

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


class UnFollowView(LoginRequiredMixin, DeleteView):
    model = UserFollows
    template_name = "bookreview/unfollow.html"
    success_url = reverse_lazy("follow")

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class TicketCreateView(LoginRequiredMixin, CreateView):
    model = Ticket
    form_class = forms.TicketCreateForm
    success_url = reverse_lazy("flux")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


class TicketUpdateView(LoginRequiredMixin, UpdateView):
    model = Ticket
    form_class = forms.TicketUpdateForm
    success_url = reverse_lazy("posts")


class TicketDeleteView(LoginRequiredMixin, DeleteView):
    model = Ticket
    template_name = "bookreview/ticket_delete.html"
    success_url = reverse_lazy("posts")


class ReviewExistingTicketCreateView(LoginRequiredMixin, CreateView):
    model = Review
    template_name = "bookreview/review_existing_ticket.html"
    form_class = forms.ReviewCreateForm
    success_url = reverse_lazy("flux")

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


class ReviewUpdateView(LoginRequiredMixin, UpdateView):
    model = Review
    template_name = "bookreview/review_update.html"
    form_class = forms.ReviewUpdateForm
    success_url = reverse_lazy("posts")


class ReviewDeleteView(LoginRequiredMixin, DeleteView):
    model = Review
    template_name = "bookreview/review_delete.html"
    success_url = reverse_lazy("posts")


class TicketAndReviewCreateView(LoginRequiredMixin, CreateView):
    model = Ticket
    form_class = forms.TicketAndReviewCreateForm
    template_name = "bookreview/ticket_and_review_create.html"
    success_url = reverse_lazy("flux")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs
