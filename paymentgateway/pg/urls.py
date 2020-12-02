from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('response/', views.order, name="response"),
    path('payment/', views.payment, name="payment"),
    path('reverse/', views.reverse, name="reverse"),
    path(r'^done/', views.manual, name="done")
]
