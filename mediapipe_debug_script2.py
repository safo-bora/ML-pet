import mediapipe as mp
import cv2
import os

from debug_voice import player_path
from mediapipe_debug import detect_hand_state


def determine_section(landmark, frame_width, frame_height):
    # Assuming 4 sections horizontally and 2 vertically
    sec_width, sec_height = frame_width / 4, frame_height / 2
    x, y = landmark.x * frame_width, landmark.y * frame_height
    col = int(x / sec_width)
    row = int(y / sec_height)
    return col + 4 * row


def highlight_section(frame, section):
    height, width, _ = frame.shape
    sec_width, sec_height = width / 4, height / 2
    col = section % 4
    row = section // 4
    start_point = (int(col * sec_width), int(row * sec_height))
    end_point = (int((col + 1) * sec_width), int((row + 1) * sec_height))
    color = (0, 255, 0)
    frame = cv2.rectangle(frame, start_point, end_point, color, 10)
    cv2.putText(frame,
                str(section + 1),
                (start_point[0] + 10, start_point[1] + 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                color,
                3,
                cv2.LINE_AA)
    return frame


if __name__ == "__main__":

    # Create objects for the drawing and hands modules
    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands

    # Create a VideoCapture object to get video feed from the default camera (camera index 0)
    cap = cv2.VideoCapture(0)

    # Initialize the hands module
    hands = mp_hands.Hands(static_image_mode=False,
                           max_num_hands=2,
                           min_detection_confidence=0.5,
                           min_tracking_confidence=0.5)

    while cap.isOpened():
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)  # Flip the frame horizontally

        if not ret:
            print("Skipping empty frame.")
            continue

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb.flags.writeable = False

        results = hands.process(frame_rgb)

        frame_rgb.flags.writeable = True
        frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

        hand_connections_drawing_spec = mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2)
        landmarks_drawing_spec = mp_drawing.DrawingSpec(color=(0, 255, 0),
                                                        thickness=5,
                                                        circle_radius=10)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                                          connection_drawing_spec=hand_connections_drawing_spec,
                                          landmark_drawing_spec=landmarks_drawing_spec)
                hand_state = detect_hand_state(hand_landmarks)

                # Highlighting the section
                if hand_state == "Pointing (Index Up)":
                    section = determine_section(hand_landmarks.landmark[8],
                                                cap.get(cv2.CAP_PROP_FRAME_WIDTH),
                                                cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                    print("Debug SECTION:", section)
                    # TODO: With sound script is slow
                    # filename = f"{int(section+1)}.mp3"
                    #
                    # # Play the audio file
                    # os.system(f"{player_path} {filename}")

                    frame = highlight_section(frame, section)

                cv2.putText(frame,
                            hand_state,
                            (50, 100),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            2,
                            (0, 255, 0),
                            2,
                            cv2.LINE_AA)

                print("Hand State:", hand_state)

        cv2.imshow('MediaPipe Hands', frame)

        # Break the loop if the user presses the 'q' key
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    # Release the capture object and destroy any OpenCV windows
    hands.close()
    cap.release()
    cv2.destroyAllWindows()
