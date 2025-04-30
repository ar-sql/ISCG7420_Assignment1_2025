# reservations/models.py

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Room(models.Model):
    name        = models.CharField(max_length=100)
    location    = models.CharField(max_length=100)
    capacity    = models.PositiveIntegerField()
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Reservation(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    room       = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time   = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_time']
        unique_together = ('room', 'start_time', 'end_time')

    def clean(self):
        """
        Prevent overlapping bookings.
        Uses room_id so we never try to fetch self.room before it's set.
        """
        if not self.room_id:
            # nothing to check yet
            return

        # look for any reservation on this room overlapping our times
        overlapping = Reservation.objects.filter(
            room_id=self.room_id,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        )
        if self.pk:
            overlapping = overlapping.exclude(pk=self.pk)

        if overlapping.exists():
            raise ValidationError('Time slot already booked.')

    def __str__(self):
        return f"{self.room.name} ({self.start_time:%Y-%m-%d %H:%M}–{self.end_time:%H:%M}) by {self.user.username}"
