from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
from django.shortcuts import render
from rest_framework.views import APIView
from .models import Keys, Locks, AuthUser, KeyLockPermissions
from .serializers import KeySerializer
from .serializers import PhoneRequestSerializer, CardRequestSerializer
from rest_framework.response import Response
from rest_framework import status, permissions
import json




class MobileLockAccessView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # requires JWT-authenticated user

    def post(self, request):
        serializer = PhoneRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        lock_id = serializer.validated_data['lock_id']
        auth_user = AuthUser.objects.get(username=request.user.username)

        # Check if this user has ANY key that can open this lock
        has_access = KeyLockPermissions.objects.filter(
            key__assigned_user=auth_user,
            lock__lock_id=lock_id
        ).exists()

        try:
            lock = Locks.objects.get(lock_id=lock_id)
        except Locks.DoesNotExist:
            # No such key → no access
            return Response(
                {
                    "lock_id": lock_id,
                    "has_access": False,
                    "reason": "Invalid Lock ID",
                },
                status=status.HTTP_200_OK,
            )


        lock_status = lock.status

        print(lock_status)

        if(has_access):
            lock_status = not lock_status

        lock.status = lock_status
        lock.save()


        return Response(
            {
                "lock_id": lock_id,
                "user_id": auth_user.id,
                "lock_status": lock_status,
            },
            status=status.HTTP_200_OK,
        )

class CardLockAccessView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = CardRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        lock_id = serializer.validated_data['lock_id']
        uid = serializer.validated_data['uid']

        try:
            key = Keys.objects.get(credential=uid)
        except Keys.DoesNotExist:
            # No such key → no access
            return Response(
                {
                    "lock_id": lock_id,
                    "has_access": False,
                    "reason": "Invalid code",
                },
                status=status.HTTP_200_OK,
            )

        try:
            lock = Locks.objects.get(lock_id=lock_id)
        except Locks.DoesNotExist:
            # No such key → no access
            return Response(
                {
                    "lock_id": lock_id,
                    "has_access": False,
                    "reason": "Invalid Lock ID",
                },
                status=status.HTTP_200_OK,
            )

        # Check if this user has ANY key that can open this lock
        has_access = KeyLockPermissions.objects.filter(
            key__credential=uid,
            lock__lock_id=lock_id
        ).exists()

        lock_status = lock.status

        if(has_access):
            lock_status = not lock_status

        lock.status = lock_status
        lock.save()

        return Response(
            {
                "lock_id": lock_id,
                "status": lock_status,
            },
            status=status.HTTP_200_OK,
        )



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
