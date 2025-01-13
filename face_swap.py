import numpy as np
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import insightface
from insightface.app import FaceAnalysis
from insightface.model_zoo import get_model
import os
from tkinter import ttk
import threading
import time

# Initialize FaceAnalysis
app = FaceAnalysis(name='buffalo_l')
app.prepare(ctx_id=0, det_size=(640, 640))

# Global variables to store images and image file names
img1 = None
img2 = None
img_rgb1 = None
img_rgb2 = None
img_swapped = None
img_name1 = ""
img_name2 = ""

# Resize parameters for displaying images
DISPLAY_WIDTH = 300
DISPLAY_HEIGHT = 300
CANVAS_PADDING = 10 # space between canvas and image

def load_image_and_display(image_num):
    global img1, img2, img_rgb1, img_rgb2, img_name1, img_name2
    
    # Open file dialog to select images
    image_path = filedialog.askopenfilename(title=f"Select the {'first' if image_num == 1 else 'second'} image",
                                            filetypes=[("All files", "*.*"), ("Image files", "*.jpg;*.jpeg;*.png;*.bmp;*.gif;*.tiff")])
    if not image_path:
        return None

    image = cv2.imread(image_path)
    if image is None:
        messagebox.showerror("Error", f"Could not load image {image_num}. Please select a valid image.")
        return None

    # Convert BGR to RGB for display in Tkinter
    img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Store the images and their file names
    if image_num == 1:
        img1 = image
        img_rgb1 = img_rgb
        img_name1 = os.path.basename(image_path)  # Get the file name
    elif image_num == 2:
        img2 = image
        img_rgb2 = img_rgb
        img_name2 = os.path.basename(image_path)  # Get the file name

    # Resize the image to fit the window
    img_resized = cv2.resize(img_rgb, (DISPLAY_WIDTH, DISPLAY_HEIGHT))

    # Display the image in the Tkinter window
    img_pil = Image.fromarray(img_resized)
    img_tk = ImageTk.PhotoImage(img_pil)
    
    if image_num == 1:
        canvas_image1.image = img_tk
        canvas_image1.create_image(DISPLAY_WIDTH/2, DISPLAY_HEIGHT/2, image=img_tk)
        label_name1.config(text=img_name1)
    elif image_num == 2:
        canvas_image2.image = img_tk
        canvas_image2.create_image(DISPLAY_WIDTH/2, DISPLAY_HEIGHT/2, image=img_tk)
        label_name2.config(text=img_name2)

    # If both images are loaded, enable the swap button
    if img1 is not None and img2 is not None:
        swap_button.config(state="normal")

def load_and_swap_faces():
    # Disable the swap button and show loading
    swap_button.config(state="disabled")
    label_loading.config(text="Swapping faces, please wait...", font=('Arial', 14, 'bold'))
    progress_bar.start() # Start progress bar
    
    # Start the face swap operation in a separate thread to keep UI responsive
    threading.Thread(target=perform_face_swap, daemon=True).start()

def perform_face_swap():
    global img_swapped
    try:
        # Detect faces in both images
        faces1 = app.get(img1)
        faces2 = app.get(img2)

        if len(faces1) == 0 or len(faces2) == 0:
            raise Exception("No faces detected in one or both images.")

        # Extract faces
        source_face = faces2[0]  # First face from second image
        target_face = faces1[0]  # First face from first image

        # Perform the face swap
        swapper = get_model('inswapper_128.onnx', download=False, download_zip=False)
        img_swapped = swapper.get(img2, source_face, target_face, paste_back=True)

        # Convert to RGB for displaying
        img_swapped_rgb = cv2.cvtColor(img_swapped, cv2.COLOR_BGR2RGB)

        # Resize the swapped image to fit the window
        img_swapped_resized = cv2.resize(img_swapped_rgb, (DISPLAY_WIDTH, DISPLAY_HEIGHT))

        # Display the swapped image
        img_swapped_pil = Image.fromarray(img_swapped_resized)
        img_swapped_tk = ImageTk.PhotoImage(img_swapped_pil)

        canvas_image_swapped.image=img_swapped_tk
        canvas_image_swapped.create_image(DISPLAY_WIDTH/2, DISPLAY_HEIGHT/2, image=img_swapped_tk)
        
        # Show the swapped image along with the two original images
        display_images()

        # Enable the save button
        save_button.config(state="normal")
        label_loading.config(text="")
        progress_bar.stop() # Stop progress bar

    except Exception as e:
        label_loading.config(text="")
        progress_bar.stop() # Stop progress bar
        messagebox.showerror("Error", str(e))

