#Processes wrist photograph with extraction of skin color and vein color

import sqlite3 #stores wrist analysis result
import cv2 # OpenCV used for image reading. Converts color between formats and uses pixel mask
import numpy as np #Pixel array operations , averaging
import os #File path
from datetime import datetime  #Timestamp
import database





class WristColorAnalyzer:
    #Encapsulating OOP with image processing in a class
    #Separate from main module
    #from color_analyzer import WristColorAnalyzer
    ALLOWED_FORMATS=["jpg", "jpeg", "png"]

    def __init__(self,image_path, db_name=None): #Emptly in the start
        self.image_path = image_path
        self.db_name = db_name or database.DATABASE_NAME
        self.image = None #Function load_image() puts it
        self.skin_color=None #array from numpy [R, G, B]
        self.skin_description=None
        self.skin_type=None
        self.vein_color=None
        self.undertone=None

        self.create_database() #Initializes table

    def create_database(self): 
        conn=sqlite3.connect(self.db_name)
        cursor=conn.cursor()

        cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS wrist_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_name TEXT,
            skin_rgb TEXT,
            skin_hex TEXT,
            skin_type TEXT,
            skin_description TEXT,
            vein_type TEXT,
            undertone TEXT,
            date_time TEXT
            )
        
        """)

        conn.commit()
        conn.close()
    
    def validate_image(self): #Checkes file 
        if not os.path.exists(self.image_path):
            raise  FileNotFoundError("Image is not found.") #Errors if failed
        filetype=self.image_path.split(".")[-1].lower() #Extracts the format only with formating 
        if filetype not in self.ALLOWED_FORMATS:
            raise ValueError("Invalid format of picture. File format" + filetype + "is not supported. Upload in jpg, jpeg or png.")

    def load_image(self): # Reads images with numpy array and cv2
        self.image = cv2.imread(self.image_path) #Loads in BGR (Blue, Gree , Red) channes which later will be converted to RGB
        if self.image is None:
            raise ValueError("Could not read image, please try again")
        if self.image.shape[2]==4:
            self.image=cv2.cvtColor(self.image,cv2.COLOR_BGRA2BGR) #Converts 4 channels (alpha) to 4 if needed
        
    def get_center_region(self): #Proportional crop of the image to have only wrist image
        h, w = self.image.shape[:2] #Slices heigjt and width
        size=int(min(h,w)*0.6) #Only 60% of the shortest side to have enough pixels
        cy,cx=h//2,w//2 # Center coordinates. // divides integers to whole numebers 
        return self.image[
            cy-size//2 : cy+size//2, # Array slicing with NumPy extracting rectangular region 
            cx-size//2 : cx+size//2          
        ]
    
    def analyze(self):
        self.validate_image() #Validates image
        self.load_image()
        if min(self.image.shape[:2])<40: #Size of image check
            raise ValueError("Image is too small, please choose a larger wrist image")
        center=self.get_center_region()
        brightness=np.mean(center) #Checks mean brightness
        if brightness<40:
            raise ValueError("Image is too dark for proper analysis, try to retake the photo in natural light.")
        if brightness> 220:
            raise ValueError("Image is too bright, take a picture with lower exposure or different lighing.")
        blurred=cv2.GaussianBlur(center,(3,3),0) #Applies blur to make it even 
        hsv=cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV) #Converts BGR to HSV (Hue, Saturation, Value) which is easier for skin detection
        mask_low = cv2.inRange(hsv,np.array([0,15,50]),np.array([30,255,255])) #Red hues - Skin pixel mask with the max and min treshholds. Excludes gray pixels, excludes dar pixels
        #Red repeats twice on the Hue 0-180 with 0-30 and 170-180. 
        mask_high = cv2.inRange(hsv, np.array([170,15,50]), np.array([180,255,255])) #Same but the top Red values 
        skin_mask = cv2.bitwise_or(mask_low, mask_high) #Combines both red masks 
        skin_pixels=center[skin_mask>0]  #Only where masks are white
        if len(skin_pixels) == 0 :
            raise ValueError("No skin was detected on your image. Use image where wrist is shown in the center, and visible clearly")
        if len(skin_pixels)<500:
            raise ValueError("Not enough skin area was detected on your image, reupload with wrist in the center closely to camera.")
        skin_rgb=np.mean(
            cv2.cvtColor(skin_pixels.reshape(-1,1,3), cv2.COLOR_BGR2RGB),
            axis=0
        )#Mean skin color , reformats pixel array to 3d chape with reshape , converts BGR to RGO for hex code output.
        #Averages all pixels and converts float average to integers 
        self.skin_color = skin_rgb.astype(int)[0]
        r,g,b=self.skin_color
        #Uses RGB to determine skin description
        if r>g and r>b:
            self.skin_description="pink/red hue ---- cool type"
        elif g>r and g>b:
            self.skin_description="yellow/olive hue ----- warm type"
        elif b>r and b>g:
            self.skin_description="bluish hue ---- cool type"
        else:
            self.skin_description="neutral"
    #Uses formula called ITU-R BT.601 luma which can calculate brightness from our eyes
    #Shows our vision of colors
        brightness=(0.299*r+0.587*g+0.114*b)
        if brightness>180:
            self.skin_type="Ivory skin"
        elif brightness>130:
            self.skin_type="Fair skin"
        else:
            self.skin_type="Olive skin"

# Detects vein colors, with separating HSV to detect blue, green and purple hues
#Veins are very faint and hat to see , having low saturation (S)
# Blue is 90-140
#Green is 35-85
#Purple is 140-165
        lower_blue=np.array([90,10,20])
        upper_blue=np.array([140,255,255])
        blue_mask=cv2.inRange(hsv,lower_blue,upper_blue) 
        lower_green=np.array([35,10,20])
        upper_green=np.array([85,255,255])
        green_mask=cv2.inRange(hsv,lower_green,upper_green)
        lower_purple=np.array([140,10,20])
        upper_purple=np.array([165, 255, 255])
        purple_mask= cv2.inRange(hsv,lower_purple,upper_purple)
        blue_count=np.sum(blue_mask>0) #This counts white pixels detected
        green_count=np.sum(green_mask>0)
        purple_count=np.sum(purple_mask>0)

# Defines vein color with small treshhold of 20% more than other colors
        if (blue_count+purple_count)> green_count*1.2:
            self.vein_color="Blue/Purple"
            vein_indicator="cool"
        elif green_count>(blue_count+purple_count)*1.2:
            self.vein_color="Green"
            vein_indicator="warm"
        else:
            self.vein_color="Mixed"
            vein_indicator="neutral"
        #Combines skin and vein outputs for single for the undertone classification
        if "cool" in self.skin_description:
            skin_indicator="cool"
        elif "warm" in self.skin_description:
            skin_indicator="warm"
        else:
            skin_indicator="neutral"
        
        if vein_indicator=="cool" and skin_indicator=="cool":
            self.undertone="Cool"
        elif vein_indicator=="warm" and skin_indicator=="warm":
            self.undertone="Warm"
        else:
            self.undertone="Neutral"

    def save_to_database(self):
        #Saves data from analusos on the new row , the query of (?) parameters pastes as tuple 
        conn=sqlite3.connect(self.db_name)
        cursor=conn.cursor()
        skin_hex='#{:02x}{:02x}{:02x}'.format(*self.skin_color) # converts range of RGB to hex value with 2 digits
        cursor.execute("""INSERT INTO wrist_analysis
            (image_name, skin_rgb, skin_hex, skin_type, skin_description, vein_type, undertone, date_time)
            VALUES (?, ?, ?, ?, ?, ?,?,?)
        """,(
            os.path.basename(self.image_path),
            str(self.skin_color.tolist()), #RGB is becoming a string separately. 
            skin_hex,
            self.skin_type,
            self.skin_description,
            self.vein_color,
            self.undertone,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        conn.close()

    def get_results(self): #Returns analysis in Pythin dicitionary
        return{
            "skin_rgb": self.skin_color.tolist(), #Converts the NumpY array to python list 
            "skin_hex": '#{:02x}{:02x}{:02x}'.format(*self.skin_color),
            "skin_type": self.skin_type,
            "skin_description": self.skin_description,
            "vein_color": self.vein_color,
            "undertone": self.undertone
        }

    def get_all_records(self): #Retrieves rows from table of wrist analysis
        conn=sqlite3.connect(self.db_name)
        cursor=conn.cursor()
        cursor.execute("SELECT * FROM wrist_analysis")
        data=cursor.fetchall() #Returns a list of tupeles 
        conn.close()
        return data

        
    #records = WristColorAnalyzer.get_all_records()

    
    def run_analysis(self): #Called in main.py to start analsis
            self.analyze()
            self.save_to_database()
            return self.get_results()
