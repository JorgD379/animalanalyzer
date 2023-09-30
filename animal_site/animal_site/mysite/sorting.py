import os
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import tensorflow.keras.applications.inception_v3 as inception
import tensorflow.keras.applications.resnet50 as resnet

import numpy as np

#прописать норм пути к моделям

model_path = './mysite/animal_classification_model_major_try.h5'

RN_model = tf.keras.models.load_model(model_path)

def classify_image(image_path, model):
    img = image.load_img(image_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = resnet.preprocess_input(img_array)

    predictions = model.predict(img_array)

    score = predictions
    return score

def sort_files(folder_path):
    result = {"animals": [], "broken": [], "empty": []}
    error_counter = 0
    for filename in os.listdir(folder_path):
        if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png")or filename.endswith(".JPG"):
            try:
                image_path = os.path.join(folder_path, filename)
                predictions = classify_image(image_path, RN_model)
                predicted_class = list(result.keys())[np.argmax(predictions)]
                result[predicted_class].append(image_path)

            except Exception as e:
                #print(e.args)
                error_counter += 1

    return result, error_counter