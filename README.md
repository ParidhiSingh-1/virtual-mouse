# Virtual Mouse (AI Gesture Controller)

An AI-powered system controller using MediaPipe and OpenCV to manipulate your mouse, system volume, and screen brightness using hand gestures. Designed with a sleek CustomTkinter GUI interface.

## 🛠️ Prerequisites
* **Operating System:** Windows (Required for `pycaw` and volume/brightness APIs)
* **Python Version:** Python 3.8 or higher
* A working Webcam

## 🚀 How to Run the Project (For Interviewers)

1. **Clone or Download the Project:**
   * Click the green **Code** button at the top of this page.
   * Click **Download ZIP** and extract the folder to your computer.

2. **Open Terminal / Command Prompt:**
   * Open your Command Prompt (`cmd`) and navigate to the extracted folder:
     ```bash
     cd path/to/extracted/virtual-mouse
     ```

3. **Install Dependencies:**
   * Run the following command to automatically install all required libraries:
     ```bash
     pip install -r requirements.txt
     ```

4. **Launch the Application:**
   * Run the script:
     ```bash
     python main.py
     ```

## 🎮 Gesture Controls
* **Right Hand (Mouse Control):** 
  * Move Index Finger -> Move Cursor
  * Pinch Thumb + Index -> Left Click
  * Pinch Thumb + Middle -> Right Click
  * Pinch Index + Middle -> Scroll Screen
* **Left Hand (System Control):**
  * Change distance between Thumb + Index -> Adjust Volume
  * Move Palm Up / Down -> Adjust Screen Brightness
