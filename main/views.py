from django.shortcuts import render
from django.http import HttpResponse



def index(request):
    context = {
        'title': "home",
        'content': 'Main page',
        }

    return render(request, 'main/index.html', context )


def contacts(request):
    return HttpResponse('contacts page')
