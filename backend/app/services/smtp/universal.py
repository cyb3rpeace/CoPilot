from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from app import db
from app.models.smtp import EmailCredentials
from app.models.smtp import email_credentials_schema


class UniversalEmailCredentials:
    @staticmethod
    def create(email: str, password: str, smtp_server: str, smtp_port: int) -> Dict[str, Union[int, str]]:
        """
        Delete all existing email credentials, create new email credentials and add them to the database.

        :param email: Email address.
        :param password: Email password.
        :param smtp_server: SMTP server address.
        :param smtp_port: SMTP server port.
        :return: Dictionary of the created email credentials.
        """
        UniversalEmailCredentials.delete_all()

        new_credential = EmailCredentials(email, password, smtp_server, smtp_port)
        db.session.add(new_credential)
        db.session.commit()
        return {
            "message": "Email credentials created successfully.",
            "success": True,
            "email_settings": email_credentials_schema.dump(new_credential),
        }

    @staticmethod
    def read_by_id(id: int) -> Optional[Dict[str, Union[int, str]]]:
        """
        Fetch email credentials by their id.

        :param id: ID of the email credentials.
        :return: Dictionary of the email credentials or None if not found.
        """
        credential = EmailCredentials.query.get(id)
        return email_credentials_schema.dump(credential) if credential else None

    @staticmethod
    def read_by_email(email: str) -> Optional[Dict[str, Union[int, str]]]:
        """
        Fetch email credentials by email address.

        :param email: Email address.
        :return: Dictionary of the email credentials or None if not found.
        """
        credential = EmailCredentials.query.filter_by(email=email).first()
        return email_credentials_schema.dump(credential) if credential else None

    @staticmethod
    def read_all() -> List[Dict[str, Union[int, str]]]:
        """
        Fetch all email credentials.

        :return: List of dictionaries of all email credentials.
        """
        credentials = EmailCredentials.query.all()
        return {
            "message": "Email credentials retrieved successfully.",
            "success": True,
            "emails_configured": email_credentials_schema.dump(credentials, many=True),
        }

    @staticmethod
    def update(
        id: int,
        email: Optional[str] = None,
        password: Optional[str] = None,
        smtp_server: Optional[str] = None,
        smtp_port: Optional[int] = None,
    ) -> Optional[Dict[str, Union[int, str]]]:
        """
        Update existing email credentials. If more than one credential exists, delete all and create a new one.

        :param id: ID of the email credentials.
        :param email: New email address.
        :param password: New email password.
        :param smtp_server: New SMTP server address.
        :param smtp_port: New SMTP server port.
        :return: Dictionary of the updated email credentials or None if not found.
        """
        credential = EmailCredentials.query.get(id)
        if not credential:
            return None
        if email is not None:
            credential.email = email
        if password is not None:
            credential.password = password
        if smtp_server is not None:
            credential.smtp_server = smtp_server
        if smtp_port is not None:
            credential.smtp_port = smtp_port

        UniversalEmailCredentials.delete_all_except_id(id)

        db.session.commit()
        return email_credentials_schema.dump(credential)

    @staticmethod
    def delete_all():
        """
        Delete all email credentials from the table.
        """
        EmailCredentials.query.delete()
        db.session.commit()

    @staticmethod
    def delete_all_except_id(id: int):
        """
        Delete all email credentials except the one with the given id.

        :param id: ID of the email credentials to keep.
        """
        EmailCredentials.query.filter(EmailCredentials.id != id).delete()
        db.session.commit()
