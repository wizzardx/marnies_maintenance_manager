"""Fixtures for the view tests."""

import datetime
from pathlib import Path

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from marnies_maintenance_manager.jobs.models import Job
from marnies_maintenance_manager.users.models import User


@pytest.fixture()
def job_created_by_bob(bob_agent_user: User) -> Job:
    """Create a job instance for Bob the agent.

    Args:
        bob_agent_user (User): The User instance representing Bob the agent.

    Returns:
        Job: The job instance created for Bob.

    """
    return Job.objects.create(
        agent=bob_agent_user,
        date=datetime.date(2022, 1, 1),
        address_details="1234 Main St, Springfield, IL",
        gps_link="https://www.google.com/maps",
        quote_request_details="Replace the kitchen sink",
    )


@pytest.fixture()
def job_created_by_peter(peter_agent_user: User) -> Job:
    """Create a job instance for Peter the agent.

    Args:
        peter_agent_user (User): The User instance representing Peter the agent.

    Returns:
        Job: The job instance created for Peter.

    """
    return Job.objects.create(
        agent=peter_agent_user,
        date="2022-01-01",
        address_details="1234 Main St, Springfield, IL",
        gps_link="https://www.google.com/maps",
        quote_request_details="Replace the kitchen sink",
    )


BASIC_TEST_PDF_FILE = Path(__file__).parent / "test.pdf"


@pytest.fixture()
def bob_job_update_url(job_created_by_bob: Job) -> str:
    """Return the URL for the job update view for the job created by Bob.

    Args:
        job_created_by_bob (Job): The job created by Bob.

    Returns:
        str: The URL for Bobs job update view.
    """
    return reverse("jobs:job_update", kwargs={"pk": job_created_by_bob.pk})


@pytest.fixture()
def test_pdf() -> SimpleUploadedFile:
    """Return a test PDF file as a SimpleUploadedFile.

    Returns:
        SimpleUploadedFile: The test PDF file.
    """
    return SimpleUploadedFile(
        "test.pdf",
        BASIC_TEST_PDF_FILE.read_bytes(),
        content_type="application/pdf",
    )
