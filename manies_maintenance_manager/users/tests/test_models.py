"""Unit tests for the User model in Manie's Maintenance Manager."""

# pylint: disable=unused-argument

import uuid

import pytest
from django.core.exceptions import ValidationError

from manies_maintenance_manager.jobs.utils import get_test_user_password
from manies_maintenance_manager.users.models import User


def test_user_get_absolute_url(user: User) -> None:
    """Verify the correct URL is returned by the User model's get_absolute_url.

    Args:
        user (User): A user instance to test URL generation.

    Asserts that the get_absolute_url method returns the expected URL,
    formatted as "/users/{username}/".
    """
    assert user.get_absolute_url() == f"/users/{user.username}/"


def _make_user(
    django_user_model: type[User],
    username: str,
    *,
    is_agent: bool = False,
    is_superuser: bool = False,
    is_manie: bool = False,
) -> User:
    """Create and return a new user with optional agent and superuser status.

    This function helps in creating a user instance with additional properties
    like being an agent or a superuser. It sets the username and password,
    marks the email as verified, and assigns the role based on the parameters.

    Args:
        django_user_model (type[User]): The User model used to create new users.
        username (str): The username for the new user.
        is_agent (bool): Flag to indicate if the user is an agent.
        is_superuser (bool): Flag to indicate if the user is a superuser.
        is_manie (bool): Flag to indicate if the user is Manie.

    Returns:
        User: The newly created user instance.
    """
    user_ = django_user_model.objects.create_user(
        username=username,
        password=get_test_user_password(),
        is_agent=is_agent,
        is_superuser=is_superuser,
        is_manie=is_manie,
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


def _create_manie_user(django_user_model: type[User]) -> User:
    return _make_user(
        django_user_model,
        username="manie",
        is_manie=True,
    )


def test_is_agent_invalid_when_no_manie_user_present(
    django_user_model: type[User],
) -> None:
    """Ensure an Agent user cannot exist without a Manie user.

    Args:
        django_user_model (type[User]): The User model used to create users.

    Verifies that creating an Agent user without a Manie user in existence
    raises a ValidationError, enforcing the business rule.
    """
    # Create a new agent user, and confirm an error because there is no Manie user
    bob = _create_bob_agent_user(django_user_model)
    with pytest.raises(ValidationError) as err:
        bob.full_clean()
    assert err.value.message_dict["__all__"] == [
        "An Agent user can only exist if Manie exists.",
    ], "The error message should indicate that there is no Manie user."


def test_is_agent_valid_when_manie_user_is_present(
    django_user_model: type[User],
    manie_user: User,
) -> None:
    """Confirm that an Agent user can exist with a Manie user present.

    Args:
        django_user_model (type[User]): Model for creating user instances.
        manie_user (User): A Manie user instance from a fixture.

    Tests successful Agent user creation and validation when a Manie user
    exists, using the relevant user fixtures.
    """
    # We have a Manie user from our fixture, so creating an Agent user should work.
    _create_bob_agent_user(django_user_model)


@pytest.mark.django_db()
def test_user_model_has_uuid_id(user: User) -> None:
    """Verify that the User model's primary key is a UUID.

    Args:
        user (User): A user instance generated through the 'user' fixture,
                     which uses the UserFactory to create a User model instance.

    Confirms that the ID of a User model instance is of type UUID.
    """
    assert isinstance(
        user.id,
        uuid.UUID,
    ), "The User model's primary key should be a UUID."
