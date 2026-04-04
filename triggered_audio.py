from pygame import mixer
import time
from pydub import AudioSegment
from pydub.playback import play


mixer.init()
mixer.set_num_channels(16)
current_track = None
start_time = 0
paused_pos = {}  

# --- OVERLAY SOUND ---
velocity_sound = mixer.Sound("songs/speed.mp3")
velocity_channel = mixer.Channel(1)

velocity_channel.play(velocity_sound, loops=-1)
velocity_channel.set_volume(0)  # start silent

def speed_to_volume(speed, max_speed=2.0):
    return max(0.0, min(1.0, speed / max_speed))

def update_velocity_layer(speed):

    # Normalize speed to volume
    volume = speed_to_volume(speed, max_speed=2.0)

    velocity_channel.set_volume(volume)

def play_triggered_audio(point):
    global current_track, start_time, paused_pos

    if not point['triggered']:
        if current_track is not None:
            elapsed = time.time() - start_time
            paused_pos[current_track] = elapsed

            print(f"PAUSE {current_track} at {elapsed:.2f}s")

            mixer.music.stop()
            current_track = None
        return

    trigger = point['triggered'][0]
    audio_file = f"songs/{trigger['audio']}"
    dist = trigger['distance']
    speed = point['speed']

    volume = max(0.0, min(1.0, (1 - dist / 0.6) ** 2))
    mixer.music.set_volume(volume)
    
    # audio = AudioSegment.from_file(audio_file, sample_width=2, 
    # frame_rate=44100, 
    # channels=2)
    
    if current_track == audio_file:
        return

    if current_track is not None:
        elapsed = time.time() - start_time
        paused_pos[current_track] = elapsed
        print(f"SWITCH PAUSE {current_track} at {elapsed:.2f}s")

    # Start/resume new track
    start_pos = paused_pos.get(audio_file, 0)

    print(f"PLAY {audio_file} from {start_pos:.2f}s")

    mixer.music.load(audio_file)
    mixer.music.play(start=start_pos)
    update_velocity_layer(speed)
    # Slice the audio from the start_time to the end
    # segment_to_play = audio[start_pos:]

    # Play the sliced segment
    # play(segment_to_play)

    current_track = audio_file
    start_time = time.time() - start_pos

