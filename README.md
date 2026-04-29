# CattleAI

## Overview

CattleAI is an AI-powered web application that identifies cattle breeds from images and provides detailed breed information along with multilingual voice output.

The system supports detection of **39 cattle breeds** and is designed for ease of use in agricultural and rural environments.

## Key Features

* Image-based cattle breed recognition using deep learning
* Supports **39 different cattle breeds**
* Displays breed-specific information (stored and structured efficiently)
* Maintains scan history using JSON-based storage
* Multilingual voice output for accessibility (e.g., Malayalam & English)
* Simple and responsive web interface

## Tech Stack

* **Frontend:** HTML, CSS, JavaScript, Bootstrap
* **Backend:** Python (Flask)
* **Model:** YOLOv8 (Ultralytics)
* **Data Handling:** Python dictionaries + JSON storage
* **Audio:** Text-to-speech for multilingual output

## How It Works

1. User uploads an image or uses live detection
2. Model identifies the cattle breed
3. System retrieves breed information
4. Displays results + generates voice output

## Applications

* Farmers and livestock owners
* Veterinary support systems
* Educational and agricultural tools

## Future Scope

* Mobile app integration
* Cloud deployment
* Expanded breed dataset
* Improved accuracy with larger training data

