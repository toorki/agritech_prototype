from django.http import HttpResponse

def index(request) :
    """Home page for the main project"""
    return HttpResponse("Welcome to AgriTech")