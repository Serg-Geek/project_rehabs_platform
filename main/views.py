from django.shortcuts import render
from django.http import HttpResponse



def index(request):
    context = {
        'title': 'Реабилитация зависимых | "Моё море"',
        'content': 'Main page',
        }

    return render(request, 'main/index.html', context )


def contacts(request):
    context = {
        'title': 'Реабилитация зависимых | Контакты',
        
        }

    return render(request, 'main/contacts.html', context )
