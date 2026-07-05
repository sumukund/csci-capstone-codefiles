# [Project Name]

Embodied Geography: dancer tracking files
---

## 💡 Overview

This system exploits the capabilities of the ZED Mini Stereo Camera to respond to the dancer in real-time as they traverse the space. This involves tracking position, calculating intersections of the dancer with our defined points, and tracking gesture and movement.
### Key Features

To determine the usefulness and usability of the camera for real-time position tracking, we defined initial parameters for the camera:
• Resolution: 1080 pixels
• Depth Mode: Neural
• Camera FPS: 60 FPS
• Detection Model: Human Body Accurate
Once a skeleton was detected we collected the following data:
• Position: Provides the 3D position of the object according to the camera as a 3D vector (x,y,z)
• Velocity: Provides the instantaneous velocity of the object in space as a 3D vector (x,y,z)
• Keypoints: Head Keypoint (26)
• Keypoints: Right Wrist: (15)
• Keypoints: Left Wrist: (8)
---

## 🛠️ Tech Stack

* **Language:** [ Python, OSC, MaxMSP ]

---

## 🚀 Getting Started

Follow these steps to get a local copy of the project up and running.

### Prerequisites


To run ZED camera software, follow the instructions to setup the ZED SDK: 

https://docs.stereolabs.com/docs/development/zed-sdk/windows

Then, get the API like this: 

https://docs.stereolabs.com/docs/development/api-languages/python

Then you can continue on and run the requirements and program. 


### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/sumukund/csci-capstone-codefiles.git
   cd csci-capstone-codefiles
   pip3 install -r requirements.txt
   ```

### Running the Application
To start the local development server:
```
py 
```
The application will start running..

---

## ✉️ Contact

* **Project Maintainer:** Sudarsna Mukund
* **Email:** mukun017@umn.edu
* **Project Link:** [https://github.com/sumukund/csci-capstone-codefiles](https://github.com/sumukund/csci-capstone-codefiles)