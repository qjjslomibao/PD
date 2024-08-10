import tkinter as tk
from PIL import Image, ImageTk
import os

# Create the main window
root = tk.Tk()
root.title("FAULT FINDER PRO")
root.geometry("800x480")  # Set custom dimensions

# Set the background color to gray
root.configure(bg="#151A24")

# Load the logo image
logo_image = Image.open("ffpro.png")  # Replace with your logo image file

# Resize the logo image to fit the window (e.g., 157x157 pixels)
logo_image = logo_image.resize((157, 157))
logo_image = ImageTk.PhotoImage(logo_image)

# Create a label to display the logo image with a gray background
logo_label = tk.Label(root, image=logo_image, bg="#151A24")
logo_label.image = logo_image  # Keep a reference to the image
logo_label.place(relx=0.5, rely=0.3, anchor=tk.CENTER)  # Position of the logo 

# Create a button to get started
def open_page():
    root.destroy()  # Close the current window
    os.system("python page.py")  # Open page.py in a new window

# Create a Canvas for the button
canvas = tk.Canvas(root, width=150, height=50, bg="#151A24", highlightthickness=0)
canvas.place(relx=0.5, rely=0.7, anchor=tk.CENTER)  # Position of the button

# Draw a rounded rectangle
def round_rectangle(x1, y1, x2, y2, radius=80, **kwargs):
    points = [
        x1 + radius, y1,
        x1 + radius, y1,
        x2 - radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1 + radius,
        x1, y1,
    ]
    return canvas.create_polygon(points, **kwargs, smooth=True)

button = round_rectangle(10, 10, 140, 40, radius=10, fill="white", outline="")
canvas.create_text(75, 25, text="GET STARTED", fill="#151A24", font=("Noto Sans SC", 12))

# Bind the button click
def on_button_click(event):
    open_page()

canvas.tag_bind(button, "<Button-1>", on_button_click)
canvas.tag_bind(canvas.create_text(75, 25, text="GET STARTED", fill="#151A24", font=("Noto Sans SC", 12)), "<Button-1>", on_button_click)

# Run the application
root.mainloop()
