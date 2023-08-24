from gtts import gTTS
import os

# Define the player path
player_path = "/opt/homebrew/bin/mpg321"

# Loop through numbers 1 to 5
for i in range(1, 6):
    # Convert number to text
    text = str(i)

    # Create the TTS object
    tts = gTTS(text=text, lang='en')

    # Save the audio file
    filename = f"{text}.mp3"
    tts.save(filename)

    # Play the audio file
    os.system(f"{player_path} {filename}")


