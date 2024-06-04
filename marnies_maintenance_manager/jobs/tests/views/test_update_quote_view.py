"""Tests for the QuoteUpdateView view."""

from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponseRedirect
from django.test import Client
from django.urls import reverse
from rest_framework import status

from marnies_maintenance_manager.jobs.models import Job
from marnies_maintenance_manager.jobs.views.update_quote_view import QuoteUpdateView

from .utils import check_basic_page_html_structure


def test_view_has_correct_basic_structure(
    job_rejected_by_bob: Job,
    marnie_user_client: Client,
) -> None:
    """Ensure that the quote update view has the correct basic structure.

    Args:
        job_rejected_by_bob (Job): A Job instance created by Bob, with a rejected quote.
        marnie_user_client (Client): The Django test client for Marnie.
    """
    check_basic_page_html_structure(
        client=marnie_user_client,
        url=reverse("jobs:update_quote", kwargs={"pk": job_rejected_by_bob.pk}),
        expected_title="Update Quote",
        expected_template_name="jobs/update_quote.html",
        expected_h1_text="Update Quote",
        expected_func_name="view",
        expected_url_name="update_quote",
        expected_view_class=QuoteUpdateView,
    )


def test_agent_cannot_use_the_view(
    job_rejected_by_bob: Job,
    bob_agent_user_client: Client,
) -> None:
    """Test that Bob cannot access the quote update view.

    Args:
        job_rejected_by_bob (Job): A Job instance created by Bob, with a rejected quote.
        bob_agent_user_client (Client): The Django test client for Bob.
    """
    response = bob_agent_user_client.get(
        reverse("jobs:update_quote", kwargs={"pk": job_rejected_by_bob.pk}),
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_must_be_logged_in_to_use_the_view(
    job_rejected_by_bob: Job,
    client: Client,
) -> None:
    """Test that a user must be logged in to access the quote update view.

    Args:
        job_rejected_by_bob (Job): A Job instance created by Bob, with a rejected quote.
        client (Client): The Django test client.
    """
    response = client.get(
        reverse("jobs:update_quote", kwargs={"pk": job_rejected_by_bob.pk}),
    )
    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert (
        response.url
        == f"/accounts/login/?next=/jobs/{job_rejected_by_bob.pk}/update-quote/"
    )


def test_view_updates_the_quote_field_on_the_job(
    job_rejected_by_bob: Job,
    marnie_user_client: Client,
    test_pdf: SimpleUploadedFile,
    test_pdf_2: SimpleUploadedFile,
) -> None:
    """Test that the view updates the quote field on the job.

    Args:
        job_rejected_by_bob (Job): A Job instance created by Bob, with a rejected quote.
        marnie_user_client (Client): The Django test client for Marnie.
        test_pdf (SimpleUploadedFile): A test PDF file.
        test_pdf_2 (SimpleUploadedFile): A test PDF file.
    """
    # Check before our test, that Job.quote (a FileField), has the same contents as the
    # original testing PDF file.
    test_pdf.seek(0)
    assert job_rejected_by_bob.quote.read() == test_pdf.read()

    response = marnie_user_client.post(
        reverse("jobs:update_quote", kwargs={"pk": job_rejected_by_bob.pk}),
        data={"quote": test_pdf_2},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url == reverse(
        "jobs:job_detail",
        kwargs={"pk": job_rejected_by_bob.pk},
    )
    job_rejected_by_bob.refresh_from_db()

    test_pdf_2.seek(0)
    assert job_rejected_by_bob.quote.read() == test_pdf_2.read()


def test_admin_can_use_the_view(
    job_rejected_by_bob: Job,
    superuser_client: Client,
) -> None:
    """Test that an admin user can access the quote update view.

    Args:
        job_rejected_by_bob (Job): A Job instance created by Bob, with a rejected quote.
        superuser_client (Client): The Django test client for the superuser.
    """
    response = superuser_client.get(
        reverse("jobs:update_quote", kwargs={"pk": job_rejected_by_bob.pk}),
    )
    assert response.status_code == status.HTTP_200_OK


def test_cannot_resubmit_the_same_quote(
    job_rejected_by_bob: Job,
    superuser_client: Client,
    test_pdf: SimpleUploadedFile,
) -> None:
    """Test that a user cannot resubmit the same quote.

    Args:
        job_rejected_by_bob (Job): A Job instance created by Bob, with a rejected quote.
        superuser_client (Client): The Django test client for the superuser.
        test_pdf (SimpleUploadedFile): A test PDF file.
    """
    # Confirm the PDF file before we attempt to re-upload it:
    test_pdf.seek(0)
    assert job_rejected_by_bob.quote.read() == test_pdf.read()

    # Attempt to re-upload the same PDF file:
    test_pdf.seek(0)
    response = superuser_client.post(
        reverse("jobs:update_quote", kwargs={"pk": job_rejected_by_bob.pk}),
        data={"quote": test_pdf},
    )

    # Confirm that the response is an HTTP 200 status code, and that the form has an
    # error:
    assert response.status_code == status.HTTP_200_OK
    assert response.context["form"].errors == {
        "quote": ["You must provide a new quote"],
    }


def test_on_success_redirects_to_the_detail_view(
    job_rejected_by_bob: Job,
    marnie_user_client: Client,
    test_pdf_2: SimpleUploadedFile,
) -> None:
    """Test that the view redirects to the job detail view on success.

    Args:
        job_rejected_by_bob (Job): A Job instance created by Bob, with a rejected quote.
        marnie_user_client (Client): The Django test client for Marnie.
        test_pdf_2 (SimpleUploadedFile): A test PDF file.
    """
    response = marnie_user_client.post(
        reverse("jobs:update_quote", kwargs={"pk": job_rejected_by_bob.pk}),
        data={"quote": test_pdf_2},
    )
    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url == reverse(
        "jobs:job_detail",
        kwargs={"pk": job_rejected_by_bob.pk},
    )