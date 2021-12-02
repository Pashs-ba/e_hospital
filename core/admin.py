from django.contrib import admin
from .models import Patient, Mutations

# Register your models here.
admin.site.register(Patient)
admin.site.register(Mutations)