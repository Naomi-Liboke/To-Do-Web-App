from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from email.mime.image import MIMEImage
import os
from django.conf import settings

def send_html_email_with_logo(subject, template_name, context, recipient):
    # Render HTML content
    html_content = render_to_string(template_name, context)

    # Create email object
    msg = EmailMultiAlternatives(subject, '', settings.DEFAULT_FROM_EMAIL, [recipient])
    msg.attach_alternative(html_content, "text/html")

    # Attach logo image inline
    logo_path = os.path.join(settings.BASE_DIR, 'to_do_app', 'static', 'to_do_app', 'images', 'focusflow-logo.png')
    with open(logo_path, 'rb') as f:
        logo = MIMEImage(f.read())
        logo.add_header('Content-ID', '<focusflow_logo>')
        logo.add_header('Content-Disposition', 'inline', filename='focusflow-logo.png')
        msg.attach(logo)

    # Send email
    msg.send()
