"""Define forms related to user management and authentication."""

from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django.contrib.auth import forms as admin_forms
from django.utils.translation import gettext_lazy as _

from .models import User


class UserAdminChangeForm(admin_forms.UserChangeForm):  # type: ignore[type-arg]
    """Provide form for changing existing users in the admin area."""

    class Meta(admin_forms.UserChangeForm.Meta):
        """Define metadata for the UserAdminChangeForm class."""

        model = User


class UserAdminCreationForm(admin_forms.UserCreationForm):  # type: ignore[type-arg]
    """
    Form for User Creation in the Admin Area.

    To change user signup, see UserSignupForm and UserSocialSignupForm.
    """

    class Meta(admin_forms.UserCreationForm.Meta):
        """Define metadata and handle unique constraint violations."""

        model = User
        error_messages = {
            "username": {"unique": _("This username has already been taken.")},
        }


class UserSignupForm(SignupForm):  # type: ignore[misc]
    """
    Form that will be rendered on a user sign up section/screen.

    Default fields will be added automatically.
    Check UserSocialSignupForm for accounts created from social.
    """


class UserSocialSignupForm(SocialSignupForm):  # type: ignore[misc]
    """
    Renders the form when user has signed up using social accounts.

    Default fields will be added automatically.
    See UserSignupForm otherwise.
    """
