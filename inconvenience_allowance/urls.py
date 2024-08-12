from django.urls import path
from .views import (
    InconvenienceRequestView,
    InconvenienceRequestLineView,
    InconvenienceRequestDetailView,
    InconvenienceRequestLineDetailView,
    TransitionStatusView,
    DayViewSet
)
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'days', DayViewSet)


urlpatterns = [
    path('inconvenience-requests/', InconvenienceRequestView.as_view(), name='inconvenience-request-list'),
    path('inconvenience-requests/<int:pk>/', InconvenienceRequestDetailView.as_view(), name='inconvenience-request-detail'),
    path('inconvenience-requests/<int:pk>/transition-status/', TransitionStatusView.as_view(), name='inconvenience-request-transition-status'),    path('inconvenience-request-lines/', InconvenienceRequestLineView.as_view(), name='inconvenience-request-line-list'),
    path('inconvenience-request-lines/', InconvenienceRequestLineView.as_view(), name='inconvenience-request-line-list'),
    path('inconvenience-request-lines/<int:pk>/', InconvenienceRequestLineDetailView.as_view(), name='inconvenience-request-line-detail'),

]