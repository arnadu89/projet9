from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q


class User(AbstractUser):
    def get_tickets_from_subscriptions(self):
        tickets = Ticket.objects.filter(
            # Q(user__followed_by__user=self) | Q(user=self)
            Q(user__in=[f.followed_user for f in self.following.all()]) | Q(user=self)
        )
        # Ticket.objects.filter(Q(user__in=[f.followed_user for f in self.following.all()]) | Q(user=self))
        # import ipdb
        # ipdb.set_trace()
        return tickets

    def get_reviews_from_subscriptions(self):
        # get reviews from :
        # users followed
        # your reviews
        # reviews that concern ticket you have posted
        reviews = Review.objects.filter(
            # Q(user__followed_by__user=self) | Q(user=self) | Q(ticket__user=self)
            Q(user__in=[f.followed_user for f in self.following.all()]) | Q(user=self) | Q(ticket__user=self)
        )
        return reviews


class UserFollows(models.Model):
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name="following")
    followed_user = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                                      on_delete=models.CASCADE,
                                      related_name="followed_by")

    class Meta:
        unique_together = ('user', 'followed_user')

    def __str__(self):
        return f"Abonnement : {self.followed_user} est suivi par {self.user}"


class Ticket(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2048, blank=True)
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    image = models.ImageField(blank=True)
    time_created = models.DateTimeField(auto_now_add=True)

    @property
    def review(self):
        return self.review_set.last()

    @property
    def reviews(self):
        return self.review_set.all()

    def has_user_already_reviewed(self, user):
        return [review for review in self.review_set.all() if user == review.user]

    def __str__(self):
        return f"Ticket for {self.title} ask by {self.user}"


class Review(models.Model):
    ticket = models.ForeignKey(to=Ticket, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=[
                                                  MinValueValidator(0),
                                                  MaxValueValidator(5),
                                              ])
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    headline = models.CharField(max_length=128)
    body = models.TextField(max_length=8192, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.ticket.title} - rated {self.rating} / 5"
