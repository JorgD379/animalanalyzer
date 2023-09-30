from django.urls import path
from . import views

urlpatterns = [
    path("", views.upload_file, name="upload_file"),
    path("result", views.result, name="result"),
    path('download-zip/', views.download_zip, name='download_zip'),
    path('download-excel/', views.download_excel, name='download_excel'),
]