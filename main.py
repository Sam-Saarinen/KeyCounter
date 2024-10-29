import tkinter as tk
from pynput import keyboard
import threading
import win32gui
import win32con
import pystray
from PIL import Image, ImageDraw

# Set up tkinter window
window = tk.Tk()
window.title("Character Counter Overlay")
window.geometry("200x100")

# Remove window decorations, set on top, and add transparency
window.overrideredirect(True)
window.attributes('-topmost', True)
window.attributes('-alpha', 0.7)  # 70% opaque

label = tk.Label(window, text="0", font=("Segoe UI", 16, "bold"), fg='#FFFFFF', bg='#000080', padx=15, pady=5)
label.pack(fill='both', expand=True)

# Function to make window click-through
def make_click_through():
    hwnd = win32gui.FindWindow(None, "Character Counter Overlay")
    styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, styles | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)

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

# Function to handle system tray icon
def create_tray_icon():
    # Create an icon image
    icon_image = Image.new('RGB', (64, 64), color='#000080')
    dc = ImageDraw.Draw(icon_image)
    dc.text((10, 20), "CC", fill='white')  # 'CC' stands for "Character Counter"

    # Function to close the overlay and exit
    def close_overlay(icon, item):
        # Immediately destroy the tkinter window and stop the tray icon
        icon.stop()
        window.quit()
        window.destroy()  # This will immediately close the overlay

    # Define the tray icon menu
    menu = pystray.Menu(
        pystray.MenuItem("Exit", close_overlay)
    )

    # Create and run the tray icon
    icon = pystray.Icon("character_counter", icon_image, "Character Counter", menu)
    icon.run()

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
