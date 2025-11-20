from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
from django.shortcuts import render
from .models import Keys
from .serializers import KeySerializer
from rest_framework.response import Response
from rest_framework import status
import json

latest_card_id = None  # global store

@api_view(['GET'])
def get_keys(request):
    keys = Keys.objects.all()
    serializer = KeySerializer(keys, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_key(request):
    serializer = KeySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Repesponse(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def latest_card(request):
    global latest_card_id
    return JsonResponse({"card_id": latest_card_id})

def index(request):
    global latest_card_id
    return render(request, "index.html", {"card_id": latest_card_id})

def return_card_id(request):
    global latest_card_id
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        card_id = data.get("card_id")
        if card_id:
            latest_card_id = card_id
            print(f"Received card_id: {card_id}")
            return JsonResponse({"status": "success", "card_id": card_id})
        else:
            return JsonResponse({"status": "error", "message": "No card_id provided"}, status=400)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)
