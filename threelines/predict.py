import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras.models import load_model

def load_image(image_path, image_size=(100, 100)):
    img = Image.open(image_path)
    img = img.resize(image_size)
    img_array = np.array(img)
    img_array = img_array / 255.0  # Normalizar la imagen
    img_array = np.expand_dims(img_array, axis=0)  # Añadir una dimensión para el batch
    return img_array

def predict_image(model, image_array):
    prediction = model.predict(image_array)
    predicted_class = np.argmax(prediction, axis=1)[0]
    return predicted_class

if __name__ == "__main__":
    # Cargar el modelo entrenado
    model = load_model('line_detection_model.h5')
    
    # Ruta de la imagen que deseas predecir
    image_path = 'imagen.png'
    
    # Cargar y preprocesar la imagen
    image_array = load_image(image_path)
    
    # Hacer la predicción
    predicted_lines = predict_image(model, image_array)
    
    print(f"La imagen contiene {predicted_lines} línea(s).")
