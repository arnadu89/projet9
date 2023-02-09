from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.forms import CharField

from bookreview.models import Review, Ticket, User, UserFollows


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Nom d'utilisateur")
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")


class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('username',)


class UserFollowsForm(forms.Form):
    followed_user = CharField()

    def __init__(self, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(**kwargs)

    def clean_followed_user(self):
        follower_username = self.cleaned_data["followed_user"]
        if not (followed_user := User.objects.filter(username=follower_username)):
            raise ValidationError(
                f"L'utilisateur avec le nom {follower_username} n'existe pas.",
                code="user_does_not_exist"
            )
        else:
            self.cleaned_data["followed_user"] = followed_user[0]

        if self.user == self.cleaned_data["followed_user"]:
            raise ValidationError(
                f"Vous ne pouvez pas vous suivre vous même !",
                code="self_subscription"
            )

        if UserFollows.objects.filter(user=self.user, followed_user__username=follower_username):
            raise ValidationError(
                f"Vous suivez déjà l'utilisateur {follower_username}.",
                code="already_subscribed"
            )
        return self.cleaned_data["followed_user"]


class TicketCreateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'image']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        # Add the current authenticated user as follower
        self.instance.user = self.request.user
        return super().save()


class TicketUpdateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'image']


class ReviewCreateForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['headline', 'body', 'rating']

    rating = forms.IntegerField(
        widget=forms.RadioSelect(
            choices=((i, i) for i in range(1, 6))
        )
    )

    def __init__(self, **kwargs):
        self.ticket_id = kwargs.pop("ticket_id")
        self.user = kwargs.pop("user")
        super().__init__(**kwargs)
        self.instance.ticket = self.ticket_id
        self.instance.user = self.user


class ReviewUpdateForm(ReviewCreateForm):
    def __init__(self, **kwargs):
        forms.ModelForm.__init__(self, **kwargs)


class TicketAndReviewCreateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'image']

    review_headline = forms.CharField(max_length=128)
    review_rating = forms.IntegerField(
        widget=forms.RadioSelect(
            choices=((i, i) for i in range(1, 6))
        )
    )
    review_body = forms.CharField(max_length=8192)

    def __init__(self, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(**kwargs)

    def save(self, commit=True):
        # saving ticket instance
        self.instance.user = self.user
        ticket_instance = super().save(commit)

        # Creating review
        review_data = {
            'headline': self.cleaned_data["review_headline"],
            'body': self.cleaned_data["review_body"],
            'rating': self.cleaned_data["review_rating"],
        }

        review_validation_form = ReviewCreateForm(
            data=review_data,
            ticket_id=ticket_instance,
            user=self.user,
        )
        if review_validation_form.is_valid():
            review_validation_form.save(commit)
        else:
            # Gérer le fail da la validation du formulaire de review
            pass

        return ticket_instance

