from django.urls import path, include
from rest_framework.routers import DefaultRouter
# 1. 必须导入 bind_identity 和 review_oa 以及 ViewSet
from .views import CustomAuthToken, RegisterView, TicketViewSet, OAViewSet, bind_identity, review_oa

# 2. 注册自动路由 (Ticket 和 OA)
router = DefaultRouter()
router.register(r'tickets', TicketViewSet, basename='ticket')
router.register(r'oa', OAViewSet, basename='oa')

urlpatterns = [
    path('login/', CustomAuthToken.as_view(), name='api_login'),
    path('register/', RegisterView.as_view(), name='api_register'),

    path('bind-identity/', bind_identity, name='api_bind_identity'),

    path('oa/<int:pk>/review/', review_oa, name='api_oa_review'),

    path('', include(router.urls)),
]