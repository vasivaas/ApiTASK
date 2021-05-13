from pathlib import Path
from datetime import datetime, timedelta
from django.contrib import auth
from django.http import HttpResponse

import jwt
import socketio
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated

from config import settings
from users.models import User
from users.serializers import UserSerializer, LoginSerializer
from users.permissions import IsCurrentOrReadOnly

static_files = {
    '/static': './drf-yasg',
}
async_mode = None
basedir = Path(__file__).resolve().parent
sio = socketio.Server(async_mode='eventlet', static_files=static_files)


def index(_request):
    return HttpResponse(open(basedir.joinpath('static/index.html')))


@sio.event
def connect(sid, environ):
    print("connect ", sid)


@sio.on('message')
def print_message(sid, message):
    print("Socket ID: ", sid)
    print(message)
    sio.emit('message', 'Status: OK')


class CreateUserView(GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(GenericAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated, IsCurrentOrReadOnly)

    def get(self, _request, pk):
        user = self._find_user_by_id(pk)
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        user = self._find_user_by_id(pk)
        self.check_object_permissions(request, user)
        serializer = self.get_serializer(user, data=request.data, partial=True)
        sio.emit('message', 'Updated personal info for user - {0}'.format(user.first_name))
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _find_user_by_id(self, pk):
        try:
            return self.get_queryset().get(pk=pk)
        except User.DoesNotExist:
            raise NotFound(detail='User not found')


class AuthenticateView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = auth.authenticate(email=request.data['email'], password=request.data['password'])

        if user is None:
            return Response({'bad_authentication': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

        dt = datetime.now() + timedelta(days=1)
        auth_token = jwt.encode({
            'exp': int(dt.strftime('%s')),
            'email': user.email
        }, settings.JWT_SECRET_KEY, algorithm='HS256')
        data = {'token': auth_token}
        return Response(data, status=status.HTTP_200_OK)
