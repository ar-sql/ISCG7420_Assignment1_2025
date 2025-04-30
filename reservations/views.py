from datetime import datetime, timedelta
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

def home(request):
    reminder = None
    if request.user.is_authenticated:
        now = timezone.now()
        reminder = Reservation.objects.filter(
            user=request.user,
            start_time__gte=now,
            start_time__lt=now + timedelta(hours=24)
        ).order_by('start_time').first()
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
    rooms = Room.objects.all()
    return render(request, 'reservations/room_list.html', {'rooms': rooms})

def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk)
    upcoming = Reservation.objects.filter(
        room=room,
        end_time__gte=timezone.now()
    ).order_by('start_time')

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
                subject  = 'Your Room Reservation is Confirmed'
                text_body = render_to_string('emails/confirmation_email.txt', ctx)
                html_body = render_to_string('emails/confirmation_email.html', ctx)
                send_mail(subject, text_body, None, [res.user.email], html_message=html_body)
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
    reservations = Reservation.objects.filter(user=request.user).order_by('start_time')
    return render(request, 'reservations/my_reservations.html', {'reservations': reservations})

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
    return render(request, 'reservations/reservation_cancel.html', {'reservation': res})

def room_status(request):
    slot_s = request.GET.get('slot_start')
    slot_e = request.GET.get('slot_end')
    try:
        start = datetime.fromisoformat(slot_s) if slot_s else timezone.now()
    except (TypeError, ValueError):
        start = timezone.now()
    end = (datetime.fromisoformat(slot_e)
           if slot_e else start + timedelta(hours=1))

    status_list = []
    for room in Room.objects.all():
        occupied = Reservation.objects.filter(
            room=room,
            start_time__lt=end,
            end_time__gt=start
        ).exists()
        next_res = Reservation.objects.filter(
            room=room,
            start_time__gte=end
        ).order_by('start_time').first()
        status_list.append({
            'room':     room,
            'occupied': occupied,
            'next_res': next_res,
        })

    return render(request, 'reservations/room_status.html', {
        'status_list': status_list,
        'slot_start':  start,
        'slot_end':    end,
    })
