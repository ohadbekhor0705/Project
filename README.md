# SkyVault — Secure Cloud Storage

Lightweight Python client/server for secure file storage with a simple Tkinter GUI.

## Features
- User auth (register/login)  
- Upload/download over TCP sockets  
- Basic transfer encryption  
- Tkinter GUI

## Structure
```
Project/
├── CClientBL.py
├── CServerBL.py
├── StorageGUI.py
├── requirements.txt
├── GUIDesign.PNG
└── README.md
```

## Install
```bash
git clone https://github.com/ohadbekhor0705/Project.git
cd Project
pip install -r requirements.txt
```

## Run
Start server:
```bash
python CServerBL.py
```
Start client:
```bash
python StorageGUI.py
```

## Tech
Python 3.x, tkinter, TCP sockets.

## Author
Ohad Bekhor
