from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import generics, viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, action
from django.db.models import Q

from .models import CustomUser, Ticket
from .serializers import UserSerializer, RegisterSerializer, TicketSerializer


# 1. Login View
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserSerializer(user).data})


# 2. Register View
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


# 3. Identity Bind View (Kept to prevent 404s from frontend, though logic is simplified)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bind_identity(request):
    user = request.user
    if user.is_identity_bound:
        return Response({"detail": "您已经绑定过身份，无需重复操作", "user": UserSerializer(user).data}, status=200)

    user.role = request.data.get('role')
    user.identity_id = request.data.get('identity_id')
    user.name = request.data.get('name')
    user.is_identity_bound = True
    user.save()

    return Response({"detail": "Bind successful", "user": UserSerializer(user).data})


# 4. Ticket ViewSet
class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Admins and Repair Admins see all tickets
        if user.role in ['admin', 'repair_admin']:
            return Ticket.objects.all()
        # Maintenance workers see all tickets (simplified logic for internship)
        if user.role == 'maintenance':
            return Ticket.objects.all()
        # Regular users (students/teachers) only see their own tickets
        return Ticket.objects.filter(submitter=user)

    def perform_create(self, serializer):
        # Automatically set status to 'pending_dispatch'
        serializer.save(submitter=self.request.user, status='pending_dispatch')

    # Ticket Handling Action (Assign, Finish, Evaluate)
    @action(detail=True, methods=['post'])
    def handle(self, request, pk=None):
        ticket = self.get_object()
        action_type = request.data.get('type')

        # Dispatch (Assign)
        if action_type == 'assign':
            worker_id = request.data.get('worker_id')
            try:
                worker = CustomUser.objects.get(pk=worker_id)
                ticket.assignee = worker
                ticket.status = 'repairing'
                ticket.save()
                return Response({'status': 'Dispatched'})
            except CustomUser.DoesNotExist:
                return Response({'error': 'Worker not found'}, status=400)

        # Finish Repair
        if action_type == 'finish':
            ticket.status = 'finished'
            ticket.save()
            return Response({'status': 'Repair Finished'})

        # Evaluate
        if action_type == 'evaluate':
            ticket.evaluation = request.data.get('comment')
            ticket.rating = request.data.get('rating', 5)
            ticket.status = 'closed'
            ticket.save()
            return Response({'status': 'Evaluated'})

        return Response({'error': 'Unknown action'}, status=400)