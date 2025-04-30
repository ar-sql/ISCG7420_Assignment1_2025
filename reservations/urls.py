from django.urls import path
from . import views

urlpatterns = [
    path('',                 views.home,              name='home'),
    path('register/',        views.register,          name='register'),
    path('rooms/',           views.room_list,         name='room_list'),
    path('rooms/<int:pk>/',  views.room_detail,       name='room_detail'),
    path('my/',              views.my_reservations,   name='my_reservations'),
    path('edit/<int:pk>/',   views.reservation_edit,  name='reservation_edit'),
    path('cancel/<int:pk>/', views.reservation_cancel,name='reservation_cancel'),
    path('status/',          views.room_status,       name='room_status'),
]
