from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from bookreview.models import Ticket, User, UserFollows


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Nom d'utilisateur")
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")


class SignupForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('username',)


class UserFollowsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        # Add the current authenticated user as follower
        self.instance.user = self.request.user
        return super().save()

    class Meta:
        model = UserFollows
        fields = ['followed_user']
        labels = {
            'followed_user': '',
        }
        widgets = {
            'followed_user': forms.widgets.TextInput()
        }


class TicketCreateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        # Add the current authenticated user as follower
        self.instance.user = self.request.user
        return super().save()
