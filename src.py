import cv2
import numpy as np
import pyautogui as pag
import keyboard

# open settingS file contaning basic configs
with open("settings.txt") as f:
    lines = f.readlines()

scaling_factor = int(lines[0].split("=")[-1].strip())                # ratio of object movement to mouse pointer movement
click_threshold = int(lines[1].split("=")[-1].strip())               # threshold of object movement which triggers left mouse click
window = int(lines[2].split("=")[-1].strip())                        # whether to show camera or not
mask_tog = int(lines[3].split("=")[-1].strip())                      # whether to show mask or not

""" 
function description: movement(pos, scale, orientation)
    pos - length of movement
    scale - scaling factor
    orientation - 0 if movement in x direction, 1 if movement in y direction

    function to return value of mouse movement based on object movement
    Also tells whether to move the mouse pointer or to click
    return type: (bool a, integer b):
        bool a tells whether it's a click or not
        integer b tells how much to move the mouse pointer
"""
def movement(pos, scale, orientation):
    if orientation == 1 and pos > click_threshold:          # whether to trigger a click
        return 1, pos
    else:                                                   # or to move the mouse pointer
        if abs(pos) < 5:                                    # don't move on small object movements
            return 0, 0
        elif abs(pos) < 50:                                 # move linearly on relatively smaller movements
            return 0, pos*scale
        elif abs(pos) < click_threshold:                    # move slowly on faster movements
            return 0, pos*scale*0.2
        else:
            return 0, 0                                     # don't move if oject movement > threshold

pag.FAILSAFE = False                                        # don't kill camera if object goes out of frame

colour = [-1]                                               # stores color of object                                

""" 
function description: def rgb_to_hsv(r, g, b)
    r, g, b - RGB values of object

    function to convert RGB value of oject to HSV values
    return type: (integer h):
        hue value for given RGB values
"""
def rgb_to_hsv(r, g, b):   
    r, g, b = r / 255.0, g / 255.0, b / 255.
    cmax = max(r, g, b)                             
    cmin = min(r, g, b)                             
    diff = cmax-cmin                                
    if cmax == cmin:  
        h = 0
    elif cmax == r:  
        h = (60 * ((g - b) / diff) + 360) % 360
    elif cmax == g: 
        h = (60 * ((b - r) / diff) + 120) % 360
    elif cmax == b: 
        h = (60 * ((r - g) / diff) + 240) % 360
    return h/2

