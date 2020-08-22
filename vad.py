'''
Real-time VAD implementation using PyAudio and WebRTCVAD

Also calculates mean amplitude of audio chunks to detect voice intensity

By Ishaan Sinha
'''

import pyaudio
import wave
import webrtcvad
import math
import numpy
import struct

FORMAT = pyaudio.paInt16
CHANNELS = 1 # Audio must be mono-channel
RATE = 32000 # Sample rates mest be 8000, 16000, 32000, or 48000
CHUNK = 960 # Audio segments must be 10, 20, or 30 ms in length, 960 / 32000 = 30 ms

audio = pyaudio.PyAudio()
vad = webrtcvad.Vad()

vad.set_mode(3) # How aggressive should the algorithm be?

def get_rms( block ):
    # RMS amplitude is defined as the square root of the 
    # mean over time of the square of the amplitude.
    # so we need to convert this string of bytes into 
    # a string of 16-bit samples...

    # we will get one short out for each 
    # two chars in the string.
    count = len(block)/2
    format = "%dh"%(count)
    shorts = struct.unpack( format, block )
    SHORT_NORMALIZE = (1.0/32768.0)

    # iterate over the block.
    sum_squares = 0.0
    for sample in shorts:
        # sample is a signed short in +/- 32768. 
        # normalize it to 1.0
        n = sample * SHORT_NORMALIZE
        sum_squares += n*n

    linearRms = math.sqrt( sum_squares / count )
    return 100 * linearRms # Reduce decimal points

# start Recording
stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=CHUNK)
print ("recording...")
frames = []

while True:
    try:
        data = stream.read(CHUNK)
        print ('Contains speech: %s' % (vad.is_speech(data, RATE)) + '\tAmplitude: %s' % round(get_rms(data), 5))
    except KeyboardInterrupt:
        break

print ("finished recording")

# stop Recording
stream.stop_stream()
stream.close()
audio.terminate()
