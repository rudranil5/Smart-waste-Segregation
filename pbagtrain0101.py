import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.utils import class_weight

# Paths
train_dir = r"C:\Desktop\DATASET171C\TRAIN"
val_dir = r"C:\Desktop\DATASET171C\VALIDATE"

# Custom binary label function
def binary_label(folder_name):
    return 1 if folder_name == "BAG" else 0

# Create custom generator with binary labels
def make_generator(directory, shuffle=True):
    all_images = []
    all_labels = []
    classes = sorted(os.listdir(directory))
    
    for cls in classes:
        cls_path = os.path.join(directory, cls)
        if not os.path.isdir(cls_path):
            continue
        label = binary_label(cls)
        for img_name in os.listdir(cls_path):
            all_images.append(os.path.join(cls_path, img_name))
            all_labels.append(label)

    # Convert to numpy
    all_images = np.array(all_images)
    all_labels = np.array(all_labels)

    # Shuffle
    if shuffle:
        idx = np.random.permutation(len(all_images))
        all_images, all_labels = all_images[idx], all_labels[idx]

    return all_images, all_labels

# Preprocessing function
def preprocess_image(path, label):
    img = tf.io.read_file(path)
    img = tf.image.decode_jpeg(img, channels=3)
    img = tf.image.resize(img, (128, 128))
    img = img / 255.0
    return img, label

# Load datasets
train_paths, train_labels = make_generator(train_dir)
val_paths, val_labels = make_generator(val_dir, shuffle=False)

train_ds = tf.data.Dataset.from_tensor_slices((train_paths, train_labels))
train_ds = train_ds.map(preprocess_image).batch(32).prefetch(tf.data.AUTOTUNE)

val_ds = tf.data.Dataset.from_tensor_slices((val_paths, val_labels))
val_ds = val_ds.map(preprocess_image).batch(32).prefetch(tf.data.AUTOTUNE)

# Handle class imbalance (optional)
weights = class_weight.compute_class_weight(
    class_weight='balanced',
    classes=np.unique(train_labels),
    y=train_labels
)
class_weights = {0: weights[0], 1: weights[1]}

# Model
model = tf.keras.Sequential([
    tf.keras.layers.Conv2D(32, (3,3), activation='relu', input_shape=(128,128,3)),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Conv2D(64, (3,3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(1, activation='sigmoid')  # Binary output
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Train
model.fit(train_ds, validation_data=val_ds, epochs=10, class_weight=class_weights)

# Save in correct format
model.save("pbagdetector171.keras")
