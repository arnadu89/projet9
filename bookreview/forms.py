from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from bookreview.models import UserFollows


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Nom d'utilisateur")
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")


class SignupForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('username',)


class UserFollowsForm(forms.ModelForm):
    class Meta:
        model = UserFollows
        fields = ['followed_user']
        labels = {
            'followed_user': '',
        }
        widgets = {
            'followed_user': forms.widgets.TextInput()
        }
