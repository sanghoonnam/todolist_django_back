from inspect import trace
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import generics, serializers, status, views, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import SignUpSerializer, LogInSerializer, LogOutSerializer
from django.conf import settings
from rest_framework.response import Response


class SignUpView(generics.GenericAPIView):
    authentication_classes = []
    serializer_class = SignUpSerializer
    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception = True)
        serializer.save()
        data = { "msg": "user created" }
        return Response(data, status=status.HTTP_201_CREATED)

class LogInView(generics.GenericAPIView):
    authentication_classes = []
    serializer_class = LogInSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception = True)
        access_token = serializer.data["tokens"]["access"]
        refresh_token = serializer.data["tokens"]["refresh"]
        data = { "msg" : "login success", "username": serializer.data["username"] }
        res = Response(data, status=status.HTTP_200_OK)
        res.set_cookie('access_token', value=access_token, httponly=True)
        res.set_cookie('refresh_token', value=refresh_token, httponly=True)
        return res

class LogOutView(generics.GenericAPIView):
    serializer_class = LogOutSerializer
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        refresh_token = { "refresh" : request.COOKIES.get(settings.SIMPLE_JWT['REFRESH_TOKEN'])}
        serializer = self.serializer_class(data = refresh_token)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = { "msg": "logout success" }
        res = Response(data, status=status.HTTP_200_OK)
        res.delete_cookie('access_token')
        res.delete_cookie('refresh_token')
        return res