import os
import schedule
import time
import cv2
import numpy as np
from database import Database  # Make sure to have database.py in the same directory
from dotenv import load_dotenv
import requests
from database import Database

load_dotenv()
db_url = os.getenv("supabaseURL")
if db_url is None:
    raise ValueError("Database URL not found. Check your environment variables.")
db = Database(os.getenv("supabaseURL"))
db.create_table()

def capture_image():
    save_path = "/home/krantlee/515 FarmDetector/Saved_images_test1"
    os.makedirs(save_path, exist_ok=True)
    filename = os.path.join(save_path, time.strftime("%Y%m%d-%H%M%S") + ".jpg")
    command = f"libcamera-still -o '{filename}' --autofocus-mode auto --tuning-file /usr/share/libcamera/ipa/rpi/vc4/imx477_af.json"
    print("Executing command:", command)
    os.system(command)

    if os.path.exists(filename) and os.path.isfile(filename):
        print(f"Captured {filename}")
        image = cv2.imread(filename)
        if image is not None:
            count = process_image(image)
            print(f"Processed {filename}: {count} weevils found")
            description = f"Date: {time.strftime('%m/%d/%Y')}\nPest category: Weevil\nNumber: {count}\nAdvice: Call us to get more help"
            upload_image_and_description(filename, description)
        else:
            print(f"Failed to load image {filename}")

def crop_center_square(image):
    height, width = image.shape[:2]
    central_square_side = min(height, width)
    top = (height - central_square_side) // 2
    left = (width - central_square_side) // 2
    cropped_img = image[top:top + central_square_side, left:left + central_square_side]
    cropped_area = central_square_side * central_square_side  # This calculates the area
    '''print(f"The cropped image area is: {cropped_area} pixels")  # This prints the area'''
    return cropped_img


def process_image(image):
    cropped_image = crop_center_square(image)
    gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    min_area = 10000  # Minimum area to be considered a weevil
    max_area = 41400  # Maximum area to be considered a weevil
    weevil_count = 0

    for contour in contours:
        area = cv2.contourArea(contour)
        if min_area < area < max_area:
            weevil_count += 1

    processed_filename = os.path.join("/home/krantlee/515 FarmDetector/Saved_images_test1", "processed_" + time.strftime("%Y%m%d-%H%M%S") + ".jpg")
    cv2.imwrite(processed_filename, thresh)
    return weevil_count

def upload_image_and_description(filename, description):
    # Assume function to upload to Supabase and insert to database
    url = db.upload_file(filename)
    db.insert_record(filename, url, description)

schedule.every(20).seconds.do(capture_image)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)
