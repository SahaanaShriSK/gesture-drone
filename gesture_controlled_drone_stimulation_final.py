import cv2
import mediapipe as mp
import pygame

# Initialize MediaPipe for hand tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

# Initialize pygame for simulation
pygame.init()

# Set up screen size for the simulation
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Gesture Controlled Drone Simulation")

# Load the drone image
drone_image = pygame.image.load('dr.png')
drone_image = pygame.transform.scale(drone_image, (200, 200))  # Resize to fit the screen

# Load the background image
background_image = pygame.image.load('b.png')
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

# Set the initial position of the "drone"
drone_pos = [screen_width // 2, screen_height // 2]
drone_speed = 5

# Initialize video capture (webcam)
cap = cv2.VideoCapture(0)

def detect_gesture(landmarks):
    thumb_tip = landmarks[4]   # Tip of the thumb
    index_tip = landmarks[8]   # Tip of the index finger

    if thumb_tip.y < landmarks[3].y and index_tip.y < landmarks[7].y:
        return "UP"
    elif thumb_tip.y > landmarks[3].y and index_tip.y > landmarks[7].y:
        return "DOWN"
    elif thumb_tip.x < index_tip.x:
        return "LEFT"   # Real-world left
    elif thumb_tip.x > index_tip.x:
        return "RIGHT"  # Real-world right
    return None



# Main loop for webcam capture and gesture control
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip frame horizontally for mirror view
    frame = cv2.flip(frame, 1)

    # Convert to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    # Detect gestures from hand landmarks
    gesture = None
    if results.multi_hand_landmarks:
        for landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)
            gesture = detect_gesture(landmarks.landmark)
    
    # Control drone movement based on gesture
    if gesture == "UP":
        drone_pos[1] -= drone_speed  # Move up
    elif gesture == "DOWN":
        drone_pos[1] += drone_speed  # Move down
    elif gesture == "LEFT":
        drone_pos[0] -= drone_speed  # Move left
    elif gesture == "RIGHT":
        drone_pos[0] += drone_speed  # Move right

    # Prevent the drone from going out of bounds
    drone_pos[0] = max(0, min(drone_pos[0], screen_width - 200))
    drone_pos[1] = max(0, min(drone_pos[1], screen_height - 200))

    # === Draw background every frame ===
    screen.blit(background_image, (0, 0))

    # Draw the drone on top of the background
    screen.blit(drone_image, (drone_pos[0], drone_pos[1]))

    # Show MediaPipe webcam window
    cv2.imshow('Hand Gesture Control', frame)

    # Update pygame display
    pygame.display.flip()

    # Handle quit events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            pygame.quit()
            cv2.destroyAllWindows()
            exit()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
pygame.quit()
cv2.destroyAllWindows()
