from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
import json

latest_card_id = None  # global store

@csrf_exempt
def latest_card(request):
    global latest_card_id
    return JsonResponse({"card_id": latest_card_id})

@csrf_exempt
def index(request):
    global latest_card_id
    return render(request, "index.html", {"card_id": latest_card_id})

@csrf_exempt
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
