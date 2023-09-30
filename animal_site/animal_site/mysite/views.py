import io
import time

from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from zipfile import ZipFile
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.inception_v3 import InceptionV3
from tensorflow.keras.applications.inception_v3 import preprocess_input, decode_predictions
import numpy as np
import os
from django.shortcuts import render
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from django.http import HttpResponse

from .forms import DocumentForm


# Create your views here.
def upload_file(request):
    context = {}
    if request.method == 'POST':
        #clear_file_media()
        uploaded_file = request.FILES['document']
        fs = FileSystemStorage()
        name = fs.save(uploaded_file.name, uploaded_file)
        if fs.url(name)[len(fs.url(name)) - 4:] == '.zip':
            print("IT IS ZIP!!!")
            file_names = ""
            with ZipFile(f'.\\.\\{fs.url(name)}', "r") as myzip:
                with open(".\\.\\media\\file_names.txt", "w",
                          encoding="utf-8") as file:
                    for line in myzip.namelist():
                        file.write(line + '\n')

            context = {"file_names": ".\\.\\.\\media\\file_names.txt",
                       "zip_path": f'.\\.\\{fs.url(name)}'}
            return render(request, 'mysite/upload_file.html', context)
        else:
            print("IT IS IMAGE!")
            context['urls'] = fs.url(name)
            # return render(request, 'ml_models/choose_target.html', context)
            return render(request, 'mysite/upload_file.html', context)
    return render(request, 'mysite/upload_file.html', context)


# Загрузка предварительно обученной модели InceptionV3
model = InceptionV3(weights='imagenet')
img_size = (299, 299)
def classify_image(image_path):
    # Загрузка изображения и изменение размера
    img = image.load_img(image_path, target_size=img_size)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    # Получение предсказаний
    predictions = model.predict(img_array)

    # Декодирование и вывод класса с наивысшей вероятностью
    decoded_predictions = decode_predictions(predictions, top=1)[0]
    label = decoded_predictions[0][1]
    score = decoded_predictions[0][2]

    return label, score

def categorize_images(image_folder):
    # Перебор всех файлов в папке с изображениями
    for filename in os.listdir(image_folder):
        if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png"):
            image_path = os.path.join(image_folder, filename)

            # Классификация изображения
            label, score = classify_image(image_path)

            # Пороговое значение для определения качества изображения
            threshold = 0.3

            # Определение качественного или некачественного изображения
            if score > threshold:
                print(f"{filename} - Качественное изображение ({label}, {score})")
                # Здесь можно выполнить дополнительные действия для качественных изображений
            else:
                print(f"{filename} - Некачественное изображение ({label}, {score})")
                # Здесь можно выполнить дополнительные действия для некачественных изображений


def result(request):
    context = {}
    time.sleep(3)
    file_names = request.GET.get("file_name")
    zip_path = request.GET.get("zip_path")
    file_paths = []

    with ZipFile(zip_path, "r") as myzip:
        for item in myzip.namelist():
            file_paths.append(item)

    with ZipFile(zip_path, "r") as myzip:
        myzip.extractall(".\\.\\media\\")
    categorize_images('.\\.\\media\\')
    return render(request, 'mysite/result.html', context)


