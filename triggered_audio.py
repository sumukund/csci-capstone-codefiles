import pygame

pygame.mixer.init()

# Cache loaded sounds + channels
playing = {}

def play_triggered_audio(triggered_points, radius=0.6):
    global playing

    active_files = set()

    for tp in triggered_points:
        audio_file = tp.get("audio")
        dist = tp.get("distance", radius)

        if not audio_file:
            continue

        active_files.add(audio_file)

        # Smooth volume curve (feels more natural than linear)
        volume = max(0.0, min(1.0, (1 - dist / radius) ** 2))

        # Start sound if not already playing
        if audio_file not in playing:
            sound = pygame.mixer.Sound(audio_file)
            channel = sound.play(loops=-1)
            playing[audio_file] = {
                "sound": sound,
                "channel": channel
            }

        # Update volume every frame
        playing[audio_file]["channel"].set_volume(volume)

    # Stop sounds that are no longer in range
    for audio_file in list(playing.keys()):
        if audio_file not in active_files:
            playing[audio_file]["channel"].stop()
            del playing[audio_file]