def display_images():
    # Display the first image
    img1_resized = cv2.resize(img_rgb1, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
    img1_pil = Image.fromarray(img1_resized)
    img1_tk = ImageTk.PhotoImage(img1_pil)
    canvas_image1.image = img1_tk
    canvas_image1.create_image(DISPLAY_WIDTH/2, DISPLAY_HEIGHT/2, image=img1_tk)

    # Display the second image
    img2_resized = cv2.resize(img_rgb2, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
    img2_pil = Image.fromarray(img2_resized)
    img2_tk = ImageTk.PhotoImage(img2_pil)
    canvas_image2.image = img2_tk
    canvas_image2.create_image(DISPLAY_WIDTH/2, DISPLAY_HEIGHT/2, image=img2_tk)


def save_image():
    save_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")])
    if save_path:
        # We are already working with the RGB image, so just save it
        cv2.imwrite(save_path, img_swapped)
        messagebox.showinfo("Saved", f"Image saved as {save_path}")

# Create Tkinter window
root = tk.Tk()
root.title("Face Swap Application")

# Set the window size (and not full-screen mode for ease of use)
root.geometry("1000x700")  # Set a fixed window size for better control

# Configure style for ttk widgets
style = ttk.Style(root)
style.theme_use('clam') # Use a modern theme

style.configure('TButton', font=('Arial', 12), padding=10)
style.configure('TLabel', font=('Arial', 10), padding=5)
style.configure("TFrame", background="#f0f0f0") # Light background

# Set style for labels
style.configure('Bold.TLabel', font=('Arial', 14, 'bold'))


# Function to toggle full-screen mode with the Escape key
def toggle_full_screen(event=None):
    if root.attributes("-fullscreen"):
        root.attributes("-fullscreen", False)
        root.geometry("1000x700")  # Restore to a fixed size
    else:
        root.attributes("-fullscreen", True)
        root.geometry("")  # Let the window take up the full screen
    return "break"

# Bind Escape key to toggle full-screen
root.bind("<Escape>", toggle_full_screen)

# Function to handle window close event properly
def on_close():
    root.quit()  # Safely close the application

# Bind the close event to the on_close function
root.protocol("WM_DELETE_WINDOW", on_close)

# Create a frame to organize the layout
frame = ttk.Frame(root, padding=20)  # Add padding around the frame
frame.pack(fill="both", expand=True)

# Configure grid layout for the frame
frame.grid_columnconfigure(0, weight=1)
frame.grid_columnconfigure(1, weight=1)
frame.grid_columnconfigure(2, weight=1)
frame.grid_rowconfigure(0, weight=1)
frame.grid_rowconfigure(1, weight=0)
frame.grid_rowconfigure(2, weight=0)
frame.grid_rowconfigure(3, weight=0)
frame.grid_rowconfigure(4, weight=0)


# Add image canvases
canvas_image1 = tk.Canvas(frame, width=DISPLAY_WIDTH + 2*CANVAS_PADDING, height=DISPLAY_HEIGHT + 2*CANVAS_PADDING)
canvas_image1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
canvas_image2 = tk.Canvas(frame, width=DISPLAY_WIDTH + 2*CANVAS_PADDING, height=DISPLAY_HEIGHT + 2*CANVAS_PADDING)
canvas_image2.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
canvas_image_swapped = tk.Canvas(frame, width=DISPLAY_WIDTH + 2*CANVAS_PADDING, height=DISPLAY_HEIGHT + 2*CANVAS_PADDING)
canvas_image_swapped.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")


# Add labels for displaying image names
label_name1 = ttk.Label(frame, text="", style='Bold.TLabel')
label_name1.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

label_name2 = ttk.Label(frame, text="", style='Bold.TLabel')
label_name2.grid(row=1, column=1, padx=10, pady=5, sticky="ew")


# Add loading label
label_loading = ttk.Label(frame, text="")
label_loading.grid(row=1, column=2, padx=10, pady=5, sticky="ew")


# Progress bar
progress_bar = ttk.Progressbar(frame, orient="horizontal", mode="indeterminate")
progress_bar.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=10)

# Add buttons in a grid layout to prevent shifting
load_button1 = ttk.Button(frame, text="Load First Image", command=lambda: load_image_and_display(1))
load_button1.grid(row=3, column=0, pady=10, sticky="ew")

load_button2 = ttk.Button(frame, text="Load Second Image", command=lambda: load_image_and_display(2))
load_button2.grid(row=3, column=1, pady=10, sticky="ew")

# Add button to swap faces
swap_button = ttk.Button(frame, text="Swap Faces", state="disabled", command=load_and_swap_faces)
swap_button.grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")

# Add button to save the swapped face image
save_button = ttk.Button(frame, text="Save Swapped Image", state="disabled", command=save_image)
save_button.grid(row=4, column=2, pady=10, sticky="ew")

def resize_canvas(event, canvas):
    global DISPLAY_WIDTH, DISPLAY_HEIGHT
    canvas.delete("all") # Delete previous content
    
    # Calculate new image size, and ensure min size
    DISPLAY_WIDTH= min(event.width, DISPLAY_WIDTH) - 2*CANVAS_PADDING
    DISPLAY_HEIGHT = min(event.height, DISPLAY_HEIGHT) - 2*CANVAS_PADDING

    
    if canvas == canvas_image1 and img_rgb1 is not None:
        img1_resized = cv2.resize(img_rgb1, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        img1_pil = Image.fromarray(img1_resized)
        img1_tk = ImageTk.PhotoImage(img1_pil)
        canvas.image = img1_tk
        canvas.create_image(event.width/2, event.height/2, image=img1_tk)

    elif canvas == canvas_image2 and img_rgb2 is not None:
        img2_resized = cv2.resize(img_rgb2, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        img2_pil = Image.fromarray(img2_resized)
        img2_tk = ImageTk.PhotoImage(img2_pil)
        canvas.image = img2_tk
        canvas.create_image(event.width/2, event.height/2, image=img2_tk)
    
    elif canvas == canvas_image_swapped and img_swapped is not None:
        img_swapped_rgb = cv2.cvtColor(img_swapped, cv2.COLOR_BGR2RGB)
        img_swapped_resized = cv2.resize(img_swapped_rgb, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        img_swapped_pil = Image.fromarray(img_swapped_resized)
        img_swapped_tk = ImageTk.PhotoImage(img_swapped_pil)
        canvas.image = img_swapped_tk
        canvas.create_image(event.width/2, event.height/2, image=img_swapped_tk)


canvas_image1.bind("<Configure>", lambda event: resize_canvas(event, canvas_image1))
canvas_image2.bind("<Configure>", lambda event: resize_canvas(event, canvas_image2))
canvas_image_swapped.bind("<Configure>", lambda event: resize_canvas(event, canvas_image_swapped))


# Start Tkinter event loop
root.mainloop()