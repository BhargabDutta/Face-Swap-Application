# Face-Swap-Application
A Python-based Face Swap application built using OpenCV, InsightFace, Tkinter, and PIL. This app allows users to load two images, swap faces between them, and save the resulting image.

**Features**
1. Load Images: Load two images from your file system to swap faces between them.
2. Face Detection and Swap: Automatically detect faces in the selected images and perform a face swap.
3. Progress Indicator: Shows a loading bar while the face swap operation is being performed.
4. Image Saving: Save the resulting face-swapped image to your file system.
5. Responsive UI: The GUI is designed to adjust to window resizing.

**Prerequisites**
1. Python 3.7 or higher
2. Required Python libraries:
    a. numpy
    b. opencv-python
    c. Pillow (PIL)
    d. tkinter
    e. insightface
    f. ttk

**Installation**
To use the Face Swap Application, follow these steps:
1. Clone the repository:
   ```
   git clone https://github.com/BhargabDutta/Face-Swap-Application.git
   cd Face-Swap-Application
   ```
2. Install dependencies:

If you haven't already, install Python 3.7 or higher. Then, install the necessary dependencies:
```
pip install -r requirements.txt
```
Ensure that you have the necessary libraries like `numpy`, `opencv-python`, `Pillow`, `tkinter`, and `insightface`.

3. Download the InsightFace model:
The application uses InsightFace for face detection and swapping. Make sure the required model (inswapper_128.onnx) is downloaded and available in your environment.
You can download it from here [https://drive.google.com/drive/folders/1lxhAVv3e2GuC-rJpKCQIaXvKl9s1g8OA?usp=sharing]

**Usage**
1. Run the application:
    To start the face swap application, run the following command:
    `python face_swap_app.py`

2. Load Images:
   a. Click "Load First Image" to select the first image (the image where the face will be replaced).
   b. Click "Load Second Image" to select the second image (the image from which the face will be taken).

3. Swap Faces:
   a. After loading both images, click the "Swap Faces" button.
   b. The application will swap the faces and display the result.

4. Save Swapped Image:
   After the faces are swapped, click "Save Swapped Image" to save the resulting image to your local system.
