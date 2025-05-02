# reservations/views.py

from datetime import datetime, date, time, timedelta

from django.shortcuts               import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth            import login
from django.contrib.auth.views      import redirect_to_login
from django.contrib.auth.models     import User
from django.contrib                 import messages
from django.utils                   import timezone
from django.core.mail               import send_mail
from django.template.loader         import render_to_string

from .models import Room, Reservation
from .forms  import (
    ReservationForm,
    RegisterForm,
    RoomForm,
    AdminReservationForm,
    AdminUserCreationForm,
    AdminUserChangeForm,
)

# ─── Helpers & Constants ──────────────────────────────────────────────────────

MAORI_NUMBERS = {
    1: 'Tahi',   2: 'Rua',    3: 'Toru',  4: 'Whā',   5: 'Rima',
    6: 'Ono',    7: 'Whitu',  8: 'Waru',  9: 'Iwa',  10: 'Tekau',
}

def admin_required(view_func):
    """
    Decorator to restrict a view to staff users only.
    Unauthenticated users are sent to the login page.
    """
    return user_passes_test(lambda u: u.is_staff, login_url='login')(view_func)


# ─── Public / User Views ──────────────────────────────────────────────────────

def home(request):
    """
    Landing page. Shows a reminder of your next reservation within 24h (if any).
    """
    reminder = None
    if request.user.is_authenticated:
        now = timezone.now()
        reminder = (
            Reservation.objects
            .filter(
                user=request.user,
                start_time__gte=now,
                start_time__lt=now + timedelta(hours=24)
            )
            .order_by('start_time')
            .first()
        )
    return render(request, 'home.html', {'reminder': reminder})


def register(request):
    """
    User registration: collects username, email, names, password.
    On success, logs the user in and redirects to room_list.
    """
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email      = form.cleaned_data['email']
            user.first_name = form.cleaned_data['first_name']
            user.last_name  = form.cleaned_data['last_name']
            try:
                user.save()
                login(request, user)
                messages.success(request, 'Account created successfully! 🎉')
                return redirect('room_list')
            except Exception as e:
                messages.error(request, f'Error creating account: {e}')
        else:
            for field, errs in form.errors.items():
                for err in errs:
                    messages.error(request, f"{field}: {err}")
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


def room_list(request):
    """
    Show all conference rooms with Māori names.
    """
    rooms = list(Room.objects.all().order_by('pk'))
    for room in rooms:
        room.display_name = MAORI_NUMBERS.get(room.pk, room.name)
    return render(request, 'reservations/room_list.html', {'rooms': rooms})


def room_detail(request, pk):
    """
    Show details and upcoming bookings for a room; allow booking if logged in.
    Sends confirmation email on success.
    """
    room = get_object_or_404(Room, pk=pk)
    room.display_name = MAORI_NUMBERS.get(room.pk, room.name)

    upcoming = (
        Reservation.objects
        .filter(room=room, end_time__gte=timezone.now())
        .order_by('start_time')
    )

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect_to_login(request.path)
        form = ReservationForm(request.POST)
        if form.is_valid():
            res = form.save(commit=False)
            res.user, res.room = request.user, room
            try:
                res.clean()
                res.save()
                # send confirmation email
                ctx = {'reservation': res}
                subject   = 'Your Room Reservation is Confirmed'
                text_body = render_to_string('emails/confirmation_email.txt', ctx)
                html_body = render_to_string('emails/confirmation_email.html', ctx)
                send_mail(subject, text_body, None, [res.user.email],
                          html_message=html_body)
                messages.success(request, 'Reservation confirmed and emailed.')
                return redirect('my_reservations')
            except Exception as e:
                messages.error(request, e)
        else:
            for field, errs in form.errors.items():
                for err in errs:
                    messages.error(request, f"{field}: {err}")
    else:
        form = ReservationForm()

    return render(request, 'reservations/room_detail.html', {
        'room':     room,
        'form':     form,
        'upcoming': upcoming,
    })


@login_required
def my_reservations(request):
    """
    List reservations for the logged-in user.
    """
    qs = Reservation.objects.filter(user=request.user).order_by('start_time')
    return render(request, 'reservations/my_reservations.html', {'reservations': qs})


@login_required
def reservation_edit(request, pk):
    """
    Let a user edit their own reservation.
    """
    res = get_object_or_404(Reservation, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=res)
        if form.is_valid():
            updated = form.save(commit=False)
            try:
                updated.clean()
                updated.save()
                messages.success(request, 'Reservation updated.')
                return redirect('my_reservations')
            except Exception as e:
                messages.error(request, e)
        else:
            for field, errs in form.errors.items():
                for err in errs:
                    messages.error(request, f"{field}: {err}")
    else:
        form = ReservationForm(instance=res)
    return render(request, 'reservations/reservation_edit.html', {
        'reservation': res, 'form': form
    })


