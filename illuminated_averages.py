import numpy as np
from scipy.io import wavfile

def reverberated_average(input_path, output_path, duration_seconds=5, window_size=8192):
    # 1. Load the audio
    sr, data = wavfile.read(input_path)
    if len(data.shape) > 1: data = data.mean(axis=1) # Convert to mono (or do each channel seperatly)
    data = data / np.max(np.abs(data)) # Normalize to improve math

    # 2. Calculate Spectral Average
    # Important: Using RFFT/IRFFT as the inputs and outputs are always real
    hop_size = window_size // 4      # Size of the FFT analysis window stide (smaller is slower)
    window = np.hanning(window_size) # Numpy has a built-in hann window creating function

    magnitudes = []
    for i in range(0, len(data) - window_size, hop_size):
        segment = data[i:i+window_size] * window
        spec = np.fft.rfft(segment)
        magnitudes.append(np.abs(spec))

    # Averaging the magnitudes "Spectral Fingerprint"
    avg_mag = np.mean(magnitudes, axis=0)

    # 3. Randomize phase and Overlaping adds based on the hann window
    out_length = int(sr * duration_seconds)
    output = np.zeros(out_length + window_size)
    num_overlaps = 8
    synth_hop = window_size // num_overlaps  # Higher overlap --> smoother texture

    for i in range(0, out_length, synth_hop):
        # Generate random phase (0 to 2pi) for each bin
        random_phase = np.exp(1j * np.random.uniform(0, 2*np.pi, len(avg_mag)))
        reconstructed_spec = avg_mag * random_phase  # Combine Average Magnitude with Random Phase

        # IFFT back to time domain (uses IRFFT in ensure results are all real)
        audio_win = np.fft.irfft(reconstructed_spec)
        audio_win *= window  #Scale acording to hann windowing falloff

        # Add to output buffer
        output[i:i+window_size] += audio_win / (num_overlaps / 2)  # Reduce volume by overlap amounts

    # Normalize and export
    output = (output / np.max(np.abs(output)) * 32767).astype(np.int16) # Scale -1,1 to lie within (signed) 16 bit wav
    wavfile.write(output_path, sr, output)

# Example Usage
reverberated_average('trimmed_input.wav', 'sonic_texture_fingerprint.wav', window_size = 32768)

# Load and play the file just created (works in Colab)
from IPython.display import Audio
sr, data = wavfile.read('sonic_texture_fingerprint.wav')
Audio(data=data, rate=sr)
sr, data = wavfile.read("input.wav")
wavfile.write('trimmed_input.wav', sr, data[:10*sr]*3) # Make a bit louder for the campoarsion

sr_trimmed, data_trimmed = wavfile.read('trimmed_input.wav')

import io
import wave
with io.BytesIO() as wav_buffer:
    with wave.open(wav_buffer, 'wb') as wf:
        wf.setnchannels(data_trimmed.shape[1] if data_trimmed.ndim > 1 else 1) # Set number of channels
        wf.setsampwidth(data_trimmed.dtype.itemsize) # Set sample width (2 for int16)
        wf.setframerate(sr_trimmed) # Set sample rate
        wf.writeframes(data_trimmed.tobytes()) # Write the raw audio data

    wav_data = wav_buffer.getvalue()

Audio(wav_data)