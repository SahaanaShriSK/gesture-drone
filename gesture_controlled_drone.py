import cv2 
import mediapipe as mp 
import socket 
import time 
 
# Initialize MediaPipe Hands for gesture recognition 
mp_hands = mp.solutions.hands 
mp_drawing = mp.solutions.drawing_utils 
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7) 
 
# Drone IP and Port (adjust based on E88 settings) 
DRONE_IP = "192.168.4.153"  # Replace with your drone's IP 
DRONE_PORT = 5007        # Replace with your drone's control port 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
 
# Define gesture commands for index finger 
gesture_commands = { 
    "move_up": "move_up",        # Index finger moving up 
    "move_down": "move_down",    # Index finger moving down 
    "move_left": "move_left",    # Index finger moving left 
    "move_right": "move_right",  # Index finger moving right 
    "hover": "hover"             # Index finger idle 
} 

# Send command to the drone 
def send_command(command): 
    try: 
        print(f"Sending command: {command}") 
        sock.sendto(command.encode(), (DRONE_IP, DRONE_PORT)) 
        time.sleep(0.1)  # Avoid sending commands too quickly 
    except socket.error as e: 
        print(f"Socket error: {e}") 
 
# Detect index finger gesture based on landmarks 
def recognize_index_finger_gesture(landmarks): 
    if not landmarks or len(landmarks) < 21:  # MediaPipe detects 21 landmarks 
        return "hover" 
 
    # Tip and MCP (base) positions of the index finger 
    index_tip = landmarks[8] 
    index_base = landmarks[5] 
 
    # Direction detection logic 
    if index_tip.y < index_base.y - 0.05:  # Moving up 
        return "move_up" 
    elif index_tip.y > index_base.y + 0.05:  # Moving down 
        return "move_down" 
    elif index_tip.x < index_base.x - 0.05:  # Moving left 
        return "move_left" 
    elif index_tip.x > index_base.x + 0.05:  # Moving right 
        return "move_right" 
    else: 
        return "hover" 
 
 
# Main loop 
cap = cv2.VideoCapture(0) 
 
try: 
    print("Press 'q' to quit.") 
    while cap.isOpened(): 
        ret, frame = cap.read() 
        if not ret: 
            print("Error: Camera not detected!") 
            break 
 
        frame = cv2.flip(frame, 1)  # Mirror image for better user experience 
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
        results = hands.process(rgb_frame) 
 
        if results.multi_hand_landmarks: 
            for hand_landmarks in results.multi_hand_landmarks: 
                # Draw hand landmarks 
                mp_drawing.draw_landmarks(frame, hand_landmarks, 
mp_hands.HAND_CONNECTIONS) 
 
                # Recognize and send gesture command 
                gesture = recognize_index_finger_gesture(hand_landmarks.landmark) 
                if gesture in gesture_commands: 
                    send_command(gesture_commands[gesture]) 
 
        # Display the frame 
        cv2.imshow("Gesture Control (Index Finger)", frame) 
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Quit when 'q' is pressed 
            break 
except Exception as e: 

    print(f"Unexpected error: {e}") 
finally: 
    # Cleanup resources 
    cap.release() 
    cv2.destroyAllWindows() 
    sock.close() 
    print("Resources released. Program terminated.") 
