import os
from functools import lru_cache

import firebase_admin
import sqlalchemy
from fastapi import Header, HTTPException
from firebase_admin import auth as firebase_auth

from core.db import engine


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(status_code=401, detail=detail)


@lru_cache
def get_firebase_app():
    options = {}
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    if project_id:
        options["projectId"] = project_id

    service_account_file = os.getenv("FIREBASE_SERVICE_ACCOUNT_FILE")

    try:
        return firebase_admin.get_app()
    except ValueError:
        if service_account_file:
            from firebase_admin import credentials

            cred = credentials.Certificate(service_account_file)
            return firebase_admin.initialize_app(cred, options=options or None)

        # ADC を優先することで、Cloud Run と `gcloud auth application-default login`
        # の両方を同じ初期化コードで扱える。
        return firebase_admin.initialize_app(options=options or None)


def ensure_auth_tables() -> None:
    with engine.begin() as conn:
        conn.execute(
            sqlalchemy.text(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                    name TEXT NOT NULL
                )
                """
            )
        )
        conn.execute(
            sqlalchemy.text(
                """
                CREATE TABLE IF NOT EXISTS firebase_users (
                    firebase_uid TEXT PRIMARY KEY,
                    user_id BIGINT NOT NULL UNIQUE,
                    email TEXT,
                    display_name TEXT,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        )


def verify_token_and_get_claims(token: str) -> dict:
    get_firebase_app()

    try:
        claims = firebase_auth.verify_id_token(token)
    except firebase_auth.ExpiredIdTokenError as exc:
        raise _unauthorized("Firebase ID token has expired") from exc
    except firebase_auth.RevokedIdTokenError as exc:
        raise _unauthorized("Firebase ID token has been revoked") from exc
    except firebase_auth.InvalidIdTokenError as exc:
        raise _unauthorized("Firebase ID token is invalid") from exc
    except ValueError as exc:
        raise _unauthorized("Firebase ID token is missing") from exc

    provider = claims.get("firebase", {}).get("sign_in_provider")
    if provider != "google.com":
        raise HTTPException(status_code=403, detail="Google sign-in is required")

    if not claims.get("email_verified", False):
        raise HTTPException(status_code=403, detail="Verified email is required")

    allowed_domain = os.getenv("AUTH_ALLOWED_EMAIL_DOMAIN", "").strip().lower()
    email = (claims.get("email") or "").strip().lower()
    if allowed_domain and not email.endswith(f"@{allowed_domain}"):
        raise HTTPException(
            status_code=403,
            detail=f"{allowed_domain} domain is required",
        )

    return claims


def verify_token_and_get_user_id(token: str) -> int:
    claims = verify_token_and_get_claims(token)
    user = upsert_firebase_user(claims)
    return user["user_id"]


def upsert_firebase_user(claims: dict) -> dict:
    ensure_auth_tables()

    firebase_uid = claims["uid"]
    email = claims.get("email")
    display_name = claims.get("name") or email or firebase_uid

    with engine.begin() as conn:
        existing = conn.execute(
            sqlalchemy.text(
                """
                SELECT fu.user_id
                FROM firebase_users fu
                WHERE fu.firebase_uid = :firebase_uid
                """
            ),
            {"firebase_uid": firebase_uid},
        ).mappings().fetchone()

        if existing is None:
            created_user = conn.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO users (name)
                    VALUES (:name)
                    RETURNING id, name
                    """
                ),
                {"name": display_name},
            ).mappings().fetchone()

            conn.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO firebase_users (
                        firebase_uid,
                        user_id,
                        email,
                        display_name
                    )
                    VALUES (
                        :firebase_uid,
                        :user_id,
                        :email,
                        :display_name
                    )
                    """
                ),
                {
                    "firebase_uid": firebase_uid,
                    "user_id": created_user["id"],
                    "email": email,
                    "display_name": display_name,
                },
            )

            return {
                "user_id": created_user["id"],
                "firebase_uid": firebase_uid,
                "email": email,
                "name": created_user["name"],
            }

        conn.execute(
            sqlalchemy.text(
                """
                UPDATE users
                SET name = :name
                WHERE id = :user_id
                """
            ),
            {"user_id": existing["user_id"], "name": display_name},
        )

        conn.execute(
            sqlalchemy.text(
                """
                UPDATE firebase_users
                SET
                    email = :email,
                    display_name = :display_name,
                    updated_at = CURRENT_TIMESTAMP
                WHERE firebase_uid = :firebase_uid
                """
            ),
            {
                "firebase_uid": firebase_uid,
                "email": email,
                "display_name": display_name,
            },
        )

        return {
            "user_id": existing["user_id"],
            "firebase_uid": firebase_uid,
            "email": email,
            "name": display_name,
        }


def get_current_user(authorization: str | None = Header(default=None)) -> dict:
    if not authorization:
        raise _unauthorized("Authorization header is required")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise _unauthorized("Authorization header must use Bearer token")

    claims = verify_token_and_get_claims(token)
    user = upsert_firebase_user(claims)

    return {
        "user_id": user["user_id"],
        "firebase_uid": user["firebase_uid"],
        "email": user["email"],
        "name": user["name"],
    }
