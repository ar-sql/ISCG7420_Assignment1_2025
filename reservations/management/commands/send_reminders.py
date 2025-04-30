import sys
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.core.mail           import send_mail
from django.template.loader     import render_to_string
from django.utils               import timezone
from reservations.models        import Reservation

class Command(BaseCommand):
    help = 'Send reminder emails for reservations happening in 24 hours.'

    def handle(self, *args, **options):
        now    = timezone.now()
        target = now + timedelta(days=1)
        upcoming = Reservation.objects.filter(
            start_time__gte=target,
            start_time__lt=target + timedelta(minutes=1)
        )
        if not upcoming:
            self.stdout.write('No reminders to send.')
            return

        for res in upcoming:
            subject   = 'Reminder: Your Reservation is Tomorrow'
            ctx       = {'reservation': res}
            text_msg  = render_to_string('emails/reminder_email.txt', ctx)
            html_msg  = render_to_string('emails/reminder_email.html', ctx)
            try:
                send_mail(subject, text_msg, None, [res.user.email], html_message=html_msg)
                self.stdout.write(f"Sent reminder to {res.user.email}")
            except Exception as e:
                self.stderr.write(f"Failed to send to {res.user.email}: {e}")
                sys.exit(1)
