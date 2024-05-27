"""Tests for the job update view."""

# pylint: disable=redefined-outer-name,unused-argument

import datetime

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from rest_framework import status

from marnies_maintenance_manager.jobs.models import Job
from marnies_maintenance_manager.jobs.views import JobUpdateView

from .conftest import BASIC_TEST_PDF_FILE
from .utils import check_basic_page_html_structure


def post_update_request_and_check_errors(
    client: Client,
    url: str,
    data: dict[str, str | SimpleUploadedFile],
    field_name: str,
    expected_error: str,
) -> None:
    """Post an update request and check for errors.

    Args:
        client (Client): The Django test client.
        url (str): The URL to post the request to.
        data (dict): The data to post.
        field_name (str): The field name to check for errors.
        expected_error (str): The expected error message.
    """
    response = client.post(url, data, follow=True)
    # Assert the response status code is 200
    assert response.status_code == status.HTTP_200_OK

    # Check the redirect chain that leads things up to here:
    assert response.redirect_chain == []

    # Check that the expected error is present.
    form_errors = response.context["form"].errors
    assert field_name in form_errors
    assert form_errors[field_name] == [expected_error]


def test_anonymous_user_cannot_access_the_view(
    client: Client,
    bob_job_update_url: str,
) -> None:
    """Test that the anonymous user cannot access the job update view.

    Args:
        client (Client): The Django test client.
        bob_job_update_url (str): The URL for Bobs job update view.
    """
    # Note: Django-FastDev causes a DeprecationWarning to be logged when using the
    # {% if %} template tag. This is somewhere deep within the Django-Allauth package,
    # while handling a GET request to the /accounts/login/ URL. We can ignore this
    # for our testing.
    with pytest.warns(
        DeprecationWarning,
        match="set FASTDEV_STRICT_IF in settings, and use {% ifexists %} instead of "
        "{% if %}",
    ):
        response = client.get(bob_job_update_url, follow=True)

    # This should be a redirect to a login page:
    assert response.status_code == status.HTTP_200_OK

    expected_redirect_chain = [
        (
            f"/accounts/login/?next=/jobs/{bob_job_update_url.split('/')[-3]}/update/",
            status.HTTP_302_FOUND,
        ),
    ]
    assert response.redirect_chain == expected_redirect_chain


