from PIL import Image
import exifread
from datetime import datetime

def get_datetime(image_path):
    # Получаем метаданные изображения
    with open(image_path, 'rb') as f:
        tags = exifread.process_file(f)

    # Извлекаем дату и время из метаданных
    if 'EXIF DateTimeOriginal' in tags:
        date_str = str(tags['EXIF DateTimeOriginal'])
        # Преобразовываем строку в формат datetime
        date_time = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
        return date_time
    else:
        return None