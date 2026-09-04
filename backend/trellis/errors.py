from flask import Flask, jsonify
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException

from trellis.auth import AuthenticationError
from trellis.extensions import db


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(AuthenticationError)
    def handle_authentication_error(error: AuthenticationError):
        return jsonify(error="unauthorized", message=str(error)), 401

    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError):
        first_error = error.errors()[0]
        return jsonify(error="validation_error", message=first_error["msg"]), 422

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(_error: IntegrityError):
        db.session.rollback()
        return (
            jsonify(error="conflict", message="The record conflicts with existing data."),
            409,
        )

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        return (
            jsonify(
                error=error.name.lower().replace(" ", "_"),
                message=error.description,
            ),
            error.code,
        )

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        app.logger.exception("Unhandled API error", exc_info=error)
        return (
            jsonify(
                error="internal_server_error",
                message="An unexpected error occurred.",
            ),
            500,
        )
