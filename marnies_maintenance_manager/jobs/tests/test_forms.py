"""Tests for the forms in the "jobs" app."""

# pylint: disable=magic-value-comparison

from django.core.files.uploadedfile import SimpleUploadedFile

from marnies_maintenance_manager.jobs.forms import JobUpdateForm
from marnies_maintenance_manager.jobs.forms import QuoteUpdateForm
from marnies_maintenance_manager.jobs.models import Job
from marnies_maintenance_manager.users.models import User


class TestJobUpdateForm:
    """Tests for the JobUpdateForm form."""

    @staticmethod
    def test_model_class_is_job() -> None:
        """Test that the JobUpdateForm is for the Job model."""
        assert JobUpdateForm.Meta.model == Job

    @staticmethod
    def test_has_date_of_inspection_field() -> None:
        """Test that the JobUpdateForm has a date_of_inspection field."""
        assert "date_of_inspection" in JobUpdateForm.Meta.fields

    @staticmethod
    def test_has_quote_field() -> None:
        """Test that the JobUpdateForm has a quote field."""
        assert "quote" in JobUpdateForm.Meta.fields

    @staticmethod
    def test_date_of_inspection_field_is_required_date_input() -> None:
        """Test that the date_of_inspection field is required."""
        data = {"date_of_inspection": ""}
        form = JobUpdateForm(data=data)
        assert not form.is_valid()
        assert "date_of_inspection" in form.errors
        assert "This field is required." in form.errors["date_of_inspection"]

    @staticmethod
    def test_quote_field_is_required_file_field() -> None:
        """Test that the quote field is required."""
        data = {"quote": ""}
        form = JobUpdateForm(data=data)
        assert not form.is_valid()
        assert "quote" in form.errors
        assert "This field is required." in form.errors["quote"]


class TestQuoteUpdateForm:
    """Tests for the QuoteUpdateForm form."""

    @staticmethod
    def test_model_class_is_job() -> None:
        """Test that the QuoteUpdateForm is for the Job model."""
        assert QuoteUpdateForm.Meta.model == Job

    @staticmethod
    def test_has_quote_field() -> None:
        """Test that the QuoteUpdateForm has a quote field."""
        assert "quote" in QuoteUpdateForm.Meta.fields

    @staticmethod
    def test_should_have_an_error_if_same_quote_is_submitted(
        bob_agent_user: User,
        test_pdf: SimpleUploadedFile,
    ) -> None:
        """Test that the form has an error if the same quote is submitted.

        Args:
            bob_agent_user (User): A user instance for Bob the agent.
            test_pdf (SimpleUploadedFile): A test PDF file.
        """
        job = Job.objects.create(
            agent=bob_agent_user,
            date="2022-01-01",
            quote=test_pdf,
        )
        data = {"quote": test_pdf}
        form = QuoteUpdateForm(data=data, instance=job)
        assert not form.is_valid()
        assert "quote" in form.errors
        assert "You must provide a new quote" in form.errors["quote"]