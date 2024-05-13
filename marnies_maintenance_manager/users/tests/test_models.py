"""Unit tests for the User model in Marnie's Maintenance Manager."""

import uuid

import pytest
from django.core.exceptions import ValidationError

from marnies_maintenance_manager.users.models import User


def test_user_get_absolute_url(user: User) -> None:
    """Verify that the User model's get_absolute_url method returns the correct URL."""
    assert user.get_absolute_url() == f"/users/{user.username}/"


def _make_user(
    django_user_model: type[User],
    username: str,
    *,
    is_agent: bool = False,
    is_superuser: bool = False,
    is_marnie: bool = False,
) -> User:
    """
    Create and return a new user with optional agent and superuser status.

    This function helps in creating a user instance with additional properties
    like being an agent or a superuser. It sets the username and password,
    marks the email as verified, and assigns the role based on the parameters.

    Args:
        django_user_model (type[User]): The User model used to create new users.
        username (str): The username for the new user.
        is_agent (bool): Flag to indicate if the user is an agent.
        is_superuser (bool): Flag to indicate if the user is a superuser.
        is_marnie (bool): Flag to indicate if the user is Marnie.

    Returns:
        User: The newly created user instance.
    """
    user_ = django_user_model.objects.create_user(
        username=username,
        password="password",  # noqa: S106
        is_agent=is_agent,
        is_superuser=is_superuser,
        is_marnie=is_marnie,
    )
    user_.emailaddress_set.create(  # type: ignore[attr-defined]
        email=f"{username}@example.com",
        primary=True,
        verified=True,
    )
    return user_


def _create_bob_agent_user(django_user_model: type[User]) -> User:
    return _make_user(
        django_user_model,
        username="bob",
        is_agent=True,
    )


def _create_marnie_user(django_user_model: type[User]) -> User:
    return _make_user(
        django_user_model,
        username="marnie",
        is_marnie=True,
    )


def test_is_agent_invalid_when_no_marnie_user_present(
    django_user_model: type[User],
) -> None:
    """Verify that an Agent user cannot exist without a Marnie user."""
    # Create a new agent user, and confirm an error because there is no Marnie user
    bob = _create_bob_agent_user(django_user_model)
    with pytest.raises(ValidationError) as err:
        bob.full_clean()
    assert err.value.message_dict["__all__"] == [
        "An Agent user can only exist if Marnie exists.",
    ], "The error message should indicate that there is no Marnie user."


def test_is_agent_valid_when_marnie_user_is_present(
    django_user_model: type[User],
    marnie_user: User,
) -> None:
    """Verify that an Agent user can exist when a Marnie user is present."""
    # We have a Marnie user from our fixture, so creating an Agent user should work.
    bob = _create_bob_agent_user(django_user_model)
    bob.full_clean()


@pytest.mark.django_db()
def test_user_model_has_uuid_id(user: User) -> None:
    """Verify that the User model has a UUID as the primary key."""
    assert isinstance(
        user.id,
        uuid.UUID,
    ), "The User model's primary key should be a UUID."
