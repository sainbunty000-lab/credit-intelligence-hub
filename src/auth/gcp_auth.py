import logging
import google.auth
from google.auth.transport.requests import Request
from google.auth.exceptions import DefaultCredentialsError

logger = logging.getLogger(__name__)

# Required scopes for Google Sheets + Drive
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


def get_gcp_credentials():
    """
    Returns Google Cloud credentials using Workload Identity Federation.

    Works in:
    - GitHub Actions (via OIDC)
    - Local dev (if gcloud auth application-default login is set)

    No service account JSON required.
    """

    try:
        # Get default credentials (WIF in CI, ADC locally)
        creds, project_id = google.auth.default(scopes=SCOPES)

        logger.info(f"🔐 GCP credentials loaded (project: {project_id})")

        # Some environments require explicit scoping
        if creds.requires_scopes:
            creds = creds.with_scopes(SCOPES)
            logger.info("🔧 Applied required scopes to credentials")

        # Ensure token is valid
        if not creds.valid:
            logger.info("🔄 Refreshing GCP credentials token")
            creds.refresh(Request())

        return creds

    except DefaultCredentialsError as e:
        logger.error("❌ No valid GCP credentials found.")
        logger.error(
            "👉 Ensure Workload Identity is configured in GitHub Actions "
            "or run `gcloud auth application-default login` locally."
        )
        raise

    except Exception as e:
        logger.error(f"❌ Unexpected error during GCP auth: {e}")
        raise
