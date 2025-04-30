from django.contrib import admin
from .models import Room, Reservation




class ReservationInline(admin.TabularInline):
    """
    Show reservations inline on the Room admin page.
    """
    model = Reservation
    extra = 0
    fields = ('user', 'start_time', 'end_time', 'created_at')
    readonly_fields = ('created_at',)

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    """
    Admin interface for Rooms.
    """
    list_display  = ('name', 'location', 'capacity')
    search_fields = ('name', 'location')
    list_filter   = ('capacity',)
    inlines       = [ReservationInline]

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    """
    Admin interface for Reservations.
    """
    list_display   = ('room', 'user', 'start_time', 'end_time', 'created_at')
    list_filter    = ('room', 'user')
    search_fields  = ('room__name', 'user__username')
    date_hierarchy = 'start_time'
