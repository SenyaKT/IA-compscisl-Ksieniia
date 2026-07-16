import sys 
sys.path.append("D:/Lib/site-packages")
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import shutil
import os

from season_dict import classify_season, SEASONS
from season_questionnaire import QUESTIONS, answered
from color_analyzer import WristColorAnalyzer
from database import create_history_table, save_analysis, get_history

BACKGROUND_COLOR ="#F5F5F5"
SIDEBAR_COLOR= "#E8E8E8"
BUTTON_COLOR = "#B5C8D8"
BUTTON_HOVER_COLOR = "#9bb5c8"
TEXT_COLOR="#2C2C2C"
CARD_COLOR="#FAC6C6"

TITLE_FONT=("Arial", 22, "bold")
HEADING_FONT=("Arial", 15, "bold")
NORMAL_FONT=("Arial", 13)
BUTTON_FONT=("Arial", 13, "bold")

WINDOW_WIDTH=1000
WINDOW_HEIGHT=700

UPLOAD_FOLDER="uploads"

class Home(ctk.CTkFrame):
    def __init__(self,parent, app):
        super().__init__(parent, fg_color=BACKGROUND_COLOR)
        self.app=app
        ctk.CTkLabel(self, text="Personal Color Analysis", font=TITLE_FONT, text_color=TEXT_COLOR).pack(pady=(80,10))
        ctk.CTkLabel(self, text="Find your seasonal color palette.\nAnswer 8 questions and upload wrist photo.", font=NORMAL_FONT, text_color=TEXT_COLOR, justify="center").pack(pady=10)
        ctk.CTkLabel(self, text="Type your name:", font=NORMAL_FONT, text_color=TEXT_COLOR).pack(pady=(30,5))
        self.name_entry=ctk.CTkEntry(self, width=220, font=NORMAL_FONT)
        self.name_entry.pack(pady=5)
        ctk.CTkButton(self, text="Start analysis", font=BUTTON_FONT, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR,text_color=TEXT_COLOR, width=180, height=38, command=self.start).pack(pady=20)

    def start(self):
        name=self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Name required","Please enter your name.")
            return
        self.app.username=name
        self.app.answers={}
        self.app.wrist_data=None
        self.app.show_page("questionnaire")

class Questionnaire_Page(ctk.CTkFrame):
    def __init__(self,parent,app):
        super().__init__(parent,fg_color=BACKGROUND_COLOR)
        self.app=app
        self.selected={}
        ctk.CTkLabel(self,text="Questionnaire", font=TITLE_FONT, text_color=TEXT_COLOR).pack(pady=(20,10))
        scroll=ctk.CTkScrollableFrame(self, fg_color=CARD_COLOR, width=680, height=420)
        scroll.pack(pady=5)
        for q in QUESTIONS:
            ctk.CTkLabel(scroll,text=q["text"], font=HEADING_FONT, text_color=TEXT_COLOR,anchor="w").pack(fill="x", padx=15,pady=(12,4))
            var=ctk.StringVar(value="")
            self.selected[q["key"]]=var
            for label,value in q["options"]:
                ctk.CTkRadioButton(scroll, text=label,variable=var,value=value,font=NORMAL_FONT,text_color=TEXT_COLOR,fg_color=BUTTON_COLOR).pack(anchor="w",padx=35,pady=2)
        
        ctk.CTkButton(self,text="Continue", font=BUTTON_FONT, fg_color=BUTTON_COLOR,hover_color=BUTTON_HOVER_COLOR, text_color=TEXT_COLOR,width=180,height=38, command=self.submit).pack(pady=15)

    def submit(self):
        answers={}
        for key ,var in self.selected.items():
            answers[key]=var.get()
        if not answered(answers):
            messagebox.showwarning("Incomplete","Please answer all questions.")
            return
        self.app.answers=answers
        self.app.show_page("photo")
    
