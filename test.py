import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import pandas as pd

#print(numpy.__file__)

# Class mapping used during training
CLASS_MAPPING = {
    'cardboard': 1,  # Recyclable
    'glass': 1,      # Recyclable
    'metal': 1,      # Recyclable
    'paper': 1,      # Recyclable
    'plastic': 0,    # Non-recyclable
    'trash': 0       # Non-recyclable
}

# Specify paths here
MODEL_PATH = r'D:\DATASET_Trash_sbh_readwrite_ard\garbage-detector\models\final_model_new.keras'  # Path to your trained model
IMAGE_PATH = r'D:\DATASET_Trash_sbh_readwrite_ard\garbage-detector\received_image.jpg'  # Path to the image for prediction
DATA_DIR = r'D:\DATASET_Trash_sbh\garbage-detector\data\dataset'  # Path to the dataset for evaluation
BATCH_SIZE = 16
IMAGE_SIZE = 224  # Updated image size to match the model input


import socket

def server_side():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('192.168.113.112', 12346))
    server_socket.listen(1)
    print("Server listening...")

    conn, addr = server_socket.accept()
    print(f"Connected by {addr}")

    with open("received_image.jpg", "wb") as f:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            f.write(data)
            
            print("Image received and saved.")

            #print("Image received and saved.")
            IMAGE_PATH = "received_image.jpg"
            #proccess the image now
            the_prediction=predict_single_image(MODEL_PATH, IMAGE_PATH, (IMAGE_SIZE, IMAGE_SIZE))

            # Evaluate model with dataset
            evaluate_model(MODEL_PATH, DATA_DIR, BATCH_SIZE, (IMAGE_SIZE, IMAGE_SIZE))
            conn.sendall(the_prediction)

            time.sleep(20)
    



def preprocess_image(img_path, image_size):
    """Preprocess a single image for prediction."""
    img = image.load_img(img_path, target_size=image_size)
    img_array = image.img_to_array(img)
    img_array = tf.keras.applications.resnet50.preprocess_input(img_array)
    return np.expand_dims(img_array, axis=0), img

import serial
import time

def predict_single_image(model_path, img_path, image_size):
    """Predict class of a single image, display it, and send result to Arduino."""
    model = load_model(model_path)
    img_tensor, original_img = preprocess_image(img_path, image_size)
    prediction = model.predict(img_tensor)[0][0]
    label = int(prediction > 0.5)
    class_name = 'Recyclable' if label == 1 else 'Non-Recyclable'
    the_prediction=(f"\nPrediction: {class_name} ({prediction:.4f} confidence)")
    print(the_prediction)
    '''
    # Send to Arduino
    try:
        arduino = serial.Serial('COM5', 9600, timeout=1)
        time.sleep(2)  # Let Arduino initialize
        arduino.write(str(label).encode())
        print(f"Sent to Arduino: {label}")
        
        while True:
            if arduino.in_waiting > 0:
                line = arduino.readline().decode('utf-8').strip()
                if line:
                    print(f"Arduino : {line}")

        # Optional: send a test signal
        # arduino.write(b'1')
        # time.sleep(1)

    except KeyboardInterrupt:
        print("Stopped listening.")
    finally:
        arduino.close()
   # except serial.SerialException as e:
    #    print(f"Failed to send to Arduino: {e}")
    '''
    # Optional: plot image
    plt.figure(figsize=(6, 6))
    plt.imshow(original_img)
    plt.title(f"Prediction: {class_name} ({prediction:.2%})", fontsize=14)
    plt.axis('off')
    plt.tight_layout()
    plt.show()
    return (the_prediction)

def load_data(data_dir):
    """Load image paths and labels for evaluation."""
    image_paths = []
    labels = []
    
    for class_name, label in CLASS_MAPPING.items():
        class_dir = os.path.join(data_dir, class_name)
        if not os.path.exists(class_dir):
            raise FileNotFoundError(f"Missing directory: {class_dir}")
        
        for image_name in os.listdir(class_dir):
            image_path = os.path.join(class_dir, image_name)
            if image_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_paths.append(image_path)
                labels.append(label)

    return pd.DataFrame({'filename': image_paths, 'label': labels})

def create_generator(df, batch_size, image_size):
    """Create a data generator for test evaluation."""
    datagen = ImageDataGenerator(
        preprocessing_function=tf.keras.applications.resnet50.preprocess_input
    )

    generator = datagen.flow_from_dataframe(
        dataframe=df,
        x_col='filename',
        y_col='label',
        target_size=image_size,
        batch_size=batch_size,
        class_mode='raw',
        shuffle=False
    )
    return generator

def evaluate_model(model_path, data_dir, batch_size, image_size):
    """Evaluate the model on the dataset and generate classification metrics."""
    print("Loading data...")
    df = load_data(data_dir)
    _, test_df = train_test_split(df, test_size=0.2, stratify=df['label'], random_state=42)

    print("Creating test generator...")
    test_gen = create_generator(test_df, batch_size, image_size)

    print(f"Loading model from {model_path}...")
    model = load_model(model_path)

    print("Predicting...")
    predictions = model.predict(test_gen, verbose=1)
    predicted_labels = (predictions > 0.5).astype(int).flatten()

    print("\nClassification Report:")
    print(classification_report(test_df['label'], predicted_labels, target_names=['Non-Recyclable', 'Recyclable']))

    cm = confusion_matrix(test_df['label'], predicted_labels)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Non-Recyclable', 'Recyclable'], yticklabels=['Non-Recyclable', 'Recyclable'])
    plt.title('Confusion Matrix')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.tight_layout()
    plt.savefig('confusion_matrix.png')
    plt.close()

    print("Confusion matrix saved as 'confusion_matrix.png'.")

# Run prediction or evaluation
if __name__ == '__main__':

    #server recieves
    server_side()
    # Predict a single image
   # predict_single_image(MODEL_PATH, IMAGE_PATH, (IMAGE_SIZE, IMAGE_SIZE))

    # Evaluate model with dataset
    #evaluate_model(MODEL_PATH, DATA_DIR, BATCH_SIZE, (IMAGE_SIZE, IMAGE_SIZE))