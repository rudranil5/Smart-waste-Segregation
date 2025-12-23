def testbag(img_path):
    
    import random
    import test
    import tensorflow as tf
    import numpy as np
    from tensorflow.keras.preprocessing import image

    # Load the trained model
    bagmodelpath = tf.keras.models.load_model(r"F:\PYTHON\pbagdetector171.keras")

    # Image path to test
    #img_path = r"C:\Desktop\DATASET171C\TRAIN\METAL\metal42.jpg" #  Replace this with your image path

    typeMODEL_PATH = r"E:\DATASET_Trash_sbh_readwrite_ard\garbage-detector\models\final_model_new.keras"
    # Preprocess the image
    img = image.load_img(img_path, target_size=(128, 128))
    img_array = image.img_to_array(img)
    img_array = img_array / 255.0
    img_array = np.expand_dims(img_array, axis=0)  # Shape: (1, 128, 128, 3)

    # Predict
    prediction = bagmodelpath.predict(img_array)[0][0]

    # Output result
    class_name = "BAG" if prediction >= 0.5 else "NON-BAG"

        
        
    confidence = round(float(prediction), 4) if prediction >= 0.5 else round(1 - float(prediction), 4)

    print(f"Prediction: {class_name} (confidence: {confidence})")

    if class_name=="BAG":
        moisture=random.randint(0,1000)
        threshold=600
        if moisture > threshold:
            #arduino.write(b'DRY\n')
            detection=f"Sent: Non recyclable  moisture - {moisture}"
            print(detection)
        else:
            #arduino.write(b'OK\n')
            detection=f"Recyclable moisture- {moisture}"
            print(detection)
    else :
        detection=test.predict_single_image(typeMODEL_PATH,img_path, (224, 224))
    return detection
if __name__=="__main__":
    pass



