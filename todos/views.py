from django.shortcuts import render
import json
# Create your views here.
from django.views.generic import View
from .models import Todo
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import generics, serializers, status, views, permissions, mixins, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from todos.serializers import TodoSerializer

def todo_instance_to_dictionary(todo):
  """
  장고 단일 모델 인스턴스, 혹은 쿼리셋을 파이썬 딕셔너리로 변환하는 헬퍼 함수
  """
  result = {}
  result["id"] = todo.id
  result["text"] = todo.text
  result["done"] = todo.done
  return result


class TodoListView(APIView):
  permission_classes = [permissions.IsAuthenticated]
  def get(self, request):
    serializer = TodoSerializer(Todo.objects.filter(author=request.user), many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
  def post(self, request):
    serializer = TodoSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save(author=request.user)
      return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class TodoCheckView(APIView):
  permission_classes = [permissions.IsAuthenticated]
  def patch(self, request, id):
    try:
      todo_instance = Todo.objects.get(id=id)
      if (todo_instance.author_id != request.user.id):
        return JsonResponse({"msg": "Cannot access other's todo"}, status=401)
      todo_instance.check_todo()
      todo_dict = todo_instance_to_dictionary(todo_instance)
      data = { "todo": todo_dict }
      return JsonResponse(data, status=200)
    except:
      return JsonResponse({"msg": "Failed to create todos"}, status=404)


class TodoView(APIView):
  permission_classes = [permissions.IsAuthenticated]
  def get(self, request, id):
    try:
      todo_instance = Todo.objects.get(id=id)
      if (todo_instance.author.id != request.user.id):
        return JsonResponse({"msg": "Cannot access other's todo"}, status=401)
      todo_dict = todo_instance_to_dictionary(todo_instance)
      data = { "todo": todo_dict }
      return JsonResponse(data, status=200)
    except:
      return JsonResponse({"msg": "Failed to get todo"}, status=404)
  
  def delete(self, request, id):
    try:
      todo_instance = Todo.objects.get(id=id)
      if (todo_instance.author.id != request.user.id):
        return JsonResponse({"msg": "Cannot access other's todo"}, status=401)
      todo_dict = todo_instance_to_dictionary(todo_instance)
      todo_instance.delete()
      data = { "todo": todo_dict }
      return JsonResponse(data, status=200)
    except:
      return JsonResponse({"msg": "Failed to delete todo"}, status=404)
  
  def patch(self, request, id):
    try:
      body = json.loads(request.body)
      todo_instance = Todo.objects.get(id=id)
      if (todo_instance.author.id != request.user.id):
        return JsonResponse({"msg": "Cannot access other's todo"}, status=401)
      todo_instance.change_todo(body["text"])
      todo_dict = todo_instance_to_dictionary(todo_instance)
      data={"todo":todo_dict}
      return JsonResponse(data, status=200)
    except:
      return JsonResponse({"msg": "Failed to patch todo"}, status=404)