""" 
function description: mouseRGB(event,x,y,flags,param)
    event - captures event, should be mouse click
    x - X coordinate of object's centroid
    y - Y coordinate of object's centroid
    flags, param - default parameters for internal usage of function

    function to calculate hue value of object which will be used as mouse pointer
    return type: (NULL)
"""
def mouseRGB(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:                      # checks mouse left button down condition
        colorsB = frame[y,x,0]
        colorsG = frame[y,x,1]
        colorsR = frame[y,x,2]
        colour[0] = rgb_to_hsv(colorsR,colorsG,colorsB)

cv2.namedWindow('mouseRGB')                                 # create a window named mousergb
cv2.setMouseCallback('mouseRGB', mouseRGB)                  # take object color as input in this window

capture= cv2.VideoCapture(0)                                # open camera
kernelOpen=np.ones((5,5))                                   # array to remove noise from other objects of same color
kernelClose=np.ones((20,20))                                # array to join possible holes in the object

centroidOld = [0, 0]                                        # holds previous centroid of object 
centroidNew = [0, 0]                                        # holds current centroid of object
Iterator = [1, 0, 0]                                        # (Entry, Stay, Exit) - boolean variables
take_only_once = 1                                          # bool to decide whether input has been taken or not

bool_hold = 0                                               # bool to check if mouse is down or up

while True:
    ret, frame = capture.read()                             # read frame by frame from camera
    # this ladder decides the range of colours which are acceptable, 
    # which can be considered part of the object,
    # a tolerance calculation:
    if colour[0] <= 15:
        lower_limit = colour[0]*0
        upper_limit = colour[0] + 15
    elif colour[0] >= 165:
        lower_limit = colour[0] - 15
        upper_limit = colour[0]*0 + 179
    else:
        lower_limit = colour[0] - 15
        upper_limit = colour[0] + 15
    
    lowerBound=np.array([lower_limit ,100, 100])
    upperBound=np.array([upper_limit ,255, 255])
    
    if colour[0] == -1:                                     # has the input been taken yet, if not then take the input
        cv2.imshow('mouseRGB', frame)
        font = cv2.FONT_HERSHEY_SIMPLEX  
        org = (50, 50)
        fontScale = 1   
        color = (255, 0, 0)  
        thickness = 2
        frame = cv2.putText(frame, 'Select the object to be used as mouse pointer.', org, font, fontScale, color, thickness, cv2.LINE_AA)

    # if the input has been taken, close the window that takes input
    if colour[0] != -1 and take_only_once == 1:
        take_only_once = 0
        cv2.destroyWindow('mouseRGB')
    
    if cv2.waitKey(1) == ord('q'):
        break
    # if input has been taken, start depicting the object as mouse pointer
    if colour[0] != -1:
        img = frame                                         # give video frame to openCV                       
        imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)       # convert BGR to HSV
        mask=cv2.inRange(imgHSV, lowerBound, upperBound)    # create the Mask
        # reduce noise for other same coloured objects
        maskOpen = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernelOpen)
        # fill holes inside the object
        maskClose = cv2.morphologyEx(maskOpen, cv2.MORPH_CLOSE, kernelClose)
        maskFinal = maskClose         
        # find contours of the object and heirarchy              
        conts, heir = cv2.findContours(maskFinal.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    
        # 
        cv2.drawContours(img,conts,-1,(255,0,0),3)

        x, y, w, h = 0, 0, 0, 0                             # initialize the dimensions of the object

        Iterator[2] = 1
        # iterate over all objects
        for i in range(len(conts)):
            x,y,w,h=cv2.boundingRect(conts[0])              # form a rectangle around the object
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255), 2) # depict on the screen
            # if object enters on screen for first time:
            if Iterator[0] == 1 and Iterator[1] == 0:
                Iterator[0] = 0
                Iterator[1] = 0
                Iterator[2] = 0
            # transition from object enters to object stays
            elif Iterator[0] == 0 and Iterator[1] == 0:
                Iterator[0] = 0
                Iterator[1] = 1
                Iterator[2] = 0
            # object is still on screen 
            elif Iterator[1] == 1:
                Iterator[2] = 0

        # calculate the poistion where mouse pointer has to be moved next
        centroidNew = [int(x)+int(w)/2, int(y)+int(w)/2]

        if Iterator[2]== 1:                                 # if object goes out of screen, don't move the mouse pointer
            centroidNew = [0,0]
            centroidOld = [0,0]
        
        # calculate movement using function defined
        bool_click,movementX = movement((centroidNew[0] - centroidOld[0]), scaling_factor, 0)
        bool_click,movementY = movement((centroidNew[1] - centroidOld[1]), scaling_factor, 1)
        # Object Enters
        if Iterator[0] == 0 and Iterator[1] == 0 and Iterator[2] == 0:           
            pag.moveTo(centroidNew[0] - centroidOld[0], centroidNew[1] - centroidOld[1])
        # Object stays and no click triggered
        if Iterator[1] == 1 and Iterator[2] ==0 and bool_click == 0:                                
            pag.move((-1)*(movementX), movementY)
        # Object stays and left mouse click released
        if Iterator[1] == 1 and Iterator[2] == 0 and bool_click == 1 and bool_hold == 1:                                
            pag.mouseUp()
            bool_hold = 0
        # Object stays and left mouse click held
        elif Iterator[1] == 1 and Iterator[2] == 0 and bool_click == 1 and bool_hold == 0:                                
            pag.mouseDown()
            bool_hold = 1

        centroidOld = centroidNew                           # assign new centroid to old centroid to calculate distance moved 

        if window == 1:                                          # enable user video
            cv2.imshow("cam",img)

        if mask_tog == 1:
            cv2.imshow("Mask_final",maskFinal)
            cv2.imshow("Mask",mask)

        if (keyboard.is_pressed('esc')) :                   # exit condition
            print("exiting loop")
            break

capture.release()                                           # stop video
cv2.destroyAllWindows()                                     # destroy all windows
