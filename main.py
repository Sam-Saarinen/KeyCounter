import tkinter as tk
from pynput import keyboard
import threading
import win32gui
import win32con
import pystray
from PIL import Image, ImageDraw
import json
import os

# Constants
WINDOW_TITLE = "Character Counter Overlay"
WINDOW_WIDTH = 150
WINDOW_HEIGHT = 50
DEFAULT_OFFSET_X = 20  # Offset from right edge
DEFAULT_OFFSET_Y = 60  # Offset from bottom edge to be above the taskbar
OPACITY_SEMI_TRANSPARENT = 0.7
OPACITY_FULL = 1.0
POSITION_FILE_NAME = "key_counter.json"
LABEL_FONT = ("Segoe UI", 16, "bold")
LABEL_FG_COLOR = '#FFFFFF'
LABEL_BG_COLOR = '#000080'

# Set up tkinter window
window = tk.Tk()
window.title(WINDOW_TITLE)

# Load position from JSON file if available
def load_position():
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    position_file = os.path.join(desktop_path, POSITION_FILE_NAME)
    if os.path.exists(position_file):
        try:
            with open(position_file, "r") as f:
                data = json.load(f)
                return data.get("x", None), data.get("y", None)
        except Exception as e:
            print(f"Error loading position: {e}")
    return None, None

# Calculate default position to be in the bottom-right corner, just above the taskbar
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
default_position = (screen_width - WINDOW_WIDTH - DEFAULT_OFFSET_X, screen_height - WINDOW_HEIGHT - DEFAULT_OFFSET_Y)

# Set window position based on saved position or default position
saved_x, saved_y = load_position()
if saved_x is not None and saved_y is not None:
    window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{saved_x}+{saved_y}")
else:
    window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{default_position[0]}+{default_position[1]}")

# Remove window decorations, set on top, and add transparency
window.overrideredirect(True)
window.attributes('-topmost', True)
window.attributes('-alpha', OPACITY_SEMI_TRANSPARENT)

label = tk.Label(window, text="0", font=LABEL_FONT, fg=LABEL_FG_COLOR, bg=LABEL_BG_COLOR, padx=15, pady=5)
label.pack(fill='both', expand=True)

# Keep track of whether repositioning is enabled
repositioning_enabled = False

# Mouse event handlers for dragging the window
drag_data = {"x": 0, "y": 0}

def start_move(event):
    if repositioning_enabled:
        drag_data["x"] = event.x
        drag_data["y"] = event.y

def on_motion(event):
    if repositioning_enabled:
        x = window.winfo_x() - drag_data["x"] + event.x
        y = window.winfo_y() - drag_data["y"] + event.y
        window.geometry(f"+{x}+{y}")

# Function to save the current position to a JSON file
def save_position():
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    position_file = os.path.join(desktop_path, POSITION_FILE_NAME)
    position_data = {
        "x": window.winfo_x(),
        "y": window.winfo_y()
    }
    try:
        with open(position_file, "w") as f:
            json.dump(position_data, f)
    except Exception as e:
        print(f"Error saving position: {e}")

# Bind mouse events to the label for repositioning
label.bind("<Button-1>", start_move)
label.bind("<B1-Motion>", on_motion)

# Function to make window click-through
def make_click_through():
    hwnd = win32gui.FindWindow(None, WINDOW_TITLE)
    styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, styles | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)

# Function to disable click-through (e.g., for interaction)
def disable_click_through():
    hwnd = win32gui.FindWindow(None, WINDOW_TITLE)
    styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    # Remove the WS_EX_TRANSPARENT style to make it clickable
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, styles & ~win32con.WS_EX_TRANSPARENT)

# Function to start the global key listener
def start_key_listener():
    def on_press(key):
        window.after(0, on_key_press)  # Ensure key presses are handled on the main thread
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

# Function to increment character count
def on_key_press():
    label['text'] = str(int(label['text']) + 1)
    window.update_idletasks()

# System tray control logic
tray_icon = None

# Function to generate the tray menu
def generate_tray_menu():
    menu_items = []
    if repositioning_enabled:
        menu_items.append(pystray.MenuItem("Fix Positioning", fix_position))
    else:
        menu_items.append(pystray.MenuItem("Enable Repositioning", enable_repositioning))
        if (window.winfo_x(), window.winfo_y()) != default_position:
            menu_items.append(pystray.MenuItem("Reset Position", reset_position))
    menu_items.append(pystray.MenuItem("Exit", close_overlay))
    return pystray.Menu(*menu_items)

# Function to create the tray icon
def create_tray_icon():
    global tray_icon

    # Create an icon image
    icon_image = Image.new('RGB', (64, 64), color='#000080')
    dc = ImageDraw.Draw(icon_image)
    dc.text((10, 20), "CC", fill='white')  # 'CC' stands for "Character Counter"

    # Create and run the tray icon
    tray_icon = pystray.Icon("character_counter", icon_image, "Character Counter", generate_tray_menu())
    tray_icon.run()

# Function to update the tray icon menu dynamically
def update_tray_icon_menu():
    global tray_icon
    tray_icon.menu = generate_tray_menu()
    tray_icon.update_menu()

# System tray menu item callbacks
def enable_repositioning(icon, item):
    global repositioning_enabled
    repositioning_enabled = True
    disable_click_through()
    window.attributes('-alpha', OPACITY_FULL)
    update_tray_icon_menu()

def fix_position(icon, item):
    global repositioning_enabled
    repositioning_enabled = False
    make_click_through()
    window.attributes('-alpha', OPACITY_SEMI_TRANSPARENT)
    save_position()  # Save position when fixing it
    update_tray_icon_menu()

def reset_position(icon, item):
    window.geometry(f"+{default_position[0]}+{default_position[1]}")
    save_position()  # Save the reset position
    update_tray_icon_menu()

def close_overlay(icon, item):
    icon.stop()
    window.quit()
    window.destroy()  # This will immediately close the overlay

# Start the key listener in a separate thread to avoid blocking tkinter's event loop
listener_thread = threading.Thread(target=start_key_listener, daemon=True)
listener_thread.start()

# Make window click-through after a short delay to ensure it's properly initialized
window.after(100, make_click_through)

# Start the system tray icon in a separate thread to avoid blocking the main loop
tray_thread = threading.Thread(target=create_tray_icon, daemon=True)
tray_thread.start()

# Run the tkinter main loop
window.mainloop()
