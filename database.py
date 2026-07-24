import json
import os
import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


class DatabaseError(Exception):
    """Raised when ValueBridge cannot complete a database operation."""


USE_FIRESTORE = os.getenv("USE_FIRESTORE", "false").strip().lower() == "true"

FIRESTORE_PROJECT_ID = os.getenv(
    "FIRESTORE_PROJECT_ID",
    os.getenv("GOOGLE_CLOUD_PROJECT", ""),
)

FIRESTORE_DATABASE_ID = os.getenv(
    "FIRESTORE_DATABASE_ID",
    "(default)",
)

FIRESTORE_REQUESTS_COLLECTION = os.getenv(
    "FIRESTORE_REQUESTS_COLLECTION",
    "requests",
)

LOCAL_DATA_DIRECTORY = Path(__file__).resolve().parent / "data"
LOCAL_DATA_FILE = LOCAL_DATA_DIRECTORY / "business_cases.json"


def _utc_now() -> str:
    """Return the current UTC timestamp in ISO format."""

    return datetime.now(timezone.utc).isoformat()


def _serialize_value(value: Any) -> Any:
    """Convert values into JSON- and Firestore-safe formats."""

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, dict):
        return {
            str(key): _serialize_value(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [_serialize_value(item) for item in value]

    return value


def _get_firestore_client():
    """Create and return the Firestore client."""

    try:
        from google.cloud import firestore
    except ImportError as exc:
        raise DatabaseError(
            "Firestore is enabled, but google-cloud-firestore is not installed."
        ) from exc

    if not FIRESTORE_PROJECT_ID:
        raise DatabaseError(
            "Firestore is enabled, but FIRESTORE_PROJECT_ID is not configured."
        )

    try:
        return firestore.Client(
            project=FIRESTORE_PROJECT_ID,
            database=FIRESTORE_DATABASE_ID,
        )
    except Exception as exc:
        raise DatabaseError(
            f"Unable to connect to Firestore: {exc}"
        ) from exc


def _ensure_local_file() -> None:
    """Create the local data directory and file when needed."""

    try:
        LOCAL_DATA_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not LOCAL_DATA_FILE.exists():
            LOCAL_DATA_FILE.write_text(
                "[]",
                encoding="utf-8",
            )

    except OSError as exc:
        raise DatabaseError(
            f"Unable to initialize local storage: {exc}"
        ) from exc


def _read_local_cases() -> list[dict[str, Any]]:
    """Read all locally stored business cases."""

    _ensure_local_file()

    try:
        raw_content = LOCAL_DATA_FILE.read_text(
            encoding="utf-8",
        )

        data = json.loads(raw_content)

    except json.JSONDecodeError:
        data = []

    except OSError as exc:
        raise DatabaseError(
            f"Unable to read local business cases: {exc}"
        ) from exc

    if not isinstance(data, list):
        return []

    return [
        item
        for item in data
        if isinstance(item, dict)
    ]


def _write_local_cases(
    cases: list[dict[str, Any]],
) -> None:
    """Write all business cases to local storage."""

    _ensure_local_file()

    try:
        LOCAL_DATA_FILE.write_text(
            json.dumps(
                cases,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    except OSError as exc:
        raise DatabaseError(
            f"Unable to write local business cases: {exc}"
        ) from exc


def initialize_database() -> tuple[bool, str]:
    """
    Initialize the configured database.

    This function is retained for compatibility with app.py.
    """

    try:
        if USE_FIRESTORE:
            client = _get_firestore_client()

            list(
                client.collection(
                    FIRESTORE_REQUESTS_COLLECTION
                ).limit(1).stream()
            )

            return True, "Firestore initialized"

        _ensure_local_file()
        return True, "Local storage initialized"

    except Exception as exc:
        return False, str(exc)


def save_request(
    case_data: dict[str, Any],
) -> str:
    """
    Create or update a ValueBridge business case.

    When an ID is included, the existing case is updated.
    Otherwise, a new case is created.

    Returns:
        The saved business-case ID.
    """

    if not isinstance(case_data, dict):
        raise DatabaseError(
            "Business-case data must be provided as a dictionary."
        )

    try:
        case_id = str(
            case_data.get("id")
            or case_data.get("request_id")
            or uuid.uuid4()
        )

        now = _utc_now()

        record = {
            **case_data,
            "id": case_id,
            "request_id": case_id,
            "created_at": case_data.get(
                "created_at",
                now,
            ),
            "updated_at": now,
            "status": case_data.get(
                "status",
                "Saved",
            ),
        }

        record = _serialize_value(record)

        if USE_FIRESTORE:
            client = _get_firestore_client()

            client.collection(
                FIRESTORE_REQUESTS_COLLECTION
            ).document(case_id).set(
                record,
                merge=True,
            )

            return case_id

        cases = _read_local_cases()

        existing_index = next(
            (
                index
                for index, item in enumerate(cases)
                if (
                    item.get("id") == case_id
                    or item.get("request_id") == case_id
                )
            ),
            None,
        )

        if existing_index is None:
            cases.append(record)
        else:
            existing_record = cases[existing_index]

            cases[existing_index] = {
                **existing_record,
                **record,
                "created_at": existing_record.get(
                    "created_at",
                    record["created_at"],
                ),
            }

        _write_local_cases(cases)

        return case_id

    except DatabaseError:
        raise

    except Exception as exc:
        raise DatabaseError(
            f"Unable to save the business case: {exc}"
        ) from exc


def create_request(
    case_data: dict[str, Any],
) -> str:
    """
    Compatibility wrapper for older ValueBridge code.

    Creates a new business case.
    """

    new_record = {
        **case_data,
        "id": None,
        "request_id": None,
    }

    return save_request(new_record)


def update_request(
    request_id: str,
    case_data: dict[str, Any],
) -> str:
    """
    Update an existing business case.

    Retained for compatibility with older app code.
    """

    if not request_id:
        raise DatabaseError(
            "A request ID is required to update a business case."
        )

    updated_record = {
        **case_data,
        "id": request_id,
        "request_id": request_id,
    }

    return save_request(updated_record)


def get_request(
    request_id: str,
) -> dict[str, Any] | None:
    """Retrieve one business case by ID."""

    if not request_id:
        return None

    try:
        if USE_FIRESTORE:
            client = _get_firestore_client()

            snapshot = client.collection(
                FIRESTORE_REQUESTS_COLLECTION
            ).document(request_id).get()

            if not snapshot.exists:
                return None

            result = snapshot.to_dict() or {}

            result["id"] = snapshot.id
            result["request_id"] = snapshot.id

            return result

        cases = _read_local_cases()

        return next(
            (
                item
                for item in cases
                if (
                    item.get("id") == request_id
                    or item.get("request_id") == request_id
                )
            ),
            None,
        )

    except DatabaseError:
        raise

    except Exception as exc:
        raise DatabaseError(
            f"Unable to retrieve the business case: {exc}"
        ) from exc


def list_requests(
    limit: int = 100,
) -> list[dict[str, Any]]:
    """Return saved business cases, newest first."""

    safe_limit = max(1, int(limit))

    try:
        if USE_FIRESTORE:
            from google.cloud import firestore

            client = _get_firestore_client()

            query = (
                client.collection(
                    FIRESTORE_REQUESTS_COLLECTION
                )
                .order_by(
                    "updated_at",
                    direction=firestore.Query.DESCENDING,
                )
                .limit(safe_limit)
            )

            results: list[dict[str, Any]] = []

            for snapshot in query.stream():
                record = snapshot.to_dict() or {}

                record["id"] = snapshot.id
                record["request_id"] = snapshot.id

                results.append(record)

            return results

        cases = _read_local_cases()

        return sorted(
            cases,
            key=lambda item: str(
                item.get(
                    "updated_at",
                    item.get("created_at", ""),
                )
            ),
            reverse=True,
        )[:safe_limit]

    except DatabaseError:
        raise

    except Exception as exc:
        raise DatabaseError(
            f"Unable to list business cases: {exc}"
        ) from exc


def get_requests(
    limit: int = 100,
) -> list[dict[str, Any]]:
    """Compatibility alias for list_requests."""

    return list_requests(limit=limit)


def update_request_status(
    request_id: str,
    status: str,
) -> str:
    """Update only the status of an existing business case."""

    existing_case = get_request(request_id)

    if existing_case is None:
        raise DatabaseError(
            "The requested business case could not be found."
        )

    existing_case["status"] = status

    return save_request(existing_case)


def delete_request(
    request_id: str,
) -> None:
    """Delete a business case."""

    if not request_id:
        raise DatabaseError(
            "A request ID is required to delete a business case."
        )

    try:
        if USE_FIRESTORE:
            client = _get_firestore_client()

            client.collection(
                FIRESTORE_REQUESTS_COLLECTION
            ).document(request_id).delete()

            return

        cases = [
            item
            for item in _read_local_cases()
            if (
                item.get("id") != request_id
                and item.get("request_id") != request_id
            )
        ]

        _write_local_cases(cases)

    except DatabaseError:
        raise

    except Exception as exc:
        raise DatabaseError(
            f"Unable to delete the business case: {exc}"
        ) from exc


def test_connection() -> tuple[bool, str]:
    """Test the configured storage connection."""

    try:
        if USE_FIRESTORE:
            client = _get_firestore_client()

            list(
                client.collection(
                    FIRESTORE_REQUESTS_COLLECTION
                ).limit(1).stream()
            )

            return True, "Connected to Firestore"

        _ensure_local_file()

        return True, "Connected to local storage"

    except Exception as exc:
        return False, str(exc)


def get_database_status() -> dict[str, Any]:
    """Return basic information about the configured database."""

    connected, message = test_connection()

    return {
        "connected": connected,
        "message": message,
        "storage_type": (
            "Firestore"
            if USE_FIRESTORE
            else "Local JSON"
        ),
        "project_id": (
            FIRESTORE_PROJECT_ID
            if USE_FIRESTORE
            else None
        ),
        "collection": (
            FIRESTORE_REQUESTS_COLLECTION
            if USE_FIRESTORE
            else None
        ),
        "local_file": (
            str(LOCAL_DATA_FILE)
            if not USE_FIRESTORE
            else None
        ),
    }
