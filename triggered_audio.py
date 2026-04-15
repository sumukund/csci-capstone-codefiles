import time
from pygame import mixer


class AudioEngine:
    def __init__(self):
        mixer.init()
        mixer.set_num_channels(16)

        self.current_track = None
        self.start_time = 0
        self.paused_pos = {}

        # Channels
        self.head_channel = mixer.Channel(1)
        self.velocity_channel = mixer.Channel(2)

        self.current_head_track = None
        self.current_velocity_track = None

        # Head tracking
        self.last_head_y = None
        self.last_head_time = 0

        # Velocity
        self.velocity_active = False

        # Config
        self.HEAD_POS_ON = 1
        self.HEAD_POS_OFF = 1.5
        self.HEAD_TIMEOUT = 0.5

        self.ACCEL_ON = 0.1
        self.ACCEL_OFF = 0.09

        self.FADE_MS = 300

        self.sound_cache = {}

    def get_sound(self, path):
        if path not in self.sound_cache:
            try:
                self.sound_cache[path] = mixer.Sound(path)
            except Exception as e:
                print(f"ERROR loading sound {path}: {e}")
                return None
        return self.sound_cache[path]

    def update_music(self, audio_file):
        if self.current_track == audio_file:
            return

        if self.current_track is not None:
            elapsed = time.time() - self.start_time
            self.paused_pos[self.current_track] = elapsed
            print(f"PAUSE {self.current_track} at {elapsed:.2f}s")

        start_pos = self.paused_pos.get(audio_file, 0)

        print(f"PLAY {audio_file} from {start_pos:.2f}s")

        try:
            mixer.music.load(audio_file)
            mixer.music.play(start=start_pos, fade_ms=self.FADE_MS)
        except Exception as e:
            print(f"ERROR loading {audio_file}: {e}")
            return

        self.current_track = audio_file
        self.start_time = time.time() - start_pos

    def stop_all(self):
        if self.current_track is not None:
            elapsed = time.time() - self.start_time
            self.paused_pos[self.current_track] = elapsed

        mixer.music.fadeout(self.FADE_MS)
        self.head_channel.fadeout(self.FADE_MS)
        self.velocity_channel.fadeout(self.FADE_MS)

        self.current_track = None
        self.current_head_track = None
        self.current_velocity_track = None
        self.velocity_active = False

    def update_head(self, head_y, head_file):
        if head_y is None:
            if self.current_head_track is not None:
                self.head_channel.fadeout(self.FADE_MS)
                self.current_head_track = None
            return

        head_y = max(0.0, min(2.5, head_y))

        if head_y < self.HEAD_POS_ON:
            if self.current_head_track != head_file:
                print(f"START HEAD: {head_file}")
                sound = self.get_sound(head_file)
                if sound:
                    self.head_channel.play(sound, loops=-1, fade_ms=self.FADE_MS)
                    self.head_channel.set_volume(0.6)
                    self.current_head_track = head_file

        elif head_y > self.HEAD_POS_OFF:
            if self.current_head_track is not None:
                print("STOP HEAD")
                self.head_channel.fadeout(self.FADE_MS)
                self.current_head_track = None

    def update_velocity(self, acceleration, velocity_file):
        if acceleration > self.ACCEL_ON:
            self.velocity_active = True
        elif acceleration < self.ACCEL_OFF:
            self.velocity_active = False

        if self.velocity_active:
            if self.current_velocity_track != velocity_file:
                print(f"START VELOCITY: {velocity_file}")
                sound = self.get_sound(velocity_file)
                if sound:
                    self.velocity_channel.play(sound, loops=-1, fade_ms=self.FADE_MS)
                    self.velocity_channel.set_volume(0.7)
                    self.current_velocity_track = velocity_file
        else:
            if self.current_velocity_track is not None:
                print("STOP VELOCITY")
                self.velocity_channel.fadeout(self.FADE_MS)
                self.current_velocity_track = None

    # ---------------- MAIN UPDATE ----------------
    def update(self, point, acceleration=0.0):
        # --- NO TRIGGER ---
        if not point.get("triggered"):
            self.stop_all()
            return

        trigger = point["triggered"][0]

        audio_file = f"songs/{trigger['audio']}"
        head_file = f"songs/{trigger['emotional_layer']}"
        velocity_file = "songs/song.wav"

        self.update_music(audio_file)

        dist = trigger["distance"]
        volume = max(0.0, min(1.0, (1 - dist / 0.6) ** 2))
        mixer.music.set_volume(volume)

        head_pos = point.get("head_position")
        head_y = None

        if head_pos and len(head_pos) >= 2:
            y = head_pos[1]
            if y == y:  # not NaN
                self.last_head_y = y
                self.last_head_time = time.time()
                head_y = y

        if head_y is None:
            if self.last_head_y and (time.time() - self.last_head_time < self.HEAD_TIMEOUT):
                head_y = self.last_head_y

        self.update_head(head_y, head_file)
        self.update_velocity(acceleration, velocity_file)