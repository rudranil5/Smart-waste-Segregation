import cv2
import numpy as np
import os
import pbagtest0101
import classificationTest0101
def multiControll(bagmodel,classificationmodel):
    count=len(os.listdir(r"C:\Desktop\sbV0101\objects"))
    print(count)
    i=1
    listDec=[]
    while i<=count:
        a=pbagtest0101.testbag(rf"C:\Desktop\sbV0101\objects\object_{i}.jpg",bagmodel)
        
        if a[-1]==0:
            b=classificationTest0101.predict_single_image(classificationmodel,rf"objects\object_{i}.jpg",(224,224))
            listDec.append(b[-1]+1)
        elif a[-1]== "Recyclable" :
            listDec.append(1)
        elif a[-1]=="Non-Recyclable":
            listDec.append(2)
        else :
            os.remove(rf"C:\Desktop\sbV0101\objects\object_{i}.jpg")
            i+=1
            continue
        
        os.remove(rf"C:\Desktop\sbV0101\objects\object_{i}.jpg")
        i+=1
    print(f"The list of descisions is as below\n\n {listDec}")
    probability=1 if listDec.count(1) > listDec.count(2)  else 2


    return probability

def processImg(img_path):
    # -----------------------------
    # Read image
    # -----------------------------
    img = cv2.imread(img_path)
    if img is None:
        raise ValueError("Image not found")

    original = img.copy()

    # -----------------------------
    # Preprocessing (WITH CLAHE)
    # -----------------------------
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # Edge-preserving blur (better than Gaussian for haze)
    blur = cv2.bilateralFilter(gray, 9, 75, 75)

    # Edge detection (adaptive thresholds)
    v = np.median(blur)
    lower = int(max(0, 0.66 * v))
    upper = int(min(255, 1.33 * v))
    edges = cv2.Canny(blur, lower, upper)

    # Strengthen edges
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    # -----------------------------
    # Find contours
    # -----------------------------
    contours, _ = cv2.findContours(
        edges,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    img_area = img.shape[0] * img.shape[1]

    # Create output folder
    os.makedirs("objects", exist_ok=True)

    object_count = 0

    # -----------------------------
    # Process each contour
    # -----------------------------
    for cnt in contours:
        area = cv2.contourArea(cnt)

        # Filter noise and floor
        if 800 < area < 0.5 * img_area:
            object_count += 1

            x, y, w, h = cv2.boundingRect(cnt)

            # Mask-based precise cut-out
            mask = np.zeros(gray.shape, dtype=np.uint8)
            cv2.drawContours(mask, [cnt], -1, 255, -1)

            obj = cv2.bitwise_and(original, original, mask=mask)
            obj_crop = obj[y:y+h, x:x+w]

            # Save object
            cv2.imwrite(f"objects//object_{object_count}.jpg", obj_crop)

            # Draw rectangle
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # -----------------------------
    # Show count on image
    # -----------------------------
    cv2.putText(
        img,
        f"Objects: {object_count}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )
    '''
    # -----------------------------
    # DISPLAY (NO AUTO-ZOOM ISSUE)
    # -----------------------------
    cv2.namedWindow("Edges", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Edges", 1200, 800)

    cv2.namedWindow("Detected Objects", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Detected Objects", 1200, 800)

    cv2.imshow("Edges", edges)
    cv2.imshow("Detected Objects", img)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
    '''

    if len(os.listdir("objects")) > 1:
        print("Total objects detected:", object_count)
        return 1
    else :
        return 0
    
if __name__=="__main__":
    processImg(r"C:\Desktop\sbV0101\received_image.jpg")
    bm=bagmodel=pbagtest0101.loadModel()
    cm=classificationTest0101.loadModel()
    multiControll(bm,cm)
