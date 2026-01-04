import random
import classificationTest0101
import tensorflow as tf
import numpy as np
import os
from tensorflow.keras.preprocessing import image

def loadModel():
    # Load the trained model
    bagmodelpath = tf.keras.models.load_model(r"F:\PYTHON\pbagdetector171.keras")

    return bagmodelpath

def testbag(img_path,bagmodelpath=tf.keras.models.load_model(r"F:\PYTHON\pbagdetector171.keras"),moisture=500):

    # Preprocess the image
    if not os.path.isfile(img_path):
        raise ValueError("No Image Recieved\t- pbagtest failed!!!")
    img = image.load_img(img_path, target_size=(128, 128))
    img_array = image.img_to_array(img)
    img_array = img_array / 255.0
    img_array = np.expand_dims(img_array, axis=0)  # Shape: (1, 128, 128, 3)

    # Predict
    prediction = bagmodelpath.predict(img_array)[0][0]
    
    #result
    class_name = "BAG" if prediction >= 0.5 else "NON-BAG"     
    confidence = round(float(prediction), 4) if prediction >= 0.5 else round(1 - float(prediction), 4)
    print(f"Prediction: {class_name} (confidence: {confidence})")
    details=[class_name,confidence] #to return and store
    if class_name=="BAG":       #next stage
        moisture=random.randint(0,1000)
        details.append(moisture) #3rd element
        threshold=600
        if moisture > threshold:
            #arduino.write(b'DRY\n')
            detection=f"Non-Recyclable  moisture - {moisture}"
            print(detection)
            details.append("Non-Recyclable")
            return details
        else:
            #arduino.write(b'OK\n')
            detection=f"Recyclable moisture- {moisture}"
            print(detection)
            details.append("Recyclable")
            return details
    else :
        details.append(0)
        return details

if __name__=="__main__":
    # Image path to test
    img_path = r"C:\Desktop\DATASET171C\TRAIN\METAL\metal42.jpg" #  Replace this with your image path
    #img_path=None
    res=testbag(img_path,loadModel())
    if res[-1]==0:
        #THE CLASSIFICATION MODEL PATH typeMODEL_PATH = r"E:\DATASET_Trash_sbh_readwrite_ard\garbage-detector\models\final_model_new.keras"
        a=classificationTest0101.loadModel()
        detection=classificationTest0101.predict_single_image(a,img_path,(224, 224))
        print(detection)
    
    



