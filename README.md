# Local Remote
## Overview
Local Remote is open-source application built in Python, designed to provide an easy and efficient way to share your screen with others on local network and give remote access in real-time. **The advantage of Local Remote is that only the host machine need to install application, other can access the screen by simply entering host machine's IP on browser with specified port (default: 756)**. The application is ideal for remote collaboration, presentations, or troubleshooting.

## Features
1. Application needs to be installed on only host machine. No need for remote machines to have application installed.
2. User based login. (Only users with in-app admin rights can have remote access)

## Installation
You can find the Local Remote installer in releases tab. Simply install the application using installer.


## Usage
Simply start the application by clicking the application icon on desktop.

>You can change the port on which application stream by accessing "hosting.json" file in "C:/Program files/Local Remote/config".
>
>You can add more users by accessing "users.json" file in "C:/Program files/Local Remote/config".

Application runs in the background without any GUI. To close the application simply end the application from Task Manager.

There are 2 profiles setup by default.
1. Administrator: Username = admin, Password = admin
2. User1: Username = user1, Password = user1

## License
This project is licensed under the GNU General Public License v3.0. See the LICENSE file for more details.

## Contact
For any questions or support, feel free to contact the project maintainer:
* Email: omsutar03@gmail.com
* GitHub: https://github.com/Omsutar03

>**Firewall and Antivirus Notice:** You may need to allow the application through your firewall or antivirus software, as it requires network permissions for screen sharing.

