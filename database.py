import logging
import os
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from google.api_core.exceptions import GoogleAPIError
from google.cloud import firestore


LOGGER = logging.getLogger(__name__)

REQUESTS_COLLECTION = os.getenv(
    "FIRESTORE_REQUESTS_COLLECTION",
    "requests",
)

USE_FIRESTORE = os.getenv(
    "USE_FIRESTORE",
    "true",
).lower() in {"1", "true", "yes"}


class DatabaseError(RuntimeError):
    """Raised when a database operation cannot be completed."""


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def get_firestore_client() -> firestore.Client:
    """
    Create a Firestore client using Application Default Credentials.

    Local development:
        gcloud auth application-default login

    Cloud Run:
        Uses the Cloud Run service account automatically.
    """
    project_id = (
        os.getenv("GOOGLE_CLOUD_PROJECT")
        or os.getenv("GCP_PROJECT")
        or None
    )

    database_id = os.getenv("FIRESTORE_DATABASE", "(default)")

    return firestore.Client(
        project=project_id,
        database=database_id,
    )


def serialize_document(
    document_id: str,
    data: dict[str, Any],
) -> dict[str, Any]:
    record = dict(data)
    record["id"] = document_id

    for field in ("created_at", "updated_at"):
        value = record.get(field)

        if isinstance(value, datetime):
            record[field] = value.isoformat()

    return record


def list_requests() -> list[dict[str, Any]]:
    if not USE_FIRESTORE:
        return []

    try:
        client = get_firestore_client()

        query = (
            client.collection(REQUESTS_COLLECTION)
            .order_by(
                "created_at",
                direction=firestore.Query.DESCENDING,
            )
        )

        return [
            serialize_document(snapshot.id, snapshot.to_dict())
            for snapshot in query.stream()
        ]

    except GoogleAPIError as exc:
        LOGGER.exception("Unable to list Firestore requests.")
        raise DatabaseError(
            "The request list could not be loaded from Firestore."
        ) from exc

    except Exception as exc:
        LOGGER.exception("Unexpected Firestore initialization error.")
        raise DatabaseError(
            "Firestore is not available in this environment."
        ) from exc


def create_request(
    request_data: dict[str, Any],
) -> dict[str, Any]:
    request_id = str(uuid4())
    now = utc_now()

    record = {
        **request_data,
        "id": request_id,
        "created_at": now,
        "updated_at": now,
    }

    if not USE_FIRESTORE:
        return serialize_document(request_id, record)

    try:
        client = get_firestore_client()

        (
            client.collection(REQUESTS_COLLECTION)
            .document(request_id)
            .set(record)
        )

        return serialize_document(request_id, record)

    except GoogleAPIError as exc:
        LOGGER.exception("Unable to create Firestore request.")
        raise DatabaseError(
            "The request could not be saved to Firestore."
        ) from exc

    except Exception as exc:
        LOGGER.exception("Unexpected Firestore write error.")
        raise DatabaseError(
            "Firestore is not available in this environment."
        ) from exc


def update_request(
    request_id: str,
    changes: dict[str, Any],
) -> None:
    if not request_id:
        raise ValueError("A request ID is required.")

    if not USE_FIRESTORE:
        return

    update_data = {
        **changes,
        "updated_at": utc_now(),
    }

    try:
        client = get_firestore_client()

        (
            client.collection(REQUESTS_COLLECTION)
            .document(request_id)
            .update(update_data)
        )

    except GoogleAPIError as exc:
        LOGGER.exception("Unable to update Firestore request.")
        raise DatabaseError(
            "The request could not be updated."
        ) from exc


def delete_request(request_id: str) -> None:
    if not request_id:
        raise ValueError("A request ID is required.")

    if not USE_FIRESTORE:
        return

    try:
        client = get_firestore_client()

        (
            client.collection(REQUESTS_COLLECTION)
            .document(request_id)
            .delete()
        )

    except GoogleAPIError as exc:
        LOGGER.exception("Unable to delete Firestore request.")
        raise DatabaseError(
            "The request could not be deleted."
        ) from exc


def test_connection() -> tuple[bool, str]:
    if not USE_FIRESTORE:
        return False, "Local session mode"

    try:
        client = get_firestore_client()
        client.collection(REQUESTS_COLLECTION).limit(1).get()

        return True, "Firestore connected"

    except Exception:
        return False, "Firestore unavailable"
