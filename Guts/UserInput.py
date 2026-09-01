"""
8 - 8 - 26 

This class holds every listener and handler for user input.

"""

import cv2
import time


class UserInput: 

    



    def screenshot_selection(): 

        top_left_corner = []
        bottom_right_corner = []
        rectDrawn = False
        image = cv2.imread(rf"C:\Users\adria\OneDrive\Documents\Coding\Python\Big Projects\Documentation Automater\Documentation-Automer-\Screenshots\waldo.png")
        tempImage = image.copy()

        # function which will be called on mouse input
        def drawRectangle(action, x, y, flags, *userdata):
        # Referencing nonlocal variables; making them accesible inside this function
            nonlocal rectDrawn, top_left_corner, bottom_right_corner

        # Mark the top left corner when left mouse button is pressed
            if rectDrawn == False and action == cv2.EVENT_LBUTTONDOWN:
                top_left_corner = [(x,y)]
                # When left mouse button is released, mark bottom right corner
            elif rectDrawn == False and action == cv2.EVENT_LBUTTONUP:
                rectDrawn = True
                bottom_right_corner = [(x,y)]   
                # Draw the rectangle; it applies the drawing to the image IN MEMORY; changes not seen because changed image not yet uploaded
                # to window.
                cv2.rectangle(image, top_left_corner[0], bottom_right_corner[0], (0,255,0),2, 8)
                # Window is recreated and new changed image is uploaded into it and therefore displayed on screen.
                cv2.imshow("Window",image)

        def window_creation(): 
            # Creating the Window the screenshot sits in. 
            cv2.namedWindow("Window", cv2.WINDOW_NORMAL) # cv2.WINDOW_NORMAL allows the window to be resizable
            # Setting the window's size to full screen. 
            cv2.setWindowProperty("Window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        def mouse_listener(): 
            # Starts listener for left button mouse press and release; calls 'drawRectangle()' when event detected
            cv2.setMouseCallback("Window", drawRectangle)

        window_creation()
        mouse_listener()

        k=0
        increment = 0
        # After all above stuff has been loaded into memory, we jump into while loop to get program running.
        while k!=113: #q quits the loop and the program
            
            # Actually running/showing/opening the Window we created; this is when the window is FIRST opened.
            cv2.imshow("Window", image)
            k = cv2.waitKey(0) # Stops loop and listens for key presses INSIDE THE WINDOW. 
            # Mouse listener is not stopped and is still listening.

            # Allows user to wipe their selection and making a new one if a mistake was made
            if (k == 99): #c replaces original image w/ copy, "wiping" the board clean
                rectDrawn = False
                image = tempImage.copy() # Must be COPY because it willl only clear one time if not 
                cv2.imshow("Window", image)

            if (k == 115): # 's' saves screenshot selection
                increment += 1
                x1, y1 = top_left_corner[0]
                x2, y2 = bottom_right_corner[0]

                cv2.imwrite(rf"C:\Users\adria\OneDrive\Documents\Coding\Python\Big Projects\Documentation Automater\Screenshots\screenshot_{increment}.png",
                                tempImage[min(y1,y2):max(y1,y2), min(x1,x2):max(x1,x2)]
                                    )
                print(f'Saved screenshot selection {increment}')

                # Allows user to take a multiple screenshots; wipes/resets image after 
                # screenshot is saved
                time.sleep(0.5) # slight wait before wiping and resetting the screenshot
                rectDrawn = False 
                image = tempImage.copy()
                cv2.imshow("Window", image)
        
        cv2.destroyAllWindows()

UserInput.screenshot_selection()

            
