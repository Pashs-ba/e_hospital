
from django.urls import path
from .views import homepage, new_patient, queries, patient_page, delete_patient

urlpatterns = [
    path('', homepage, name='homepage'),
    path('create_patient', new_patient, name='new_patient'),
    path('queries', queries, name='queries'),
    path('patient/<int:pk>', patient_page, name='patient_page'),
    path('patient/delete/<int:pk>', delete_patient, name='delete_patient')
]
