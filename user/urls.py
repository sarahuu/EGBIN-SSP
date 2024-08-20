from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet,UserDetailView,UserView,MicrosoftTokenValidationView,UserOwnView, CustomTokenObtainPairView,CustomTokenRefreshView

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet)


 
urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),    path('', UserView.as_view(), name="user_list"),
    path('<int:pk>/',UserDetailView.as_view(),name="user_view"),
    path('validate-token/', MicrosoftTokenValidationView.as_view(), name='validate_token'),
    path('own/', UserOwnView.as_view(), name='user_own_view')
]
