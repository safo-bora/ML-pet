import cv2
import mediapipe as mp

# Initialize MediaPipe Pose module
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Initialize MediaPipe drawing module
mp_drawing = mp.solutions.drawing_utils

# Specify yellow color for landmarks
landmark_color = (0, 255, 255)  # Yellow in BGR format
landmark_style = mp_drawing.DrawingSpec(color=landmark_color, thickness=3, circle_radius=7)

# Specify white color for connections
connection_style = mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=4)

# Start capturing video from the webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        continue

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)

    # Draw the pose annotations on the frame
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                  landmark_style, connection_style)

        # Add labels to each landmark
        for id, landmark in enumerate(results.pose_landmarks.landmark):
            landmark_px = mp_drawing._normalized_to_pixel_coordinates(landmark.x, landmark.y, frame.shape[1], frame.shape[0])
            if landmark_px:  # Check if the conversion is successful
                cv2.putText(frame, str(id), landmark_px, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    cv2.imshow('MediaPipe Pose', frame)
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
