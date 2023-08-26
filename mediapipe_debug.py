import mediapipe as mp
import cv2
# import os
# from gtts import gTTS

arduino_logic = False

if arduino_logic:
    from lib import ArduinoLCD, ArduinoLEDController


class ArduinoHelper(object):

    if arduino_logic:
        lcd = ArduinoLCD()
        led = ArduinoLEDController()
        MAX_PINS = 5
        pin_states = [False] * MAX_PINS  # False indicates off, True indicates on.
        last_hands_state = None  # added to keep track of the previous hands_state

    @staticmethod
    def replace_second_space_with_newline(string):
        parts = string.split(' ')
        if len(parts) > 2:
            parts[1] = parts[1] + '\n'
        return ' '.join(parts)

    @classmethod
    def sent_to_lcd(cls, hands_state):
        if hands_state != cls.last_hands_state:
            cls.lcd.clear_lcd()
            cls.lcd.send_to_lcd(cls.replace_second_space_with_newline(hands_state))
            cls.last_hands_state = hands_state

            # Play the audio file:
            # tts = gTTS(text=hands_state, lang='en')
            # filename = f"{hands_state}.mp3"
            # tts.save(filename)
            # player_path = "/opt/homebrew/bin/mpg321"
            # os.system(f"{player_path} {filename}")

    @classmethod
    def toggle_target_led(cls, pin_number):
        num = int(pin_number)
        if num < 1 or num > cls.MAX_PINS:
            print(f"pin_number should be between 1 and {cls.MAX_PINS}")

        for i in range(cls.MAX_PINS):
            if i < num:
                if not cls.pin_states[i]:
                    cls.led.toggle_led(i + 1)
                    cls.pin_states[i] = True
            else:
                if cls.pin_states[i]:
                    cls.led.turn_off(i + 1)
                    cls.pin_states[i] = False

    @classmethod
    def turn_off(cls, pin):
        if cls.pin_states[pin - 1]:  # -1 since our list is 0-indexed, but pins start from 1
            cls.led.turn_off(pin)
            cls.pin_states[pin - 1] = False


def replace_second_space_with_newline(s):
    # Find the index of the first space
    first_space_index = s.find(' ')

    # If there is no space, return the string as it is
    if first_space_index == -1:
        return s

    # Find the index of the second space
    second_space_index = s.find(' ', first_space_index + 1)

    # If there is no second space, return the string as it is
    if second_space_index == -1:
        return s

    # Replace the second space with a newline and return the result
    return s[:second_space_index] + '\n' + s[second_space_index + 1:]


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

    if arduino_logic:
        helper.toggle_target_led(str(fingers_count))

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


if __name__ == "__main__":

    if arduino_logic:
        helper = ArduinoHelper()

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

        hand_connections_drawing_spec = mp_drawing.DrawingSpec(color=(255, 255, 0), thickness=2)
        landmarks_drawing_spec = mp_drawing.DrawingSpec(color=(0, 255, 0),
                                                        thickness=5,
                                                        circle_radius=10)

        # Draw the hand landmarks if hands are detected
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                                          connection_drawing_spec=hand_connections_drawing_spec,
                                          landmark_drawing_spec=landmarks_drawing_spec)
                hand_state = detect_hand_state(hand_landmarks)\

                cv2.putText(frame,
                            hand_state,
                            (50, 100),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            3,
                            (255, 255, 0),
                            3,
                            cv2.LINE_AA)

                print("Hand State:", hand_state)

                if arduino_logic:
                    helper.sent_to_lcd(hands_state=hand_state)

        cv2.imshow('MediaPipe Hands', frame)

        # Break the loop if the user presses the 'q' key
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    # Release the capture object and destroy any OpenCV windows
    hands.close()
    cap.release()
    cv2.destroyAllWindows()

    if arduino_logic:
        helper.lcd.close_connection()
        helper.led.turn_off_all_leds()
        helper.led.close()