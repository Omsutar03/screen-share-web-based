# This file is part of Local Remote.
#
# Local Remote is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Local Remote is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Local Remote. If not, see <https://www.gnu.org/licenses/>.


from flask import Flask, Response, request, session, redirect, url_for
from flask_session import Session
import cv2
import numpy as np
from PIL import ImageGrab
import pyautogui
import json

# Function to load server configuation
def load_configurations():
    # Load server configs
    with open('config/hosting.json', 'r') as file:
        serverConfigs = json.load(file)
    
    return serverConfigs

serverConfigs = load_configurations()

# Flask set-up
app = Flask(__name__)
app.secret_key = serverConfigs['secretKey']  # Replace with a strong secret key. (can be any string)
app.config['SESSION_TYPE'] = 'filesystem'  # Use filesystem-based sessions. This will save session cookies in server directory.
Session(app)

# Load allowed users with their credentials and roles
with open('config/users.json', 'r') as file:
    users = json.load(file)

# Function to capture screen as a frame
def capture_full_screen():
    screenshot = ImageGrab.grab()
    return screenshot

# Function to enerate frames
def generate_frames():
    while True:
        frame = capture_full_screen()
        if frame is None:
            continue

        frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Function to create video feed on web interface
@app.route('/video_feed')
def video_feed():
    if 'username' not in session:
        return redirect(url_for('login'))
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Function for login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            session['username'] = username
            session['role'] = users[username]['role']
            return redirect(url_for('index'))
        else:
            return 'Invalid credentials', 401
    return '''
        <form method="post">
            Username: <input type="text" name="username">
            Password: <input type="password" name="password">
            <input type="submit" value="Login">
        </form>
    '''

# Function for logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))

# Function for html content on web interface
@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    role = session['role']

    # Empty HTML for toggle (if user is not logged in as admin)
    editToggleHtml = ""

    # HTML for toggle (if user is logged in as admin)
    if role == 'admin':
        editToggleHtml = """
        <div class="label">
            <span id="editStatus" style="color: azure;">View-Only</span>
            <label class="switch">
                <input type="checkbox" id="editToggle">
                <span class="slider"></span>
            </label>
        </div>
        """

    return f'''
        <html>
        <head>
            <title>Application Screen Stream</title>
            <style>
                .switch {{
                    position: relative;
                    display: inline-block;
                    width: 52px;
                    height: 16px;
                }}
                .switch input {{ 
                    opacity: 0;
                    width: 0;
                    height: 0;
                }}
                .slider {{
                    position: absolute;
                    cursor: pointer;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background-color: #ccc;
                    transition: .4s;
                    border-radius: 14px;
                }}
                .slider:before {{
                    position: absolute;
                    content: "";
                    height: 8px;
                    width: 8px;
                    border-radius: 50%;
                    left: 4px;
                    bottom: 4px;
                    background-color: white;
                    transition: .4s;
                }}
                input:checked + .slider {{
                    background-color: #068090;
                }}
                input:checked + .slider:before {{
                    transform: translateX(26px);
                }}
                .label {{
                    display: flex;
                    align-items: center;
                    margin-bottom: 10px;
                }}
                .label span {{
                    margin-right: 10px;
                }}
            </style>
            <script>
                let isEditing = false;
                let videoWidth = 0;
                let videoHeight = 0;

                function toggleEditMode() {{
                    isEditing = !isEditing;
                    document.getElementById("editStatus").innerText = isEditing ? "Edit Mode" : "View-Only";
                }}

                function sendMouseClick(event) {{
                    if (isEditing) {{
                        const rect = event.target.getBoundingClientRect();
                        const x = event.clientX - rect.left;
                        const y = event.clientY - rect.top;
                        fetch(`/mouse_click?x=${{x}}&y=${{y}}&video_width=${{videoWidth}}&video_height=${{videoHeight}}`, {{ method: 'POST' }});
                    }}
                }}

                function sendKeyboardInput(event) {{
                    if (isEditing) {{
                        const key = event.key;
                        fetch(`/keyboard_input?key=${{key}}`, {{ method: 'POST' }});
                    }}
                }}

                function setVideoDimensions() {{
                    const video = document.getElementById('stream');
                    videoWidth = video.clientWidth;
                    videoHeight = video.clientHeight;
                }}

                function forceLogout() {{
                    fetch('/logout', {{ method: 'GET' }}).then(() => {{
                        window.location.reload(true); // Force reload without cache to trigger reauthentication
                    }});
                }}

                window.onload = () => {{
                    document.getElementById('editToggle').addEventListener('change', toggleEditMode);
                    document.getElementById('stream').addEventListener('click', sendMouseClick);
                    document.addEventListener('keydown', sendKeyboardInput);
                    setVideoDimensions();
                    window.addEventListener('resize', setVideoDimensions);
                    
                    // Force logout on page reload
                    window.addEventListener('beforeunload', forceLogout);
                }}
            </script>
        </head>
        <body style="background-color: rgb(31, 31, 31);">
            <img id="stream" src="/video_feed" width="100%" />
            {editToggleHtml}
            <a href="/logout" style="color: #fff;">Logout</a>
        </body>
        </html>
    '''

# Function to simulate mouse clicks
@app.route('/mouse_click', methods=['POST'])
def mouse_click():
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        x = float(request.args.get('x'))
        y = float(request.args.get('y'))
        video_width = float(request.args.get('video_width'))
        video_height = float(request.args.get('video_height'))

        # Get the full screen resolution
        screen_width, screen_height = pyautogui.size()

        # Calculate scaling factors
        scale_x = screen_width / video_width
        scale_y = screen_height / video_height

        # Adjust the coordinates based on the scaling factors
        x = int(x * scale_x)
        y = int(y * scale_y)

        pyautogui.click(x, y)  # Perform the click on full screen
    except ValueError as e:
        print(f"Error converting coordinates: {e}")
    return '', 204

# Function to simulate keyboard inputs
@app.route('/keyboard_input', methods=['POST'])
def keyboard_input():
    if 'username' not in session:
        return redirect(url_for('login'))

    key = request.args.get('key')
    
    # Simulate input
    pyautogui.press(key)
    return '', 204

if __name__ == '__main__':
    # Load server configs
    serverConfigs = load_configurations()

    # Hosting server locally on port defined in server configs
    app.run(host='0.0.0.0', port=serverConfigs['hostingPort'])
