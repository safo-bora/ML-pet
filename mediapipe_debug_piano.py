import cv2
import time
import threading
import mediapipe as mp

from pydub.generators import Sine
from pydub.playback import play


# Frequencies corresponding to a I-IV-V-I chord progression in C major
# Chords: C major (C-E-G), F major (F-A-C), G major (G-B-D), back to C major
frequencies = [261.63, 329.63, 392.00,  # C major chord: C4, E4, G4
               349.23, 440.00, 523.25,  # F major chord: F4, A4, C5
               392.00, 493.88, 587.33,  # G major chord: G4, B4, D5
               261.63, 329.63, 392.00]  # Back to C major chord


# Dictionary to keep track of the last played time for each frequency
last_played_times = {}


def detect_hand_state(hand_landmarks):
    finger_tips = [4, 8, 12, 16, 20]  # Index of the tip landmarks for each finger
    finger_mcp = [1, 5, 9, 13, 17]  # Index of the MCP joint for each finger

    def is_finger_open(tip, mcp, next_mcp):
        return hand_landmarks.landmark[tip].y < hand_landmarks.landmark[mcp].y and hand_landmarks.landmark[tip].y < \
            hand_landmarks.landmark[next_mcp].y

    # Create a list to track the open/closed state of fingers
    fingers_state = [is_finger_open(finger_tips[i], finger_mcp[i], finger_mcp[i + 1] if i < 4 else finger_mcp[0]) for i
                     in range(5)]

    fingers_count = fingers_state.count(True)
    print("Number of Open Fingers:", fingers_count)

    if all(not finger for finger in fingers_state):
        return "Fist"
    if fingers_state == [False, True, True, False, False]:
        return "Victory/Peace Sign"
    if fingers_state == [True, False, False, False, False]:
        return "Thumbs Up"
    if fingers_state == [False, True, False, False, False]:
        return "Pointing (Index Up)"
    if fingers_state == [False, False, True, True, True]:
        return "Three fingers (Scouts Salute)"
    if fingers_state == [False, True, False, False, True]:
        return "Rock on"
    if fingers_state == [True, True, True, True, True] and \
            (hand_landmarks.landmark[finger_tips[0]].x - hand_landmarks.landmark[finger_tips[1]].x)**2 + \
            (hand_landmarks.landmark[finger_tips[0]].y - hand_landmarks.landmark[finger_tips[1]].y)**2 < 0.02:
        return "OK Sign"
    if fingers_state == [True, True, False, False, False] and \
            (hand_landmarks.landmark[finger_tips[0]].x - hand_landmarks.landmark[finger_tips[1]].x)**2 + \
            (hand_landmarks.landmark[finger_tips[0]].y - hand_landmarks.landmark[finger_tips[1]].y)**2 < 0.02:
        return "Pinch"
    if all(finger for finger in fingers_state) and \
            hand_landmarks.landmark[finger_tips[0]].x > hand_landmarks.landmark[0].x:
        return "Open Palm"
    if fingers_state == [True, False, False, False, True]:
        return "Hang Loose/Shaka"
    if fingers_state == [True, True, False, False, False]:
        return "Gun Hand Gesture"
    if fingers_state == [True, True, True, True, True]:
        return "Open Hand"
    if fingers_state == [True, True, False, False, True]:
        return "Call Me"

    return "Other"


def play_tone(frequency, duration=350, min_interval=1):
    """
    Play a tone at the specified frequency. Each frequency is played
    only once in every 'min_interval' seconds.

    Parameters:
    frequency (int): Frequency of the tone in Hz
    duration (int): Duration of the tone in milliseconds
    min_interval (float): Minimum interval between plays for the same frequency in seconds
    """
    current_time = time.time()
    last_played = last_played_times.get(frequency, 0)

    if current_time - last_played >= min_interval:
        tone = Sine(frequency)
        audio_segment = tone.to_audio_segment(duration=duration)
        play(audio_segment)
        last_played_times[frequency] = current_time


def determine_section(landmark, frame_width, frame_height):
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

    # Define a set of colors
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255), (128, 128, 0), (128, 0, 128)]
    color = colors[section % len(colors)]

    frame = cv2.rectangle(frame, start_point, end_point, color, 10)

    # Text settings
    text = str(section + 1)
    font_scale = 10
    font_thickness = 3
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]

    # Center the text and convert to integer
    text_x = int(start_point[0] + (sec_width - text_size[0]) / 2)
    text_y = int(start_point[1] + (sec_height + text_size[1]) / 2)

    cv2.putText(frame, text, (text_x, text_y), font, font_scale, color, font_thickness, cv2.LINE_AA)

    return frame


if __name__ == "__main__":
    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands

    cap = cv2.VideoCapture(0)

    hands = mp_hands.Hands(static_image_mode=False,
                           max_num_hands=2,
                           min_detection_confidence=0.5,
                           min_tracking_confidence=0.5)

    while cap.isOpened():
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)

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

                section = determine_section(hand_landmarks.landmark[8],
                                            cap.get(cv2.CAP_PROP_FRAME_WIDTH),
                                            cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                print("DEBUG SECTION:", section)

                try:
                    threading.Thread(target=play_tone, args=(frequencies[section-1],)).start()
                except IndexError:
                    print("ERROR! Section FAILED:", section)

                frame = highlight_section(frame, section)

        cv2.imshow('MediaPipe Hands', frame)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    hands.close()
    cap.release()
    cv2.destroyAllWindows()
