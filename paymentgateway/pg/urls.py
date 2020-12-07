from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    #path('response/', views.order, name="response"), # for order
    path('response/', views.subscription, name="response"),  # for subscription
    path('payment/', views.payment, name="payment"),
    path('reverse/', views.reverse, name="reverse"),
    path(r'^done/', views.manual, name="done")
]
