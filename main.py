import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import screen_brightness_control as sbc
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import customtkinter as ctk
from threading import Thread

# --- GLOBAL OPTIMIZATION ---
pyautogui.FAILSAFE = False 
pyautogui.PAUSE = 0  
SCREEN_W, SCREEN_H = pyautogui.size()
SMOOTHING = 5 

class VirtualController:
    def __init__(self):
        self.running = False
        self.cap = None
        self.dragging = False
        self.plocX, self.plocY = 0, 0
        self.vol_per = 0
        self.bright_per = 0
        
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.8
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume = cast(interface, POINTER(IAudioEndpointVolume))
            self.vol_range = self.volume.GetVolumeRange() 
        except Exception: self.volume = None

    def get_dist(self, p1, p2):
        return np.hypot(p1.x - p2.x, p1.y - p2.y)

    def run_logic(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.running = True
        
        while self.running:
            success, frame = self.cap.read()
            if not success: break
            
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            status_msg = "Scanning..."
            action_color = (0, 212, 255) # Default Neon Blue

            if results.multi_hand_landmarks:
                for idx, hand_lms in enumerate(results.multi_hand_landmarks):
                    label = results.multi_handedness[idx].classification[0].label
                    
                    t_tip = hand_lms.landmark[4]
                    i_tip = hand_lms.landmark[8]
                    m_tip = hand_lms.landmark[12]
                    r_tip = hand_lms.landmark[16]
                    p_tip = hand_lms.landmark[20]

                    # --- RIGHT HAND: MOUSE & CURSOR ---
                    if label == 'Right':
                        # 1. CURSOR TRACKING
                        cx, cy = int(i_tip.x * w), int(i_tip.y * h)
                        nx = np.interp(cx, [w*0.2, w*0.8], [0, SCREEN_W])
                        ny = np.interp(cy, [h*0.2, h*0.8], [0, SCREEN_H])
                        currX = self.plocX + (nx - self.plocX) / SMOOTHING
                        currY = self.plocY + (ny - self.plocY) / SMOOTHING
                        
                        # Visual Feedback for Cursor
                        cv2.circle(frame, (cx, cy), 15, (255, 0, 0), 2)
                        cv2.putText(frame, "CURSOR", (cx-30, cy-25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

                        # 2. GESTURE LOGIC
                        if self.get_dist(i_tip, m_tip) < 0.035:
                            diff_y = self.plocY - currY
                            if abs(diff_y) > 3:
                                pyautogui.scroll(int(diff_y * 3))
                                status_msg = "Mouse: Scrolling"
                                action_color = (255, 165, 0) # Orange
                        
                        elif self.get_dist(t_tip, p_tip) < 0.035:
                            if not self.dragging:
                                pyautogui.mouseDown()
                                self.dragging = True
                            pyautogui.moveTo(currX, currY, _pause=False)
                            status_msg = "Mouse: Dragging"
                            action_color = (255, 0, 255) # Magenta
                        
                        else:
                            if self.dragging:
                                pyautogui.mouseUp()
                                self.dragging = False
                            
                            pyautogui.moveTo(currX, currY, _pause=False)
                            status_msg = "Mouse: Cursor Active"
                            
                            # Clicks
                            if self.get_dist(t_tip, i_tip) < 0.03:
                                pyautogui.click()
                                status_msg = "Mouse: Left Click"
                                cv2.waitKey(100)
                            elif self.get_dist(t_tip, m_tip) < 0.03:
                                pyautogui.rightClick()
                                status_msg = "Mouse: Right Click"
                                cv2.waitKey(100)
                            elif self.get_dist(t_tip, r_tip) < 0.03:
                                pyautogui.doubleClick()
                                status_msg = "Mouse: Double Click"
                                cv2.waitKey(200)

                        self.plocX, self.plocY = currX, currY

                    # --- LEFT HAND: SYSTEM CONTROL ---
                    elif label == 'Left':
                        # Brightness & Volume Gauges
                        b_val = np.interp(hand_lms.landmark[9].y, [0.2, 0.8], [100, 0])
                        sbc.set_brightness(int(b_val))
                        self.bright_per = int(b_val)
                        
                        if self.volume:
                            vol_dist = self.get_dist(t_tip, i_tip)
                            v = np.interp(vol_dist, [0.03, 0.2], [self.vol_range[0], self.vol_range[1]])
                            self.volume.SetMasterVolumeLevel(v, None)
                            self.vol_per = int(np.interp(v, [self.vol_range[0], self.vol_range[1]], [0, 100]))
                        
                        status_msg = f"System: Vol {self.vol_per}% | Bright {self.bright_per}%"
                        action_color = (0, 255, 0) # Green

                    self.mp_draw.draw_landmarks(frame, hand_lms, self.mp_hands.HAND_CONNECTIONS)

            # --- HUD OVERLAY ---
            cv2.rectangle(frame, (0, 0), (w, 50), (20, 20, 20), -1)
            cv2.putText(frame, status_msg, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, action_color, 2)
            
            # Show visual bars only when using Left hand
            if status_msg.startswith("System"):
                cv2.rectangle(frame, (50, 150), (85, 400), (50, 50, 50), -1)
                cv2.rectangle(frame, (50, 400 - int(self.vol_per*2.5)), (85, 400), (0, 255, 0), -1)
                cv2.rectangle(frame, (w-85, 150), (w-50, 400), (50, 50, 50), -1)
                cv2.rectangle(frame, (w-85, 400 - int(self.bright_per*2.5)), (w-50, 400), (0, 255, 255), -1)

            cv2.imshow("Gesture Control Engine", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break

        self.cap.release()
        cv2.destroyAllWindows()

# --- NEON GUI ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Neon Gesture Controller Pro")
        self.geometry("550x750")
        self.controller = VirtualController()

        ctk.CTkLabel(self, text="AI GESTURE INTERFACE", font=("Impact", 32), text_color="#00D4FF").pack(pady=30)

        self.tabs = ctk.CTkTabview(self, width=480, height=420, corner_radius=15)
        self.tabs.pack(padx=20, pady=10)
        t1 = self.tabs.add("Right Hand (Mouse)")
        t2 = self.tabs.add("Left Hand (System)")

        # Right Hand Instructions with Cursor
        ctk.CTkLabel(t1, text=(
            "• CURSOR MOVEMENT:\n  Move your Index Finger (Blue Tracking Circle)\n\n"
            "• LEFT CLICK:\n  Pinch Thumb + Index\n\n"
            "• RIGHT CLICK:\n  Pinch Thumb + Middle\n\n"
            "• DOUBLE CLICK:\n  Pinch Thumb + Ring\n\n"
            "• SCROLL:\n  Pinch Index + Middle and move Hand\n\n"
            "• DRAG & DROP:\n  Pinch Thumb + Pinky (Hold to drag)"
        ), justify="left", font=("Consolas", 13)).pack(pady=10, padx=20)
        
        # Left Hand Instructions
        ctk.CTkLabel(t2, text=(
            "• VOLUME CONTROL:\n  Adjust distance between Thumb + Index\n  (Green Gauge will appear)\n\n"
            "• BRIGHTNESS CONTROL:\n  Move Palm Up or Down\n  (Yellow Gauge will appear)\n\n"
            "• NOTE:\n  Left hand actions are isolated and\n  will not move the mouse cursor."
        ), justify="left", font=("Consolas", 13)).pack(pady=20, padx=20)

        self.start_btn = ctk.CTkButton(self, text="ENGAGE ENGINE", height=50, width=300, corner_radius=25,
                                       fg_color="#00D4FF", text_color="black", font=("Arial", 16, "bold"), command=self.start)
        self.start_btn.pack(pady=10)

        self.stop_btn = ctk.CTkButton(self, text="TERMINATE ENGINE", height=50, width=300, corner_radius=25,
                                      fg_color="#dc3545", text_color="white", font=("Arial", 16, "bold"), command=self.stop)
        self.stop_btn.pack(pady=5)

    def start(self):
        if not self.controller.running:
            Thread(target=self.controller.run_logic, daemon=True).start()
            self.start_btn.configure(text="ENGINE ONLINE", state="disabled", fg_color="#1DB954")

    def stop(self):
        self.controller.running = False
        self.start_btn.configure(text="ENGAGE ENGINE", state="normal", fg_color="#00D4FF")

if __name__ == "__main__":
    app = App()
    app.mainloop()