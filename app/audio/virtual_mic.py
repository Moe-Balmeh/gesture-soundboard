import re
import threading

import numpy as np
import sounddevice as sd

RATE = 44100  # same as pygame's mixer
CABLE_NAME = "CABLE Input"  # the "speaker" side of VB-Cable, zoom hears it as "CABLE Output"
# directsound resamples for us, wasapi would need the exact device rate
HOST = "Windows DirectSound"
# mic and cable run on separate clocks, so the mic can slowly get ahead.
# if more than 0.1s piles up, skip ahead so your voice doesn't lag behind
MIC_MAX = RATE // 10
MIC_KEEP = RATE // 50


def _devices(output):
    for i, device in enumerate(sd.query_devices()):
        channels = device["max_output_channels" if output else "max_input_channels"]
        if channels > 0 and sd.query_hostapis(device["hostapi"])["name"] == HOST:
            yield i, device["name"]


def find_device(name, output):
    for i, device_name in _devices(output):
        if name.lower() in device_name.lower():
            return i
    return None


def short_name(name):
    # "Microphone (3- Rapoo Gaming Headset)" -> "Rapoo Gaming Headset"
    # the number can change when you replug it, find_device matches by part of the name anyway
    inside = re.search(r"\((.*)\)", name)
    return re.sub(r"^\d+- ", "", inside.group(1) if inside else name)


def list_mics():
    # the cable itself is left out, picking it would feed the sound back into itself
    return [
        short_name(name) for _, name in _devices(output=False)
        if "cable" not in name.lower() and name != "Primary Sound Capture Driver"
    ]


class VirtualMic:
    def __init__(self):
        self._stream = None
        self._mic_stream = None
        self._playing = []  # [samples, position]
        self._mic_audio = np.zeros(0, np.float32)
        self._lock = threading.Lock()
        self.error = None
        self.mic_error = None
        self.mic_name = None
        self.mic_volume = 1.0
        self.sounds_volume = 1.0

    @property
    def is_open(self):
        return self._stream is not None

    def open(self):
        device = find_device(CABLE_NAME, output=True)
        if device is None:
            self.error = "VB-Cable not found. Install it, then restart the app."
            return False
        try:
            self._stream = sd.OutputStream(
                RATE, device=device, channels=2, dtype="float32", latency="low", callback=self._fill
            )
            self._stream.start()
            self.error = None
        except sd.PortAudioError:
            self._stream = None
            self.error = "Couldn't open VB-Cable."
            return False
        self._open_mic()
        return True

    def set_mic(self, name):
        self.mic_name = name
        if self.is_open:
            self._close_mic()
            self._open_mic()

    def _open_mic(self):
        self.mic_error = None
        if not self.mic_name:
            return
        device = find_device(self.mic_name, output=False)
        if device is None:
            self.mic_error = "Mic not found. Is it plugged in?"
            return
        try:
            self._mic_stream = sd.InputStream(
                RATE, device=device, channels=1, dtype="float32", latency="low", callback=self._on_mic
            )
            self._mic_stream.start()
        except sd.PortAudioError:
            self._mic_stream = None
            self.mic_error = "Couldn't open that mic."

    def _close_mic(self):
        if self._mic_stream is not None:
            self._mic_stream.close()
            self._mic_stream = None
        with self._lock:
            self._mic_audio = np.zeros(0, np.float32)

    def play(self, samples):
        # pygame gives int16, the stream wants floats between -1 and 1
        samples = samples.astype(np.float32) / 32768
        if samples.ndim == 1:
            samples = samples[:, None]
        if samples.shape[1] == 1:
            samples = np.repeat(samples, 2, axis=1)
        with self._lock:
            self._playing.append([samples[:, :2], 0])

    def _on_mic(self, data, frames, time_info, status):
        # runs on the mic's audio thread
        with self._lock:
            audio = np.concatenate([self._mic_audio, data[:, 0]])
            if len(audio) > MIC_MAX:
                audio = audio[-MIC_KEEP:]
            self._mic_audio = audio

    def _fill(self, out, frames, time_info, status):
        # runs on the cable's audio thread, adds up the sounds and your voice
        out.fill(0)
        with self._lock:
            for sound in self._playing:
                samples, pos = sound
                chunk = samples[pos:pos + frames]
                out[:len(chunk)] += chunk
                sound[1] = pos + frames
            self._playing = [s for s in self._playing if s[1] < len(s[0])]
            voice, self._mic_audio = self._mic_audio[:frames], self._mic_audio[frames:]
        out *= self.sounds_volume
        out[:len(voice)] += voice[:, None] * self.mic_volume
        np.clip(out, -1, 1, out=out)  # overlapping sounds can go over

    def close(self):
        self._close_mic()
        if self._stream is not None:
            self._stream.close()
            self._stream = None
        with self._lock:
            self._playing = []
