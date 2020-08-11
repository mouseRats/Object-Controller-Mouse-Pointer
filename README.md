# Object Controlled Mouse Pointer

With the increasing usage of computers in day to day life, we are moving to an age where there is a need to control a computer interface using only one's hands. This project allows a user to control the cursor on their computer using a coloured object.

# How to Run the Code
To run the code, make sure the webcam isn't being used anywhere else. To run, use the following command:

> python src.py


## Required Libraries
The code has been written in Python3.

 - PyAutoGUI
 - Keyboard
 - OpenCV
 - Numpy

To install the libraries, use "pip install -r requirements.txt"

## Configuration Files
 - Settings.txt -- Modify this file for customization.
	 - Contains the parameters for the execution of the script.
	 - The sensitivity is the sensitivity of the mouse. Basically a scaling factor. Increase it to increase sensitivity (Default 2)
	 - The click_threshold is the distance the mouse has to travel to interpret it as a click. (Default 100)
	 - The window_toggle variable is a Boolean variable which keeps the user video window on or off while the script is running. (Default 1)
	 - The mask_toggle variable is a Boolean variable which keeps the user object mask visible or not while script is running. (Default 1)

## Working of the Script

 - The script automatically imports settings.txt.
 - Once the script is executed, a window will open which will take the webcam video from the user.
 - In this video, the user must click on the object which the script should track. Ensure there aren't any other objects of a similar colour in the background.
 - Object will be masked to remove noies from background and fill holes in the object.
 - Once the object has been selected, the window will close. If the window variable from the settings.txt file is 1, the video will remain on.
 - The script will now track the object as it moves.
 - For very small movement, the cursor will remain stationary.
 - For moderate movement, the cursor will move in the direction the object is moved in.
 - For large movements, the cursor remains stationary.
 - A sudden downward movement above the threshold value will trigger a MouseDown (like holding left mouse button). This threshold value is determined by click_threshold from the settings.txt file.
 - A second sudden downward movement above the threshold value will trigger a MouseUp (like releasing the left mouse button).
 - So for clicking, 2 sudden downward movements are required.
 - At any point of time, to exit and close the script, press the 'ESC' key on the keyboard.

## Future Aspects

 - Improving stability and making the movement smoother.
 - Detection of multiple colours - one for movement, one for left click, one for right click etc.
 - Instead of clicking on the object, a box will be displayed. By placing an object in the box, the script will begin to track the object.
 - Implementing finger detection and gesture detection.
 - Upgrading the model to use sensors like accelerometer, gyrometer to obtain the orientation and movement of the hand.
