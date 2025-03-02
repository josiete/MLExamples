import random
from PIL import Image, ImageDraw

def create_image_with_lines(image_size=(100, 100), max_lines=3):
    # Crear una imagen con fondo blanco
    img = Image.new('RGB', image_size, 'white')
    draw = ImageDraw.Draw(img)
    
    # Generar un número aleatorio de líneas (entre 1 y max_lines)
    num_lines = random.randint(1, max_lines)
    
    for _ in range(num_lines):
        # Generar puntos aleatorios para cada línea
        start_point = (random.randint(0, image_size[0]), random.randint(0, image_size[1]))
        end_point = (random.randint(0, image_size[0]), random.randint(0, image_size[1]))
        
        # Dibujar la línea en la imagen
        draw.line([start_point, end_point], fill='black', width=2)
    
    return img, num_lines

def generate_dataset(num_images, image_size=(100, 100), max_lines=3):
    images = []
    labels = []
    
    for _ in range(num_images):
        img, num_lines = create_image_with_lines(image_size, max_lines)
        images.append(img)
        labels.append(num_lines)
    
    return images, labels

def save_images(images, labels, output_dir='dataset'):
    import os
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for i, (img, label) in enumerate(zip(images, labels)):
        img_filename = f"{output_dir}/image_{i+1}_lines_{label}.png"
        img.save(img_filename)

if __name__ == "__main__":
    num_images = 5  # Número de imágenes a generar
    images, labels = generate_dataset(num_images)
    save_images(images, labels)
