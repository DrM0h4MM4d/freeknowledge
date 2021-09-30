from __future__ import absolute_import, unicode_literals
from celery.app import shared_task
from django.utils import timezone
# from .models import NotificationAdminCenter, ChallengeEvent
from django.core.mail import EmailMessage


# @shared_task
# def expire_date_checker():
#     notifs = NotificationAdminCenter.objects.all()
#     challenges = ChallengeEvent.objects.all()

#     for i in notifs:
#         if i.expr_date < timezone.now():
#             i.delete()
#             print("An Instance of notifications model deleted: notif expired.")

#     for i in challenges:
#         if i.expr_date < timezone.now():
#             i.delete()
#             print("An Instance of challenges model deleted: challenge expired.")


@shared_task
def send_email(mail_subject, message, to_email):
    email = EmailMessage(
                mail_subject, message, to=[to_email]
    )
    email.send()
