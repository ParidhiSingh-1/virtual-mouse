# Virtual Mouse (AI Gesture Controller)

An AI-powered system controller using MediaPipe and OpenCV to manipulate your mouse, system volume, and screen brightness using hand gestures. Designed with a sleek CustomTkinter GUI interface.

---

## 🛠️ Prerequisites
* **Operating System:** Windows (Required for `pycaw` and volume/brightness system APIs)
* **Python Version:** Python 3.8 or higher
* A working Webcam

---

## 🚀 How to Run the Project

Open your Command Prompt (`cmd`) or Terminal and copy-paste the following exact commands step by step:

1. **Clone and Navigate to the Project:**
   ```bash
   # Clone the repository to your computer
   git clone [https://github.com/ParidhiSingh-1/virtual-mouse.git](https://github.com/ParidhiSingh-1/virtual-mouse.git)

   # Move exactly into the project folder
   cd virtual-mouse

2. **Install Dependencies:**
   * Run the following command to automatically install all required libraries:
     ```bash
     pip install -r requirements.txt
     ```

3. **Launch the Application:**
   * Run the script:
     ```bash
     python main.py
     ```

## Gesture Controls
* **Right Hand (Mouse Control):** 
  * Move Index Finger -> Move Cursor
  * Pinch Thumb + Index -> Left Click
  * Pinch Thumb + Middle -> Right Click
  * Pinch Index + Middle -> Scroll Screen
* **Left Hand (System Control):**
  * Change distance between Thumb + Index -> Adjust Volume
  * Move Palm Up / Down -> Adjust Screen Brightness