def test_agent_user_cannot_access_the_view(
    bob_agent_user_client: Client,
    bob_job_update_url: str,
) -> None:
    """Test that the agent user cannot access the job update view.

    Args:
        bob_agent_user_client (Client): The Django test client for Bob.
        bob_job_update_url (str): The URL for Bobs job update view.
    """
    response = bob_agent_user_client.get(bob_job_update_url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_admin_user_can_access_the_view(
    superuser_client: Client,
    bob_job_update_url: str,
) -> None:
    """Test that the admin user can access the job update view.

    Args:
        superuser_client (Client): The Django test client for the superuser.
        bob_job_update_url (str): The URL for Bobs job update view.
    """
    response = superuser_client.get(bob_job_update_url)
    assert response.status_code == status.HTTP_200_OK


def test_marnie_user_can_access_the_view(
    marnie_user_client: Client,
    bob_job_update_url: str,
) -> None:
    """Test that the Marnie user can access the job update view.

    Args:
        marnie_user_client (Client): The Django test client for Marnie.
        bob_job_update_url (str): The URL for Bobs job update view.
    """
    response = marnie_user_client.get(bob_job_update_url)
    assert response.status_code == status.HTTP_200_OK


def test_page_has_basic_correct_structure(
    marnie_user_client: Client,
    bob_job_update_url: str,
) -> None:
    """Test that the job update page has the correct basic structure.

    Args:
        marnie_user_client (Client): The Django test client for Marnie.
        bob_job_update_url (str): The URL for Bobs job update view.
    """
    check_basic_page_html_structure(
        client=marnie_user_client,
        url=bob_job_update_url,
        expected_title="Update Maintenance Job",
        expected_template_name="jobs/job_update.html",
        expected_h1_text="Update Maintenance Job",
        expected_func_name="view",
        expected_url_name="job_update",
        expected_view_class=JobUpdateView,
    )


def test_view_has_date_of_inspection_field(
    job_created_by_bob: Job,
    marnie_user_client: Client,
    bob_job_update_url: str,
    test_pdf: SimpleUploadedFile,
) -> None:
    """Test that the job update page has the 'date_of_inspection' field.

    Args:
        job_created_by_bob (Job): The job created by Bob.
        marnie_user_client (Client): The Django test client for Marnie.
        bob_job_update_url (str): The URL for Bobs job update view.
        test_pdf (SimpleUploadedFile): The test PDF file.
    """
    response = marnie_user_client.post(
        bob_job_update_url,
        {
            "date_of_inspection": "2001-02-05",
            "quote": test_pdf,
        },
        follow=True,
    )
    # Assert the response status code is 200
    assert response.status_code == status.HTTP_200_OK

    # Check the redirect chain that leads things up to here:
    assert response.redirect_chain == [
        (f"/jobs/{job_created_by_bob.pk}/", status.HTTP_302_FOUND),
    ]

    # Refresh the Maintenance Job from the database, and then check the updated
    # record:
    job_created_by_bob.refresh_from_db()
    assert job_created_by_bob.date_of_inspection == datetime.date(2001, 2, 5)


def test_view_has_quote_field(
    job_created_by_bob: Job,
    marnie_user_client: Client,
    bob_job_update_url: str,
    test_pdf: SimpleUploadedFile,
) -> None:
    """Test that the job update page has the 'quote' field.

    Args:
        job_created_by_bob (Job): The job created by Bob.
        marnie_user_client (Client): The Django test client for Marnie.
        bob_job_update_url (str): The URL for Bobs job update view.
        test_pdf (SimpleUploadedFile): The test PDF file.
    """
    # POST request to upload new PDF
    response = marnie_user_client.post(
        bob_job_update_url,
        {
            "date_of_inspection": "2001-02-05",
            "quote": test_pdf,
        },
        follow=True,
    )

    # Assert the response status code is 200
    assert response.status_code == status.HTTP_200_OK

    # Check the redirect chain that leads things up to here:
    assert response.redirect_chain == [
        (f"/jobs/{job_created_by_bob.pk}/", status.HTTP_302_FOUND),
    ]

    # Refresh the Maintenance Job from the database
    job_created_by_bob.refresh_from_db()

    # And confirm that the PDF file has been updated
    assert job_created_by_bob.quote.name.endswith("test.pdf")


def test_date_of_inspection_field_is_required(
    job_created_by_bob: Job,
    marnie_user_client: Client,
    bob_job_update_url: str,
) -> None:
    """Test that the 'date_of_inspection' field is required.

    Args:
        job_created_by_bob (Job): The job created by Bob.
        marnie_user_client (Client): The Django test client for Marnie.
        bob_job_update_url (str): The URL for Bobs job update view.
    """
    post_update_request_and_check_errors(
        client=marnie_user_client,
        url=bob_job_update_url,
        data={},
        field_name="date_of_inspection",
        expected_error="This field is required.",
    )


def test_quote_field_is_required(
    job_created_by_bob: Job,
    marnie_user_client: Client,
    bob_job_update_url: str,
) -> None:
    """Test that the 'quote' field is required.

    Args:
        job_created_by_bob (Job): The job created by Bob.
        marnie_user_client (Client): The Django test client for Marnie.
        bob_job_update_url (str): The URL for Bobs job update view.
    """
    post_update_request_and_check_errors(
        client=marnie_user_client,
        url=bob_job_update_url,
        data={},
        field_name="quote",
        expected_error="This field is required.",
    )


def test_updating_job_changes_status_to_inspection_completed(
    job_created_by_bob: Job,
    marnie_user_client: Client,
    bob_job_update_url: str,
    test_pdf: SimpleUploadedFile,
) -> None:
    """Test that updating the job changes the status to 'Inspection Completed'.

    Args:
        job_created_by_bob (Job): The job created by Bob.
        marnie_user_client (Client): The Django test client for Marnie.
        bob_job_update_url (str): The URL for Bobs job update view.
        test_pdf (SimpleUploadedFile): The test PDF file.
    """
    # POST request to upload new details:
    response = marnie_user_client.post(
        bob_job_update_url,
        {
            "date_of_inspection": "2001-02-05",
            "quote": test_pdf,
        },
        follow=True,
    )

    # Assert the response status code is 200
    assert response.status_code == status.HTTP_200_OK

    # Check the redirect chain that leads things up to here:
    assert response.redirect_chain == [
        (f"/jobs/{job_created_by_bob.pk}/", status.HTTP_302_FOUND),
    ]

    # Refresh the Maintenance Job from the database
    job_created_by_bob.refresh_from_db()

    # Check that the status changed as expected
    assert job_created_by_bob.status == Job.Status.INSPECTION_COMPLETED.value


def test_should_not_allow_txt_extension_file_for_quote(
    job_created_by_bob: Job,
    marnie_user_client: Client,
    bob_job_update_url: str,
) -> None:
    """Test that the view should not allow a .txt file extension for the 'quote' field.

    Args:
        job_created_by_bob (Job): The job created by Bob.
        marnie_user_client (Client): The Django test client for Marnie.
        bob_job_update_url (str): The URL for Bobs job update view.
    """
    # New TXT file to upload
    test_txt = SimpleUploadedFile(
        "test.txt",
        BASIC_TEST_PDF_FILE.read_bytes(),
        content_type="application/pdf",
    )

    post_update_request_and_check_errors(
        client=marnie_user_client,
        url=bob_job_update_url,
        data={
            "date_of_inspection": "2001-02-05",
            "quote": test_txt,
        },
        field_name="quote",
        expected_error="File extension “txt” is not allowed. "
        "Allowed extensions are: pdf.",
    )


def test_validates_pdf_contents(
    job_created_by_bob: Job,
    marnie_user_client: Client,
    bob_job_update_url: str,
) -> None:
    """Test that the view should validate the contents of the PDF file.

    Args:
        job_created_by_bob (Job): The job created by Bob.
        marnie_user_client (Client): The Django test client for Marnie.
        bob_job_update_url (str): The URL for Bobs job update view.
    """
    # New PDF file to upload
    new_pdf = SimpleUploadedFile(
        "new.pdf",
        b"invalid_file_content",
        content_type="application/pdf",
    )

    post_update_request_and_check_errors(
        client=marnie_user_client,
        url=bob_job_update_url,
        data={
            "date_of_inspection": "2001-02-05",
            "quote": new_pdf,
        },
        field_name="quote",
        expected_error="This is not a valid PDF file.",
    )


def test_marnie_cannot_access_view_after_initial_site_inspection(
    bob_job_with_initial_marnie_inspection: Job,
    marnie_user_client: Client,
    bob_job_update_url: str,
) -> None:
    """Ensure Marnie can't access the update view after completing initial inspection.

    Args:
        bob_job_with_initial_marnie_inspection (Job): The job created by Bob with the
            initial inspection done by Marnie.
        marnie_user_client (Client): The Django test client for Marnie.
        bob_job_update_url (str): The URL for the job update view for the job created
            by Bob.
    """
    response = marnie_user_client.get(bob_job_update_url)
    assert response.status_code == status.HTTP_403_FORBIDDEN
