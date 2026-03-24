from django.http import HttpResponse


def index(request):
    return HttpResponse("Recommendations module scaffold is ready.")
