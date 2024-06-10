"""Tests for the visibility of the update link in the job detail view.

This module contains tests to ensure that the update link is visible to the correct
users in the job detail view.
"""

from bs4 import BeautifulSoup
from django.test import Client
from django.urls import reverse
from rest_framework import status

from marnies_maintenance_manager.jobs.models import Job


def _get_update_link_or_none(job: Job, user_client: Client) -> BeautifulSoup | None:
    """Get the link to the job update view, or None if it couldn't be found.

    Args:
        job (Job): The job to get the update link for.
        user_client (Client): The Django test client for the user.

    Returns:
        BeautifulSoup | None: The link to the job update view, or None if it couldn't
    """
    response = user_client.get(
        reverse("jobs:job_detail", kwargs={"pk": job.pk}),
    )
    assert response.status_code == status.HTTP_200_OK
    page = response.content.decode("utf-8")

    # Use Python BeautifulSoup to parse the HTML and find the link
    # to the job update view.
    soup = BeautifulSoup(page, "html.parser")

    # Get the link with the text "Update", using BeautifulSoup (or None, if it
    # couldn't be found), and return that.
    return soup.find("a", string="Update")


class TestUpdateLinkVisibility:
    """Tests to ensure that the update link is visible to the correct users."""

    @staticmethod
    def test_page_has_update_link_going_to_update_view(
        job_created_by_bob: Job,
        marnie_user_client: Client,
    ) -> None:
        """Ensure that the job detail page has a link to the update view.

        Args:
            job_created_by_bob (Job): The job created by Bob.
            marnie_user_client (Client): The Django test client for Marnie.
        """
        link = _get_update_link_or_none(job_created_by_bob, marnie_user_client)
        assert link is not None

        # Confirm that the link goes to the correct URL.
        expected_url = reverse("jobs:job_update", kwargs={"pk": job_created_by_bob.pk})
        assert link["href"] == expected_url

    @staticmethod
    def test_update_link_is_visible_for_admin(
        job_created_by_bob: Job,
        admin_client: Client,
    ) -> None:
        """Ensure that the job detail page shows the update link to the admin user.

        Args:
            job_created_by_bob (Job): The job created by Bob.
            admin_client (Client): The Django test client for the admin user.
        """
        link = _get_update_link_or_none(job_created_by_bob, admin_client)
        assert link is not None

    @staticmethod
    def test_update_link_is_not_visible_for_agent(
        job_created_by_bob: Job,
        bob_agent_user_client: Client,
    ) -> None:
        """Ensure that the job detail page does not show the update link to agents.

        Args:
            job_created_by_bob (Job): The job created by Bob.
            bob_agent_user_client (Client): The Django test client for Bob.
        """
        response = bob_agent_user_client.get(
            reverse("jobs:job_detail", kwargs={"pk": job_created_by_bob.pk}),
        )
        assert response.status_code == status.HTTP_200_OK
        page = response.content.decode("utf-8")

        # Use Python BeautifulSoup to parse the HTML and find the link
        # to the job update view.
        soup = BeautifulSoup(page, "html.parser")

        # Check with BeautifulSoup that the link is not present.
        link = soup.find("a", string="Update")
        assert link is None

    @staticmethod
    def test_update_link_is_not_visible_to_marnie_after_he_has_done_initial_inspection(
        bob_job_with_initial_marnie_inspection: Job,
        marnie_user_client: Client,
    ) -> None:
        """Ensure Marnie can't see the update link after completing initial inspection.

        Args:
            bob_job_with_initial_marnie_inspection (Job): The job created by Bob with
                the initial inspection done by Marnie.
            marnie_user_client (Client): The Django test client for Marnie.
        """
        response = marnie_user_client.get(
            reverse(
                "jobs:job_detail",
                kwargs={"pk": bob_job_with_initial_marnie_inspection.pk},
            ),
        )
        assert response.status_code == status.HTTP_200_OK
        page = response.content.decode("utf-8")

        # Use Python BeautifulSoup to parse the HTML and find the link with the text
        # "Update"
        soup = BeautifulSoup(page, "html.parser")
        link = soup.find("a", string="Update")

        # Confirm that we couldn't find it:
        assert (
            link is None
        ), "The link to update the job should not be visible to Marnie."