class Photo(ctk.CTkFrame):
    def __init__(self,parent,app):
        super().__init__(parent,fg_color=BACKGROUND_COLOR)
        self.app=app
        self.image_path=None
        ctk.CTkLabel(self, text="Wrist Photo", font=TITLE_FONT , text_color=TEXT_COLOR).pack(pady=(50,10))
        ctk.CTkLabel(self, text="You may appload a photo of your inner wrist taken under natural daylight.\nWrist must be in the center of the photo, visible clearly.\n Formats Accepted: JPG, JPEG, PNG",font=NORMAL_FONT,text_color=TEXT_COLOR, justify="center").pack(pady=10)
        self.preview=ctk.CTkLabel(self, text="No photo selected yet.",font=NORMAL_FONT,text_color=TEXT_COLOR)
        self.preview.pack(pady=15)
        ctk.CTkButton(self, text="Choose Photo from device",font=BUTTON_FONT, fg_color=BUTTON_COLOR,hover_color=BUTTON_HOVER_COLOR, text_color=TEXT_COLOR,width=180,height=38,command=self.choose_photo).pack(pady=5)
        button_row=ctk.CTkFrame(self,fg_color="transparent")
        button_row.pack(pady=20)
        ctk.CTkButton(button_row, text="Skip",font=BUTTON_FONT, fg_color="#CCCCCC",hover_color="#BBBBBB", text_color=TEXT_COLOR,width=130,height=38,command=self.skip).pack(side="left",padx=10)
        ctk.CTkButton(button_row, text="Analyze and Continue",font=BUTTON_FONT, fg_color=BUTTON_COLOR,hover_color=BUTTON_HOVER_COLOR, text_color=TEXT_COLOR,width=138,height=38,command=self.analyze).pack(side="left",padx=10)
        
    def choose_photo(self):
            path=filedialog.askopenfilename(title="Select wrist photo", filetypes=[("Image files","*.jpg *.jpeg *.png")])
            print("Selected path:",path)
            if not path:
                return
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            destination=os.path.join(UPLOAD_FOLDER,os.path.basename(path))
            shutil.copy(path,destination)
            self.image_path=destination
            self.preview.configure(text=os.path.basename(path))
            print("Image path set to:", self.image_path)

    def skip(self):
            self.app.wrist_data=None
            self.app.run_classification()

    def analyze(self):
            if not self.image_path:
                messagebox.showinfo("No photo", "Continuing without a photo")
                self.app.wrist_data=None
                self.app.run_classification()
                return
            try:
                analyzer=WristColorAnalyzer(self.image_path)
                result=analyzer.run_analysis()
                self.app.wrist_data=result
                self.app.run_classification()
            except FileNotFoundError as e:
                messagebox.showerror("File not found", str(e))
            except ValueError as e:
                messagebox.showerror("Photo issue", str(e))
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
class Results(ctk.CTkFrame):
    def __init__(self,parent,app):
          super().__init__(parent,fg_color=BACKGROUND_COLOR)
          self.app=app
          self.content=ctk.CTkScrollableFrame(self,fg_color=BACKGROUND_COLOR)
          self.content.pack(fill="both",expand=True,padx=10,pady=10)
        
    def show_results(self,result):
        for widget in self.content.winfo_children():
              widget.destroy()
        ctk.CTkLabel(self.content, text="Your Personal Season:" + result["season_name"], font=TITLE_FONT,text_color=TEXT_COLOR).pack(pady=(20,5))
        ctk.CTkLabel(self.content,text=result["description"], font=NORMAL_FONT,text_color=TEXT_COLOR,wraplength=600,justify="center").pack(pady=(0,15))
        ctk.CTkLabel(self.content,text="Your color palette", font=HEADING_FONT,text_color=TEXT_COLOR).pack(pady=(10,5))
        for rows in range(0,10,5):
             row=ctk.CTkFrame(self.content,fg_color="transparent")
             row.pack(pady=3)
             for hexcolors in result["best_colors"][rows:rows+5]:
                  self.draw_swatch(row,hexcolors,50)
        ctk.CTkLabel(self.content,text="Outfit Suggestions", font=HEADING_FONT, text_color=TEXT_COLOR).pack(pady=(20,5))

        outfitrow=ctk.CTkFrame(self.content,fg_color="transparent")
        outfitrow.pack(pady=5)
        for outfit in result["outfit_combinations"]:
            outfit_frame=ctk.CTkFrame(outfitrow,fg_color=CARD_COLOR)
            outfit_frame.pack(side="left",padx=10)
            for hexcolors in outfit:
                 self.draw_swatch(outfit_frame,hexcolors,45)

        ctk.CTkButton(self.content,text="Previous analysis",font=BUTTON_FONT,fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR, text_color=TEXT_COLOR,width=180,height=38,command=lambda:self.app.show_page("history")).pack(pady=20)

    def draw_swatch(self,parent,hexcolors,size):
            boximage=Image.new("RGB",(size,size),hexcolors)
            imagecolor=ctk.CTkImage(light_image=boximage,size=(size,size))
            frame=ctk.CTkFrame(parent,fg_color="transparent")
            frame.pack(side="left",padx=4,pady=4)
            label=ctk.CTkLabel(frame,image=imagecolor,text="")
            label.image=imagecolor
            label.pack()
            ctk.CTkLabel(frame,text=hexcolors,font=("Arial",9),text_color=TEXT_COLOR).pack()

