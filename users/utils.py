from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


def send_verification_email(user):
    """
    Generates a token and sends a verification email to the user.
    """
    token = PasswordResetTokenGenerator().make_token(user)
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

    verification_link = f"https://yourfrontend.com/verify-email/?uidb64={uidb64}&token={token}"

    subject = "Verify Your Email"
    message = f"Hi {user.username},\n\nPlease click the link below to verify your email:\n{verification_link}\n\nThank you!"
    from_email = "no-reply@example.com"
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)
