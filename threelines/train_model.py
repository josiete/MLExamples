import os
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras import layers, models

def load_dataset(image_dir='dataset', image_size=(100, 100)):
    images = []
    labels = []

    for filename in os.listdir(image_dir):
        if filename.endswith('.png'):
            img = Image.open(os.path.join(image_dir, filename))
            img = img.resize(image_size)
            img_array = np.array(img)
            images.append(img_array)

            # Extraer el número de líneas del nombre del archivo
            label = int(filename.split('_')[-1].split('.')[0])
            labels.append(label)

    images = np.array(images)
    labels = np.array(labels)
    
    return images, labels

def preprocess_data(images, labels):
    images = images / 255.0  # Normalizar las imágenes
    labels = tf.keras.utils.to_categorical(labels, num_classes=4)  # Convertir etiquetas a one-hot encoding
    return images, labels

def create_model(input_shape):
    model = models.Sequential([
        layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.Flatten(),
        layers.Dense(64, activation='relu'),
        layers.Dense(4, activation='softmax')
    ])
    
    model.compile(optimizer='adam',
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    return model

if __name__ == "__main__":
    image_size = (100, 100)
    images, labels = load_dataset(image_size=image_size)
    images, labels = preprocess_data(images, labels)

    # Dividir el conjunto de datos en entrenamiento y validación
    from sklearn.model_selection import train_test_split
    X_train, X_val, y_train, y_val = train_test_split(images, labels, test_size=0.2, random_state=42)

    model = create_model(input_shape=(image_size[0], image_size[1], 3))
    
    # Entrenar el modelo
    model.fit(X_train, y_train, epochs=10, validation_data=(X_val, y_val))
    
    # Guardar el modelo entrenado
    model.save('line_detection_model.h5')
