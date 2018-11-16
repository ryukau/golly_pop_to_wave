"""
matplotlibのサイズ調整について。

https://stackoverflow.com/questions/13714454/specifying-and-saving-a-figure-with-exact-size-in-pixels
"""

import matplotlib.pyplot as pyplot
import numpy
import soundfile
import subprocess
from pathlib import Path

Path("img").mkdir(exist_ok=True)

wav_data = []

snd_dir = Path("snd")
for index, wav_file in enumerate(snd_dir.glob("*.wav")):
    wav_name = str(wav_file)
    data, _ = soundfile.read(wav_name)
    wav_data.append(data)

    # Format 1-2-3-P4-5_foo_bar.wav into 1/2/3:P4,5
    rule = wav_name.split("_")[0].split("/")[1].split("P")
    rule[0] = rule[0].replace("-", "/", 2).replace("-", ":")
    rule[1] = rule[1].replace("-", ",")

    pyplot.figure(figsize=(12.80, 7.20), dpi=10)
    pyplot.plot(data, lw=0.5, color="black")
    pyplot.title("P".join(rule))
    pyplot.box(False)
    pyplot.grid()
    pyplot.xlabel("Generation")
    pyplot.ylabel("Population ratio")
    pyplot.ylim([0, 1])
    pyplot.savefig(f"img/{index:08}.png", dpi=100)
    pyplot.close()

wav_data = numpy.concatenate(wav_data, axis=None)
soundfile.write("merged.wav", wav_data, 44100)

subprocess.run([
    "ffmpeg",
    "-framerate",
    "5",
    "-i",
    "img/%08d.png",
    "-i",
    "merged.wav",
    "-c:v",
    "libx264",
    "-pix_fmt",
    "yuv420p",
    "-crf",
    "18",
    "-r",
    "30",
    "-c:a",
    "aac",
    "-b:a",
    "256k",
    "-y",
    "output.mp4",
])
