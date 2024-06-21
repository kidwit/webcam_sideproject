import cv2
import numpy as np
import speech_recognition as sr
import threading

# Initialize the recognizer
recognizer = sr.Recognizer()

# Function to capture audio and transcribe to text
def listen_and_transcribe():
    global text
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)  # Increase timeout and phrase_time_limit
            text = recognizer.recognize_google(audio)
            print(f"Recognized: {text}")
        except sr.WaitTimeoutError:
            text = "Probably hasn't said anything tbh"
            print(text)
        except sr.UnknownValueError:
            text = "Isnt saying anything"
            print(text)
        except sr.RequestError:
            text = "Google Speech Recognition service error"
            print(text)
        except Exception as e:
            text = f"Error: {str(e)}"
            print(text)

# Initialize the webcam
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Use DirectShow backend for Windows
cap.set(cv2.CAP_PROP_FPS, 30)  # Limit FPS to reduce load
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Lower resolution
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("Error: Could not open the webcam.")
    exit()

# Initialize text for overlay
text = ""

# Run speech recognition in a separate thread
def recognize_speech():
    while True:
        listen_and_transcribe()

speech_thread = threading.Thread(target=recognize_speech, daemon=True)
speech_thread.start()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break

    # Define font and position for text
    font = cv2.FONT_HERSHEY_SIMPLEX
    bottom_left_corner_of_text = (10, frame.shape[0] - 10)
    font_scale = 1
    font_color = (0, 215, 255)  # Gold in BGR format
    line_type = 2

    # Add a background rectangle for better readability
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, line_type)
    cv2.rectangle(frame, (bottom_left_corner_of_text[0], bottom_left_corner_of_text[1] - text_height - baseline),
                  (bottom_left_corner_of_text[0] + text_width, bottom_left_corner_of_text[1]), (0, 0, 0), -1)

    # Overlay the text onto the frame
    cv2.putText(frame, text, bottom_left_corner_of_text, font, font_scale, font_color, line_type)

    # Display the resulting frame
    cv2.imshow('Webcam Feed with Speech-to-Text', frame)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close windows
cap.release()
cv2.destroyAllWindows()
