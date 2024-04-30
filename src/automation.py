import time
import pyautogui
import cv2 
import os
global template_path
template_path = os.path.abspath("../images")

def locateArrowOnScreen(gui):
    """
    Returns:
        tuple: If found, returns the center coordinates of the right arrow button.\n
                  If not found, prompts the user to confirm the location and returns
                       the confirmed coordinates.
    """
    try:
        right_arrow_templates = ["rightAW/rightA(1).png", "rightAW/rightA(2).png","rightAW/rightA(3).png","rightAW/rightA(4).png"]
        for template in right_arrow_templates:
            # Join the directory path and the template filename
            arrow_path = os.path.join(template_path, template)
            rightarrowButtonLocation = pyautogui.locateCenterOnScreen(arrow_path, confidence=0.6)
            if rightarrowButtonLocation:
                break
        #print(captureButtonLocation, " ", rightarrowButtonLocation)
        return rightarrowButtonLocation
    except pyautogui.ImageNotFoundException:
        print("Arrow not found")
        rightarrowButtonLocation = gui.get_user_confirmed_position("Right Arrow")
        return rightarrowButtonLocation
    
def locateButtonOnScreen(gui):
    """
    Returns:
        tuple: If found, returns the coordinates and dimensions of the capture button.
                  If not found, prompts the user to confirm the location and returns
               the confirmed coordinates and default dimensions.
    """
    try:
        captureButtonLocation = pyautogui.locateOnScreen("../images/capture.png", confidence=0.6)
        return captureButtonLocation
    except pyautogui.ImageNotFoundException:
        print("Button not found")
        width, height = 90, 30
        x, y = gui.get_user_confirmed_position("Capture Button")
        return x, y, width, height

#take screenshot of the Capture button and save
def take_screenshot(left, top, width, height):
    button_screenshot = pyautogui.screenshot(region=(int(left), int(top), int(width), int(height)))
    button_screenshot.save("../images/button_screenshot.png")

#Detect the button color by converting to grayscale and comparing each pixel
def detect_button_color(button_image):
    img = cv2.imread(button_image)
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)     # Convert image to grayscale
        
    # threshold ranges for yellow and white
    yellow_lower, yellow_upper= 100, 200
    white_lower, white_upper = 200, 255
    yellow_count = 0
    white_count = 0
        
    # Iterate through each pixel in the grayscale image
    for row in gray_image:
        for pixel_value in row:
            if yellow_lower <= pixel_value <= yellow_upper:
                yellow_count += 1
            elif white_lower <= pixel_value <= white_upper:
                white_count += 1
        
    #print(f"yellow {yellow_count},white {white_count}")
    # Determine predominant color based on pixel counts
    if yellow_count > white_count:
        return True
    elif white_count > yellow_count:
        return False

#get Coordinates of the button and arrow, and return them
def get_coordinates(gui, stop_event):
    check_stop_event(stop_event)

    captureButtonLocation = locateButtonOnScreen(gui)
    rightarrowButtonLocation = locateArrowOnScreen(gui)   

    if captureButtonLocation and rightarrowButtonLocation:
        left, top, width, height = captureButtonLocation                    #Extract the region coordinates
        take_screenshot(left, top, width, height)       #Screen_shot and save function called
        #print(left, top, width, height)
        x = left + (width / 2)
        y = top + (height / 2)
        return rightarrowButtonLocation, left, top, width, height, x, y
    
    return None, None, None, None, None, None, None

def automation_sequence(gui, total_photos, stop_event):
    """
    Automate the process of capturing photos and navigating to the next location.

    This function is the main automation sequence that performs the following steps:
    1. Locate the capture button and right arrow button on the screen.
    2. For the specified number of photos:\n
        a. Move the cursor to the capture button and click it.\n
        b. Move the cursor to the right arrow button and click it.\n
        c. Wait for the button color to change.\n
        d. Update the GUI with the number of photos captured.\n
    3. If the stop event is set or a timeout occurs while waiting for the button color change,
       stop the automation sequence.

    Args:
        gui (WindowsGui): The instance of the WindowsGui class.
        total_photos (int): The total number of photos to capture.
        stop_event (threading.Event): An event object used to signal the automation sequence to stop.

    Returns:
        None
    """

    time.sleep(1.5)
    try:
        rightarrowButtonLocation, left, top, width, height, x, y = get_coordinates(gui, stop_event)
    except StopAutomationException:
        return

    for i in range(total_photos): 
        check_stop_event(stop_event)

        pyautogui.moveTo(x,y, 1)            #move the cursor to Capture Button in 1 s
        pyautogui.click()
        pyautogui.moveTo(rightarrowButtonLocation.x,rightarrowButtonLocation.y, 1)
        pyautogui.click()
        print(f"{i} photo captured")
        gui.photos_taken += 1  # Increment by one or actual number of photos taken
        gui.update_status()

        # Wait for button color to change with a timeout
        timeout = 90  # seconds
        check_interval = 3  # seconds
        elapsed_time = 0
        button_color_changed = False

        while not button_color_changed and elapsed_time < timeout:
            time.sleep(check_interval)
            elapsed_time += check_interval
            print(elapsed_time)
            check_stop_event(stop_event)

            take_screenshot(left, top, width, height)
            button_path = os.path.join(template_path, "button_screenshot.png")
            button_color_changed = detect_button_color(button_path)
            
        if elapsed_time > timeout:
            print("Time Out")
            time.sleep(3)

def check_stop_event(stop_event):
    if stop_event.is_set():
        print("Stopping automation immediately...")
        pyautogui.alert(text='Stopping automation immediately', title='Notice', button='OK')
        raise StopAutomationException  

class StopAutomationException(Exception):
    pass

