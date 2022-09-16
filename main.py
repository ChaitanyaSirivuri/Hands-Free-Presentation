from turtle import goto
from cvzone.HandTrackingModule import HandDetector
import cv2
import os
import numpy as np

# Guide to use the application:
# Advance to line 161

# Presentation window dimensions
winWidth, winHeight = 1280, 720


# Initialize camera
capture = cv2.VideoCapture(0)
capture.set(3, winWidth)
capture.set(4, winHeight)

# Set up hand detector
detection = HandDetector(detectionCon=0.8, maxHands=1)

# List of all slides and slide pointer
slidesList = []
slideNumber = 0

# flag for the action occurrence
flag = False
flagCounter = 0

# Draw the canvas on slides
drawMode = False
draw = [[]]
drawNumber = -1
initialDraw = False  # flag for the first draw


# sub-window dimensions
height, width = int(120 * 2), int(213 * 2)

# Access all the slides in the folder
slides = os.listdir("slides")


while True:

    # load the slides
    hit, slide = capture.read()
    slide = cv2.flip(slide, 1)
    # join all the slides for the presentation
    presentation = os.path.join("slides", slides[slideNumber])
    currentSlide = cv2.imread(presentation)  # read the slides

    # Detect the hands landmarks
    hands, slide = detection.findHands(slide)

    # Draw Gesture Threshold line for necessary gestures
    cv2.line(slide, (0, 300),
             (winWidth, 300), (0, 255, 0), 10)

    # If system detects a hand
    if hands and flag is False:

        hand = hands[0]
        cx, cy = hand["center"]
        lmList = hand["lmList"]  # List of 21 Landmark points
        fingers = detection.fingersUp(hand)  # List of fingers that are up

        # 8 represents the index finger
        xVal = int(np.interp(lmList[8][0], [0, winWidth], [0, winWidth]))
        yVal = int(np.interp(lmList[8][1], [0, winHeight], [0, winHeight]))
        indexFinger = xVal, yVal

        if cy <= 300:  # If the hand is in the threshold line

            # If the Thumb finger is up
            # Gesture 1: Traverse to previous slide
            if fingers == [1, 0, 0, 0, 0]:
                flag = True
                if slideNumber > 0:
                    slideNumber -= 1
                    draw = [[]]
                    drawNumber = -1
                    initialDraw = False

            # If the pinky is up
            # Gesture 2: Traverse to next slide
            if fingers == [0, 0, 0, 0, 1]:
                flag = True
                if slideNumber < len(slides) - 1:
                    slideNumber += 1
                    draw = [[]]
                    drawNumber = -1
                    initialDraw = False

        # If the index finger is up
        # Gesture 3: pointer on the slide
        if fingers == [0, 1, 0, 0, 0]:
            cv2.circle(currentSlide, indexFinger, 12, (0, 0, 255), cv2.FILLED)

        # If both the index and middle fingers are up
        # Gesture 4: Draw on the slide
        if fingers == [0, 1, 1, 0, 0]:
            if initialDraw is False:
                initialDraw = True
                drawNumber += 1
                draw.append([])
            draw[drawNumber].append(indexFinger)
            cv2.circle(currentSlide, indexFinger, 12, (0, 0, 255), cv2.FILLED)

        else:
            initialDraw = False

        # If Index, middle and ring fingers are up
        # Gesture 5: undo the last draw
        if fingers == [0, 1, 1, 1, 0]:
            if draw:
                draw.pop(-1)
                drawNumber -= 1
                flag = True

        # If all the fingers are up
        # Gesture 6: clear the drawing
        if fingers == [1, 1, 1, 1, 1]:
            draw = [[]]
            drawNumber = -1
            initialDraw = False
    else:
        initialDraw = False

    # Check if the slide has traversed forward or backward
    if flag:
        flagCounter += 1
        if flagCounter > 10:
            flagCounter = 0
            flag = False

    # Draw the drawing on the slide
    for i, annotation in enumerate(draw):
        for j in range(len(annotation)):
            if j != 0:
                cv2.line(currentSlide, annotation[j - 1],
                         annotation[j], (0, 0, 200), 12)

    # Join the video and presentation window
    slideSmall = cv2.resize(slide, (width, height))
    joinHeight, joinWidth, _ = currentSlide.shape
    currentSlide[0:height, joinWidth - width: joinWidth] = slideSmall

    # Display the window
    cv2.imshow("Slides", currentSlide)

    # Press q to quit
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

# Release the camera and destroy all the windows
capture.release()
cv2.destroyAllWindows()

# Guide to use the application
# Guide to use the application
# 1. Use the index finger to point on the slide
# 2. Use the index and middle finger to draw on the slide
# 3. Use the index, middle and ring finger to undo the last draw
# 4. Use all the fingers to clear the drawing
# 5. Use the thumb finger to traverse to previous slide
# 6. Use the pinky to traverse to next slide
