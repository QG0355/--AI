from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomAuthToken, RegisterView, TicketViewSet, bind_identity
from django.urls import path
from . import views


router = DefaultRouter()
router.register(r'tickets', TicketViewSet, basename='ticket')

urlpatterns = [
    path('login/', CustomAuthToken.as_view(), name='api_login'),
    path('register/', RegisterView.as_view(), name='api_register'),
    path('bind-identity/', bind_identity, name='api_bind_identity'),
    path('', include(router.urls)),
    path('change_status/<int:order_id>/', views.change_status, name='change_status'),
]
