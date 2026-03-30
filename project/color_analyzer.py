import sqlite3
import cv2
import numpy as np
import os
from datetime import datetime


class WristColorAnalyzer:
    #from color_analyzer import WristColorAnalyzer
    ALLOWED_FORMATS=["jpg", "jpeg", "png"]

    def __init__(self,image_path, db_name="color_database.db"):
        self.image_path = image_path
        self.db_name = db_name
        self.image = None
        self.skin_color=None
        self.skin_description=None
        self.skin_type=None
        self.vein_color=None
        self.undertone=None

        self.create_database()

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
    
    def validate_image(self):
        if not os.path.exists(self.image_path):
            raise  FileNotFoundError("Image is not found.")
        ext=self.image_path.split(".")[-1].lower()
        if ext not in self.ALLOWED_FORMATS:
            raise ValueError("Invalid format of picture. Use jpg, jpeg or png.")

    def load_image(self):
        self.image = cv2.imread(self.image_path)
        if self.image is None:
            raise ValueError("Could not read image.")
        
    def get_center_region(self, size=200):
        h, w, _ = self.image.shape 
        return self.image[
            h//2 - size//2 : h//2 + size//2,
            w//2 - size//2 : w//2 + size//2          
        ]
    
    def analyze(self):
        self.validate_image()
        self.load_image()
        center=self.get_center_region()
        brightness=np.mean(center)
        if brightness<40:
            raise ValueError("Image is too dark for proper analysis.")
        if brightness> 220:
            raise ValueError("Image is too bright, take a picture with lower exposure.")
        hsv=cv2.cvtColor(center, cv2.COLOR_BGR2HSV)
        lower_skin = np.array([0,30,60])
        upper_skin = np.array([25,255,255])
        skin_mask = cv2.inRange(hsv,lower_skin,upper_skin)
        skin_pixels=center[skin_mask>0]
        if len(skin_pixels) == 0 :
            raise ValueError("No skin was detected on your image. Use image where wrist is shown in the center, and there is enough natural light")
        if len(skin_pixels)<500:
            raise ValueError("Not enough skin area was detected on your image, reupload with wrist in the center.")
        skin_rgb=np.mean(
            cv2.cvtColor(skin_pixels.reshape(-1,1,3), cv2.COLOR_BGR2RGB),
            axis=0
        )
        self.skin_color = skin_rgb.astype(int)[0]
        r,g,b=self.skin_color
        if r>g and r>b:
            self.skin_description="pink/red hue ---- cool type"
        elif g>r and g>b:
            self.skin_description="yellow/olive hue ----- warm type"
        elif b>r and b>g:
            self.skin_description="bluish hue ---- cool type"
        else:
            self.skin_description="neutral"
        brightness=(0.299*r+0.587*g+0.114*b)
        if brightness>200:
            self.skin_type="Ivory skin"
        elif brightness>150:
            self.skin_type="Fair skin"
        else:
            self.skin_type="Olive skin"

        lower_blue=np.array([90,40,20])
        upper_blue=np.array([140,255,255])
        blue_mask=cv2.inRange(hsv,lower_blue,upper_blue)
        lower_green=np.array([35,40,20])
        upper_green=np.array([85,255,255])
        green_mask=cv2.inRange(hsv,lower_green,upper_green)
        lower_purple=np.array([140,40,20])
        upper_purple=np.array([165, 255, 255])
        purple_mask= cv2.inRange(hsv,lower_purple,upper_purple)
        blue_count=np.sum(blue_mask>0)
        green_count=np.sum(green_mask>0)
        purple_count=np.sum(purple_mask>0)

        if (blue_count+purple_count)> green_count*1.2:
            self.vein_color="Blue/Purple"
            vein_indicator="cool"
        elif green_count>(blue_count+purple_count)*1.2:
            self.vein_color="Green"
            vein_indicator="warm"
        else:
            self.vein_color="Mixed"
            vein_indicator="neutral"
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
        conn=sqlite3.connect(self.db_name)
        cursor=conn.cursor()
        skin_hex='#{:02x}{:02x}{:02x}'.format(*self.skin_color)
        cursor.execute("""INSERT INTO wrist_analysis
            (image_name, skin_rgb, skin_hex, skin_type, skin_description, vein_type, undertone, date_time)
            VALUES (?, ?, ?, ?, ?, ?,?,?)
        """,(
            os.path.basename(self.image_path),
            str(self.skin_color.tolist()),
            skin_hex,
            self.skin_type,
            self.skin_description,
            self.vein_color,
            self.undertone,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        conn.close()

    def get_results(self):
        return{
            "skin_rgb": self.skin_color,
            "skin_hex": '#{:02x}{:02x}{:02x}'.format(*self.skin_color),
            "skin_type": self.skin_type,
            "skin_description": self.skin_description,
            "vein_color": self.vein_color,
            "undertone": self.undertone
        }

    def get_all_records(self):
        conn=sqlite3.connect(self.db_name)
        cursor=conn.cursor()
        cursor.execute("SELECT * FROM wrist_analysis")
        data=cursor.fetchall()
        conn.close()
        return data

        
    #records = WristColorAnalyzer.get_all_records()

    def run_analysis(self):
        try:
            self.analyze()
            self.save_to_database()

            return self.get_results()
        except FileNotFoundError:
            return{"Error, image file was not found "}
        except ValueError as error:
            return{"Error": str(error)}
        except:
            return{"Error, something is wrong"}