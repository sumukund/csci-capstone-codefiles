import time
from pygame import mixer

mixer.init()
mixer.set_num_channels(16)

# =========================
# STATE
# =========================
current_track = None
current_head_track = None
start_time = 0
paused_pos = {}

head_channel = mixer.Channel(1)

last_head_y = None
last_head_time = 0


HEAD_POS_ON = 0.9     # crouch / lean down
HEAD_POS_OFF = 1.4    # stand up
HEAD_TIMEOUT = 0.5    # time out for NAN

FADE_MS = 300

sound_cache = {}

def get_sound(path):
    if path not in sound_cache:
        try:
            sound_cache[path] = mixer.Sound(path)
        except Exception as e:
            print(f"ERROR loading sound {path}: {e}")
            return None
    return sound_cache[path]


def play_triggered_audio(point):
    global current_track, current_head_track, start_time
    global last_head_y, last_head_time

    if not point.get('triggered'):
        if current_track is not None:
            elapsed = time.time() - start_time
            paused_pos[current_track] = elapsed

            print(f"STOP ALL at {elapsed:.2f}s")

            mixer.music.fadeout(FADE_MS)
            head_channel.fadeout(FADE_MS)

            current_track = None
            current_head_track = None

        return

    trigger = point['triggered'][0]

    audio_file = f"songs/{trigger['audio']}"
    velocity_file = f"songs/{trigger['emotional_layer']}"

    dist = trigger['distance']


    head_pos = point.get('head_position')
    valid = False

    if head_pos and len(head_pos) >= 2:
        head_y = head_pos[1]

        if head_y is not None and head_y == head_y:
            last_head_y = head_y
            last_head_time = time.time()
            valid = True

    # fallback to last known good value
    if not valid:
        if last_head_y is not None and (time.time() - last_head_time < HEAD_TIMEOUT):
            head_y = last_head_y
            print("USING LAST HEAD POSITION")
        else:
            print("HEAD LOST → SAFE SHUTDOWN")
            head_y = None


    if current_track != audio_file:
        if current_track is not None:
            elapsed = time.time() - start_time
            paused_pos[current_track] = elapsed
            print(f"SWITCH PAUSE {current_track} at {elapsed:.2f}s")

        start_pos = paused_pos.get(audio_file, 0)

        print(f"PLAY {audio_file} from {start_pos:.2f}s")

        try:
            mixer.music.load(audio_file)
            mixer.music.play(start=start_pos, fade_ms=FADE_MS)
        except Exception as e:
            print(f"ERROR loading music {audio_file}: {e}")
            return

        current_track = audio_file
        start_time = time.time() - start_pos

    # distance-based volume
    volume = max(0.0, min(1.0, (1 - dist / 0.6) ** 2))
    mixer.music.set_volume(volume)


    if head_y is None:
        if current_head_track is not None:
            print("FORCE STOP VELOCITY (HEAD LOST)")
            head_channel.fadeout(FADE_MS)
            current_head_track = None
        return

    head_y = max(0.0, min(2.5, head_y))

    # --- TURN ON ---
    if head_y < HEAD_POS_ON:
        if current_head_track != velocity_file:
            print(f"START VELOCITY: {velocity_file}")

            sound = get_sound(velocity_file)
            if sound is not None:
                head_channel.play(sound, loops=-1, fade_ms=FADE_MS)
                head_channel.set_volume(0.6)

                current_head_track = velocity_file

    # --- TURN OFF ---
    elif head_y > HEAD_POS_OFF:
        if current_head_track is not None:
            print("STOP VELOCITY")

            head_channel.fadeout(FADE_MS)
            current_head_track = None