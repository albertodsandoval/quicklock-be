from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the embedded index.")

def return_card_id(request):
    if request.method == 'POST':
        return HttpResponse(request.POST.get('card_id'))