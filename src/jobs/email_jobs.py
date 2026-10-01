import asyncio

from src.utils.mail import send_email


def send_email_job(emails: list[str], subject: str, html: str):
    asyncio.run(send_email(emails=emails, subject=subject, html=html))
