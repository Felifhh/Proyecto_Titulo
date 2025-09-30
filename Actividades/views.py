from django.http import HttpResponse

def index(request):
    return HttpResponse("Aquí se mostrarán los certificados")
