# KeyCounter
A python script for overlaying a cumulative "keys pressed" counter. Intended as a simple abstract productivity metric. Assumes Windows-based environment.

The overlay comes with a system tray icon that can be used to reposition (by dragging) the overlay, or to exit the program. As of right now, the program resets the count whenever it's closed. The number isn't guaranteed to display well past 10^6 key presses.

## Usage:
1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the environment:
   - Windows: `venv\Scripts\activate`
   - Unix: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`

Alternatively, just use the uploaded .exe, which was created using `pyinstaller --onefile --windowed main.py`.