class History(ctk.CTkFrame):
    def __init__(self,parent,app):
        super().__init__(parent,fg_color=BACKGROUND_COLOR)
        self.app=app
        ctk.CTkLabel(self,text="Recent Analyzes", font=TITLE_FONT,text_color=TEXT_COLOR).pack(pady=(20,10))
        self.list=ctk.CTkScrollableFrame(self,fg_color=CARD_COLOR,width=700,height=450)
        self.list.pack(pady=10)
    def clear(self):
        for widget in self.list.winfo_children():
            widget.destroy()
        records=get_history()
        if not records:
            ctk.CTkLabel(self.list,text="No analyses here yet",font=NORMAL_FONT,text_color=TEXT_COLOR).pack(pady=20)
            return
        for entry in records:
            row=ctk.CTkFrame(self.list,fg_color=BACKGROUND_COLOR)
            row.pack(fill="x",padx=10,pady=5)
            ctk.CTkLabel(row,text=entry["season_name"],font=HEADING_FONT,text_color=TEXT_COLOR,width=200,anchor="w").pack(side="left",padx=10)
            ctk.CTkLabel(row,text="Score:"+str(entry["score"]),font=NORMAL_FONT,text_color=TEXT_COLOR,width=80,anchor="w").pack(side="left",padx=10)
            ctk.CTkLabel(row,text=entry["date_time"],font=NORMAL_FONT,text_color=TEXT_COLOR,anchor="e").pack(side="right",padx=10)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Personal Color Analysis")
        self.geometry("1000x700")
        ctk.set_appearance_mode("light")
        self.username=None
        self.answers={}
        self.wrist_data=None
        create_history_table()
        sidebar=ctk.CTkFrame(self,width=160,fg_color=SIDEBAR_COLOR, corner_radius=0)
        sidebar.pack(side="left",fill="y")
        ctk.CTkButton(sidebar,text="Home",fg_color=BUTTON_COLOR,hover_color=BUTTON_HOVER_COLOR,text_color=TEXT_COLOR,font=BUTTON_FONT,command=lambda:self.show_page("home")).pack(padx=15,pady=(30,5),fill="x")
        ctk.CTkButton(sidebar,text="Questionnaire",fg_color=BUTTON_COLOR,hover_color=BUTTON_HOVER_COLOR,text_color=TEXT_COLOR,font=BUTTON_FONT,command=lambda:self.show_page("questionnaire")).pack(padx=15,pady=5,fill="x")
        ctk.CTkButton(sidebar,text="Photo",fg_color=BUTTON_COLOR,hover_color=BUTTON_HOVER_COLOR,text_color=TEXT_COLOR,font=BUTTON_FONT,command=lambda:self.show_page("photo")).pack(padx=15,pady=5,fill="x")
        ctk.CTkButton(sidebar,text="Results",fg_color=BUTTON_COLOR,hover_color=BUTTON_HOVER_COLOR,text_color=TEXT_COLOR,font=BUTTON_FONT,command=lambda:self.show_page("results")).pack(padx=15,pady=5,fill="x")
        ctk.CTkButton(sidebar,text="History",fg_color=BUTTON_COLOR,hover_color=BUTTON_HOVER_COLOR,text_color=TEXT_COLOR,font=BUTTON_FONT,command=lambda:self.show_page("history")).pack(padx=15,pady=5,fill="x")
        main=ctk.CTkFrame(self,fg_color=BACKGROUND_COLOR)
        main.pack(side="right",fill="both",expand=True)
        self.pages={
             "home":Home(main,self),
             "questionnaire":Questionnaire_Page(main,self),
             "photo":Photo(main,self),
             "results":Results(main,self),
             "history":History(main,self)

        }
        for page in self.pages.values():
             page.place(relx=0,rely=0,relwidth=1,relheight=1)
        self.show_page("home")
    def show_page(self,name):
            if name=="history":
                  self.pages["history"].clear()
            self.pages[name].tkraise()
    def run_classification(self):
             result=classify_season(self.answers,self.wrist_data)
             save_analysis(self.username,result["season_name"],result["score"],self.answers)
             self.pages["results"].show_results(result)
             self.show_page("results")
if __name__=="__main__":
    app=App()
    app.mainloop()


        
    




