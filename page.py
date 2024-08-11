import threading
import sys
import tkinter as tk
from tkinter.constants import *
from PIL import Image, ImageTk
import sounddevice as sd
import numpy as np
import wavio
import librosa
from tensorflow.keras.models import load_model
from tkinter import messagebox

# Define the possible classes and associated problems
class_labels = {
    0: "Grinding",
    1: "Invalid",
    2: "Knocking",
    3: "Normal",
    4: "Squeaking",
}

# Function to preprocess user input sound
def preprocess_sound(file_path):
    y, sr = librosa.load(file_path, sr=None)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
    mfcc_scaled = np.mean(mfcc.T, axis=0)
    return mfcc_scaled.reshape(1, mfcc_scaled.shape[0], 1)

# Load trained model
model_path = 'D:/Download/pdwa-20240720T174257Z-001/pdwa/fcnn_engine_sound_classification_model_finals.h5'
model = load_model(model_path)

# Function to predict sound class
def predict_sound_class(file_path, model):
    preprocessed_sound = preprocess_sound(file_path)
    prediction = model.predict(preprocessed_sound)
    predicted_class = np.argmax(prediction)
    
    # Retrieve the label and possible problem from the dictionary
    label = class_labels.get(predicted_class, "Unknown")
    return label

class MainApp:
    def __init__(self, top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''

        top.geometry("800x480")
        top.title("FAULT FINDER PRO")
        top.resizable(0, 0)
        top.configure(background="#6a7095")
        top.configure(highlightbackground="#d9d9d9")
        top.configure(highlightcolor="#000000")

        self.top = top

        # Container to hold all pages
        self.container = tk.Frame(top)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.configure(background="#00001c")
        self.container.configure(highlightbackground="#d9d9d9")
        self.container.configure(highlightcolor="#000000")

        self.pages = {}  # Dictionary to store pages

        # Create pages
        for PageClass in (GettingStartedPage, MainPage, InformationPage):
            page_name = PageClass.__name__
            page = PageClass(parent=self.container, controller=self)
            self.pages[page_name] = page
            page.grid(row=0, column=0, sticky="nsew")

        self.show_page("GettingStartedPage")

    def show_page(self, page_name):
        page = self.pages[page_name]
        page.tkraise()

    def show_main_dashboard(self):
        self.show_page("MainPage")

    def show_information_page(self):
        self.show_page("InformationPage")

    def update_information_page_text(self, sound_class, problems, recommendations):
        information_page = self.pages["InformationPage"]
        information_page.update_label_text(sound_class, problems, recommendations)

    def update_list_history(self, items):
        main_page = self.pages["MainPage"]
        main_page.AddItemListbox2(items)

class GettingStartedPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.Canvas1 = tk.Canvas(self)
        self.Canvas1.place(relx=0.005, rely=0.004, relheight=0.985, relwidth=0.991)
        self.Canvas1.configure(background="#151a24")
        self.Canvas1.configure(borderwidth="2")
        self.Canvas1.configure(highlightbackground="#d9d9d9")
        self.Canvas1.configure(highlightcolor="#000000")
        self.Canvas1.configure(relief="ridge")
        self.Canvas1.configure(selectbackground="#d9d9d9")
        self.Canvas1.configure(selectforeground="black")

        self.Frame1 = tk.Frame(self.Canvas1)
        self.Frame1.place(relx=0.013, rely=0.021, relheight=0.962, relwidth=0.98)
        self.Frame1.configure(relief='groove')
        self.Frame1.configure(borderwidth="2")
        self.Frame1.configure(background="#151a24")
        self.Frame1.configure(highlightbackground="#d9d9d9")
        self.Frame1.configure(highlightcolor="#000000")

        self.Button1 = tk.Button(self.Frame1)
        self.Button1.place(relx=0.322, rely=0.703, height=76, width=267)
        self.Button1.configure(activebackground="#d9d9d9")
        self.Button1.configure(activeforeground="black")
        self.Button1.configure(background="#ffffff")
        self.Button1.configure(disabledforeground="#a3a3a3")
        self.Button1.configure(font="-family {Segoe UI} -size 28")
        self.Button1.configure(foreground="#000000")
        self.Button1.configure(highlightbackground="#d9d9d9")
        self.Button1.configure(highlightcolor="#000000")
        self.Button1.configure(text='''GET STARTED''', command=self.continue_to_dashboard)

        image_path = "./assets/img/F1.png"
        image1 = Image.open(image_path)
        test = ImageTk.PhotoImage(image1)
        self.Label1 = tk.Label(self.Canvas1, image=test)
        self.Label1.image = test  # Keep a reference to avoid garbage collection
        self.Label1.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
        self.Label1.configure(borderwidth=0)

    def continue_to_dashboard(self):
        self.controller.show_main_dashboard()

class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.is_recording = False  # To track the recording state
        self.recording = None  # Store the recording object
        self.fs = 44100  # Sample rate
        self.recording_file_path = "output.wav"  # Default file path for the recording
        self.recorded_data = []  # Store recorded data in a list

        self.Canvas1 = tk.Canvas(self)
        self.Canvas1.place(relx=0.009, rely=0.019, relheight=0.965, relwidth=0.98)
        self.Canvas1.configure(background="#151a24")
        self.Canvas1.configure(highlightbackground="#d9d9d9")
        self.Canvas1.configure(highlightcolor="#000000")
        self.Canvas1.configure(insertbackground="#000000")
        self.Canvas1.configure(relief="ridge")
        self.Canvas1.configure(selectbackground="#d9d9d9")
        self.Canvas1.configure(selectforeground="black")

        diagnose = Image.open('assets/img/diagnose.png')
        dimg = ImageTk.PhotoImage(diagnose)

        self.btnDiagnose = tk.Button(self.Canvas1, image=dimg)
        self.btnDiagnose.place(relx=0.599, rely=0.518, height=186, width=277)
        self.btnDiagnose.image = dimg
        self.btnDiagnose.configure(command=self.diagnose_sound)
        self.btnDiagnose.place_forget()  # Hide the diagnose button initially

        recording = Image.open('assets/img/record.png')
        ring = ImageTk.PhotoImage(recording)

        self.btnRecord = tk.Button(self.Canvas1, image=ring)
        self.btnRecord.place(relx=0.599, rely=0.065, height=196, width=277)
        self.btnRecord.image = ring
        self.btnRecord.configure(command=self.start_recording)

        stop_img = Image.open('assets/img/stop.png')
        self.stop_icon = ImageTk.PhotoImage(stop_img)

        self.btnStop = tk.Button(self.Canvas1, image=self.stop_icon)
        self.btnStop.place(relx=0.599, rely=0.065, height=196, width=277)
        self.btnStop.image = self.stop_icon
        self.btnStop.configure(command=self.stop_recording)
        self.btnStop.place_forget()  # Hide the stop button initially

        self.Labelframe1 = tk.LabelFrame(self.Canvas1)
        self.Labelframe1.place(relx=0.077, rely=0.065, relheight=0.853, relwidth=0.51)
        self.Labelframe1.configure(relief='groove')
        self.Labelframe1.configure(font="-family {Segoe UI} -size 18")
        self.Labelframe1.configure(foreground="#ffffff")
        self.Labelframe1.configure(labelanchor="n")
        self.Labelframe1.configure(text='''SCAN HISTORY''')
        self.Labelframe1.configure(background="#637188")
        self.Labelframe1.configure(highlightbackground="#d9d9d9")
        self.Labelframe1.configure(highlightcolor="#000000")

        self.Listbox2 = tk.Listbox(self.Labelframe1)
        self.Listbox2.place(relx=0.028, rely=0.091, relheight=0.841, relwidth=0.944)
        self.Listbox2.configure(background="white")
        self.Listbox2.configure(disabledforeground="#a3a3a3")
        self.Listbox2.configure(font="TkFixedFont")
        self.Listbox2.configure(foreground="#000000")
        self.Listbox2.configure(highlightbackground="#d9d9d9")
        self.Listbox2.configure(highlightcolor="#000000")
        self.Listbox2.configure(selectbackground="#c4c4c4")
        self.Listbox2.configure(selectforeground="black")
        self.Listbox2.configure(activestyle='none')

    def AddItemListbox2(self, items):
        for item in items:
            self.Listbox2.insert(tk.END, item)

    def start_recording(self):
        self.is_recording = True
        self.recorded_data = []  # Clear previously recorded data

        def callback(indata, frames, time, status):
            if self.is_recording:
                self.recorded_data.append(indata.copy())

        self.recording = sd.InputStream(callback=callback, channels=1, samplerate=self.fs)
        self.recording.start()
        self.btnRecord.place_forget()
        self.btnStop.place(relx=0.599, rely=0.065, height=196, width=277)

    def stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.recording.stop()
            self.btnStop.place_forget()
            self.btnDiagnose.place(relx=0.599, rely=0.518, height=186, width=277)
            self.btnRecord.place(relx=0.599, rely=0.065, height=196, width=277)

            # Convert recorded data to numpy array and save as WAV file
            recorded_array = np.concatenate(self.recorded_data, axis=0)
            wavio.write(self.recording_file_path, recorded_array, self.fs, sampwidth=2)

    def diagnose_sound(self):
        # Run sound diagnosis and update information page
        sound_class = predict_sound_class(self.recording_file_path, model)

        # Determine possible problems and recommendations based on the predicted label
        problems = []
        recommendations = []

        if sound_class == "Squeaking":
            problems.append(" ")
            recommendations.append("Loose belt")
            recommendations.append("Worn belt")
        elif sound_class == "Grinding":
            problems.append(" ")
            recommendations.append("Water pump")
            recommendations.append("Alternator bearing")
        elif sound_class == "Knocking":
            problems.append(" ")
            recommendations.append("Fuel injector")
            recommendations.append("Excessive clearance")
        elif sound_class == "Normal":
            problems.append(" ")
            recommendations.append("No action required")
        elif sound_class == "Invalid":
            problems.append(" ")
            recommendations.append("Ensure you are recording the sound correctly")

        # Update the information page with sound class, problem, and recommendations
        self.controller.update_information_page_text(sound_class, problems, recommendations)
        self.controller.show_information_page()
        self.AddItemListbox2([f"{sound_class} {''.join(problems)}"])

class InformationPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(background="#151a24")  # Dark background color

        # Sound Class Label
        self.class_label = tk.Label(self, font=("Arial", 48, "bold"), bg="#151a24")
        self.class_label.pack(pady=25)  # Adjusted padding

        # Recommendations Listbox now includes possible problems
        self.recommendation_listbox = tk.Listbox(self, font=("Arial", 16), fg="black", bg="white", selectbackground="white", selectforeground="black")
        self.recommendation_listbox.pack(pady=80, padx=20, fill="x", expand=True)

        # Resize and add Back Button
        back_img = Image.open('./assets/img/back.png')
        back_img = back_img.resize((50, 50), Image.Resampling.LANCZOS)  # Resize image to 50x50
        self.back_icon = ImageTk.PhotoImage(back_img)
        self.back_button = tk.Button(self, image=self.back_icon, command=self.go_back, bg="#151a24", bd=0)
        self.back_button.place(relx=0.01, rely=0.01, anchor=tk.NW)

        # Add Save Button
        self.save_button = tk.Button(self, text="Save", font=("Arial", 16, "bold"), bg="yellow", fg="black", command=self.save_information)
        self.save_button.place(relx=0.85, rely=0.85, width=100, height=50)

    def update_label_text(self, sound_class, problems, recommendations):
        # Choose color based on sound class
        color = "black"  # Default color
        if sound_class in ["Grinding", "Knocking", "Squeaking"]:
            color = "red"
        elif sound_class == "Normal":
            color = "green"
        elif sound_class == "Invalid":
            color = "blue"

        self.class_label.config(text=sound_class, fg=color)
        self.recommendation_listbox.delete(0, tk.END)
        self.recommendation_listbox.insert(tk.END, "POSSIBLE PROBLEM")
        for problem in problems:
            self.recommendation_listbox.insert(tk.END, problem)
        for recommendation in recommendations:
            self.recommendation_listbox.insert(tk.END, recommendation)

    def go_back(self):
        self.controller.show_main_dashboard()

    def save_information(self):
        # Implement save functionality
        messagebox.showinfo("Save", "Information saved successfully!")
        self.controller.show_main_dashboard()

if __name__ == '__main__':
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
