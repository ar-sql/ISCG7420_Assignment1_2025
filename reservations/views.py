from datetime import datetime, date, time, timedelta
from django.shortcuts               import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth            import login
from django.contrib.auth.views      import redirect_to_login
from django.contrib                 import messages
from django.utils                   import timezone
from django.core.mail               import send_mail
from django.template.loader         import render_to_string

from .models import Room, Reservation
from .forms  import ReservationForm, RegisterForm

# Māori names for rooms 1–10
MAORI_NUMBERS = {
    1: 'Tahi',   2: 'Rua',    3: 'Toru',  4: 'Whā',   5: 'Rima',
    6: 'Ono',    7: 'Whitu',  8: 'Waru',  9: 'Iwa',  10: 'Tekau',
}

def home(request):
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
    rooms = list(Room.objects.all().order_by('pk'))
    for room in rooms:
        room.display_name = MAORI_NUMBERS.get(room.pk, room.name)
    return render(request, 'reservations/room_list.html', {'rooms': rooms})

def room_detail(request, pk):
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
                messages.success(request, 'Reservation confirmed (email sent).')
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
    reservations = (
        Reservation.objects
        .filter(user=request.user)
        .order_by('start_time')
    )
    return render(request, 'reservations/my_reservations.html',
                  {'reservations': reservations})

@login_required
def reservation_edit(request, pk):
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
        'reservation': res,
        'form':        form,
    })

@login_required
def reservation_cancel(request, pk):
    res = get_object_or_404(Reservation, pk=pk, user=request.user)
    if request.method == 'POST':
        res.delete()
        messages.success(request, 'Reservation cancelled.')
        return redirect('my_reservations')
    return render(request, 'reservations/reservation_cancel.html',
                  {'reservation': res})

def room_status(request):
    """
    Display a grid of rooms vs hourly slots (08:00–18:00).
    Users can browse any date >= today via ?date=YYYY-MM-DD
    """
    today    = timezone.localtime().date()
    date_str = request.GET.get('date')
    if date_str:
        try:
            selected = date.fromisoformat(date_str)
        except ValueError:
            selected = today
    else:
        selected = today

    prev_date = (selected - timedelta(days=1)) if selected > today else None
    next_date = selected + timedelta(days=1)

    tz    = timezone.get_current_timezone()
    slots = []
    for hour in range(8, 18):
        start = datetime.combine(selected, time(hour, 0)).replace(tzinfo=tz)
        end   = start + timedelta(hours=1)
        slots.append((start, end))

    table = []
    for room in Room.objects.order_by('pk'):
        display  = MAORI_NUMBERS.get(room.pk, room.name)
        statuses = []
        for slot_start, slot_end in slots:
            occupied = Reservation.objects.filter(
                room=room,
                start_time__lt=slot_end,
                end_time__gt=slot_start
            ).exists()
            statuses.append(occupied)
        table.append({'display': display, 'statuses': statuses})

    return render(request, 'reservations/room_status.html', {
        'date':      selected,
        'prev_date': prev_date,
        'next_date': next_date,
        'slots':     slots,
        'table':     table,
        'today':     today,
    })
