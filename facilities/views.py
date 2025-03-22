from django.shortcuts import render
from django.http import HttpResponse


def clinics_catalog(request):
    return render (request, "facilities/clinics_catalog.html")

def clinic_detail(request):
    return render (request, "facilities/clinic_detail.html")



# Create your views here.
