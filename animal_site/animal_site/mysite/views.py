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
from django.shortcuts import render
import sys
import shutil
from . import sorting
from django.http import FileResponse
from django.conf import settings
import os
from django.http import HttpResponse, Http404
# Create your views here.
import chardet
from PIL import Image
import exifread
from datetime import datetime
import pandas as pd

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
            with ZipFile(f'.\\.\\{fs.url(name)}', 'r') as myzip:
                # Получаем список файлов в архиве
                file_list = myzip.namelist()

            count_file = len(file_list)

            context = {"wait_time": f"{int(count_file * 0.1) * 1.5} c.",
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

"""def categorize_images(image_folder):
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
"""


def get_datetime(image_path):
    # Получаем метаданные изображения
    with open(image_path, 'rb') as f:
        tags = exifread.process_file(f)

    # Извлекаем дату и время из метаданных
    if 'EXIF DateTimeOriginal' in tags:
        date_str = str(tags['EXIF DateTimeOriginal'])
        # Преобразовываем строку в формат datetime
        date_time = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
        if 4 <= date_time.hour < 16:
            return "День"
        else:
            return "Ночь"
    else:
        return None
def archiveFiles(dirs: dict[str, str], resultDir : str, bakeDir : str = "./dir"):
    if (os.path.exists(bakeDir)):
        shutil.rmtree(bakeDir)
    os.mkdir(bakeDir)
    for k in dirs.keys():
        keyPath = os.path.normpath(os.path.join(bakeDir, k))
        #print(f"Key: {k}\n Path:{keyPath}")
        os.mkdir(keyPath)
        for file in dirs[k]:
            newPath = ""
            data = get_datetime(file)
            if data == None:
                newPath = os.path.normpath(os.path.join(keyPath, os.path.basename(file)))
            else:
                newPath = os.path.normpath(os.path.join(keyPath, data))
                if not os.path.exists(newPath):
                    os.mkdir(newPath)
                newPath = os.path.normpath(os.path.join(newPath, os.path.basename(file)))
            #print(f"copy {file} to {newPath }")
            shutil.copy(file, newPath)
    shutil.make_archive(resultDir, 'zip', bakeDir)
    shutil.rmtree(bakeDir)

def clear_file_media():
    folder_path = '.\\.\\media\\'

    # Удаление содержимого папки
    try:
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if 'res_zip' in file_path or 'xlsx' in file_path:
                continue
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        #print(f"Содержимое папки {folder_path} успешно удалено.")
    except Exception as e:
        print(f"Произошла ошибка при удалении содержимого папки {folder_path}: {e}")

def detect_encoding(data):
    result = chardet.detect(data)
    return result['encoding']
def result(request):
    #global file_names_glob, zip_path_glob
    context = {}
    time.sleep(3)
    #file_names = request.GET.get("file_name")
    zip_path = request.GET.get("zip_path")
    #file_names = file_names_glob
    #print(zip_path_glob)
    #zip_path = zip_path_glob
    file_paths = []

    with ZipFile(zip_path, "r") as myzip:
        for item in myzip.namelist():
            file_paths.append(item)

    with ZipFile(zip_path, 'r') as myzip:
        for file_info in myzip.infolist():
            # Получаем имя файла в байтовом формате из архива
            file_name_bytes = file_info.filename.encode('cp437', errors='replace')

            # Определяем кодировку файла
            file_encoding = detect_encoding(file_name_bytes)
            #print(file_encoding)
            # Декодируем байтовую строку в Unicode
            file_name = file_name_bytes.decode("IBM866", errors='replace')

            # Полный путь к файлу после извлечения
            file_path = os.path.join('.\\.\\media\\', file_name)

            # Извлекаем файл
            with open(file_path, 'wb') as file:
                file.write(myzip.read(file_info))
        #myzip.extractall(".\\.\\media\\")
    #categorize_images('.\\.\\media\\')
    res = sorting.sort_files('.\\.\\media\\')
    #print(res)

    archiveFiles(res[0], ".\\.\\media\\res_zip")
    #df = pd.DataFrame(columns=['filename', 'broken', 'empty', 'animal'])

    d = {}
    d['filename'] = []
    d['broken'] = []
    d['empty'] = []
    d['animal'] = []

    for k, v in res[0].items():
        if k == 'animals':
            for el in v:
                d['filename'].append(el)
                d['broken'].append(0)
                d['empty'].append(0)
                d['animal'].append(1)
        if k == 'broken':
            for el in v:
                d['filename'].append(el)
                d['broken'].append(1)
                d['empty'].append(0)
                d['animal'].append(0)
        if k == 'empty':
            for el in v:
                d['filename'].append(el)
                d['broken'].append(0)
                d['empty'].append(1)
                d['animal'].append(0)

    df = pd.DataFrame(d)
    df.to_excel('.\\.\\media\\submission.xlsx', index=False)

    clear_file_media()
    return render(request, 'mysite/result.html', context)


def download_zip(request):
    file_path = os.path.join(settings.MEDIA_ROOT, 'res_zip.zip')
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.zip")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404

def download_excel(request):
    file_path = os.path.join(settings.MEDIA_ROOT, 'submission.xlsx')
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.xlsx")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404