@login_required
def reservation_cancel(request, pk):
    """
    Let a user cancel their own reservation.
    """
    res = get_object_or_404(Reservation, pk=pk, user=request.user)
    if request.method == 'POST':
        res.delete()
        messages.success(request, 'Reservation cancelled.')
        return redirect('my_reservations')
    return render(request, 'reservations/reservation_cancel.html', {'reservation': res})


def room_status(request):
    """
    Show availability grid for a date (08:00–18:00), grouped by time of day,
    disallow navigation to past dates.
    """
    today    = timezone.localtime().date()
    date_str = request.GET.get('date')
    try:
        selected = date.fromisoformat(date_str) if date_str else today
    except ValueError:
        selected = today

    prev_date = selected - timedelta(days=1) if selected > today else None
    next_date = selected + timedelta(days=1)

    tz    = timezone.get_current_timezone()
    slots = []
    hours = []
    for h in range(8, 18):
        start = datetime.combine(selected, time(h, 0)).replace(tzinfo=tz)
        end   = start + timedelta(hours=1)
        slots.append((start, end))
        hours.append(h)

    periods = [
        ('Morning',   range(8, 12)),
        ('Afternoon', range(12, 17)),
        ('Evening',   range(17, 18)),
    ]
    groups = []
    for label, rng in periods:
        count = sum(1 for h in hours if h in rng)
        if count:
            groups.append({'label': label, 'count': count})

    table = []
    for room in Room.objects.order_by('pk'):
        statuses = [
            Reservation.objects.filter(
                room=room,
                start_time__lt=end,
                end_time__gt=start
            ).exists()
            for start, end in slots
        ]
        table.append({
            'display':   MAORI_NUMBERS.get(room.pk, room.name),
            'statuses': statuses
        })

    return render(request, 'reservations/room_status.html', {
        'today':     today,
        'date':      selected,
        'prev_date': prev_date,
        'next_date': next_date,
        'groups':    groups,
        'slots':     slots,
        'table':     table,
    })


# ─── In-App Admin Panel Views ───────────────────────────────────────────────────

@admin_required
def admin_dashboard(request):
    return render(request, 'admin/dashboard.html')


@admin_required
def admin_room_list(request):
    rooms = Room.objects.order_by('pk')
    return render(request, 'admin/room_list.html', {'rooms': rooms})


@admin_required
def admin_room_create(request):
    form = RoomForm(request.POST or None)
    if form.is_valid():
        form.save(); messages.success(request, 'Room added.')
        return redirect('admin_room_list')
    return render(request, 'admin/room_form.html', {'form': form, 'title': 'Add Room'})


@admin_required
def admin_room_edit(request, pk):
    room = get_object_or_404(Room, pk=pk)
    form = RoomForm(request.POST or None, instance=room)
    if form.is_valid():
        form.save(); messages.success(request, 'Room updated.')
        return redirect('admin_room_list')
    return render(request, 'admin/room_form.html', {'form': form, 'title': 'Edit Room'})


@admin_required
def admin_room_delete(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        room.delete(); messages.success(request, 'Room deleted.')
        return redirect('admin_room_list')
    return render(request, 'admin/confirm_delete.html', {'object': room, 'type': 'Room'})


@admin_required
def admin_reservation_list(request):
    qs = Reservation.objects.select_related('user', 'room').order_by('-start_time')
    return render(request, 'admin/reservation_list.html', {'reservations': qs})


@admin_required
def admin_reservation_create(request):
    form = AdminReservationForm(request.POST or None)
    if form.is_valid():
        form.save(); messages.success(request, 'Reservation created.')
        return redirect('admin_reservation_list')
    return render(request, 'admin/reservation_form.html', {'form': form, 'title': 'Add Reservation'})


@admin_required
def admin_reservation_cancel(request, pk):
    res = get_object_or_404(Reservation, pk=pk)
    if request.method == 'POST':
        res.delete(); messages.success(request, 'Reservation cancelled.')
        return redirect('admin_reservation_list')
    return render(request, 'admin/confirm_delete.html', {'object': res, 'type': 'Reservation'})


@admin_required
def admin_user_list(request):
    users = User.objects.order_by('username')
    return render(request, 'admin/user_list.html', {'users': users})


@admin_required
def admin_user_create(request):
    form = AdminUserCreationForm(request.POST or None)
    if form.is_valid():
        form.save(); messages.success(request, 'User created.')
        return redirect('admin_user_list')
    return render(request, 'admin/user_form.html', {'form': form, 'title': 'Add User'})


@admin_required
def admin_user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = AdminUserChangeForm(request.POST or None, instance=user)
    if form.is_valid():
        form.save(); messages.success(request, 'User updated.')
        return redirect('admin_user_list')
    return render(request, 'admin/user_form.html', {'form': form, 'title': 'Edit User'})


@admin_required
def admin_user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete(); messages.success(request, 'User deleted.')
        return redirect('admin_user_list')
    return render(request, 'admin/confirm_delete.html', {'object': user, 'type': 'User'})
