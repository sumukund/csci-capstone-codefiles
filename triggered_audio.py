from pygame import mixer

mixer.init()

# Cache loaded sounds + channels
playing = {}

def play_triggered_audio(point):
    global playing

    active_files = set()
    if point['triggered'] == []: 
        print("no audio")
        return
    else: 
        dist = point['triggered'][0]['distance']
        print(dist)
        audio_file = point['triggered'][0]['audio']

        # Smooth volume curve (feels more natural than linear)
        volume = max(0.0, min(1.0, (1 - dist / 0.6) ** 2 ))

        # Start sound if not already playing
        if audio_file not in playing:
            breakpoint()
            sound = mixer.Sound(audio_file)
            channel = sound.play(loops=-1)
            playing[audio_file] = {
                "sound": sound,
                "channel": channel
            }

        # Update volume every frame
        playing[audio_file]["channel"].set_volume(volume)

    # # Stop sounds that are no longer in range
    # for audio_file in list(playing.keys()):
    #     if audio_file not in active_files:
    #         playing[audio_file]["channel"].stop()
    #         del playing[audio_file]