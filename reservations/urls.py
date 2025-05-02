# reservations/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home & Auth
    path('',                    views.home,               name='home'),
    path('login/',              auth_views.LoginView.as_view(
                                  template_name='registration/login.html'
                                ),                       name='login'),
    path('logout/',             auth_views.LogoutView.as_view(), name='logout'),
    path('register/',           views.register,           name='register'),

    # User-facing
    path('rooms/',              views.room_list,          name='room_list'),
    path('rooms/<int:pk>/',     views.room_detail,        name='room_detail'),
    path('my_reservations/',    views.my_reservations,    name='my_reservations'),
    path('edit/<int:pk>/',      views.reservation_edit,   name='reservation_edit'),
    path('cancel/<int:pk>/',    views.reservation_cancel, name='reservation_cancel'),
    path('status/',             views.room_status,        name='room_status'),

    # In-app Admin Panel (staff only)
    path('admin/',                        views.admin_dashboard,           name='admin_dashboard'),
    path('admin/rooms/',                  views.admin_room_list,           name='admin_room_list'),
    path('admin/rooms/add/',              views.admin_room_create,         name='admin_room_create'),
    path('admin/rooms/<int:pk>/edit/',    views.admin_room_edit,           name='admin_room_edit'),
    path('admin/rooms/<int:pk>/delete/',  views.admin_room_delete,         name='admin_room_delete'),

    path('admin/reservations/',           views.admin_reservation_list,    name='admin_reservation_list'),
    path('admin/reservations/add/',       views.admin_reservation_create,  name='admin_reservation_create'),
    path('admin/reservations/<int:pk>/cancel/',
                                          views.admin_reservation_cancel,  name='admin_reservation_cancel'),

    path('admin/users/',                  views.admin_user_list,           name='admin_user_list'),
    path('admin/users/add/',              views.admin_user_create,         name='admin_user_create'),
    path('admin/users/<int:pk>/edit/',    views.admin_user_edit,           name='admin_user_edit'),
    path('admin/users/<int:pk>/delete/',  views.admin_user_delete,         name='admin_user_delete'),
]
