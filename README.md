# pop_to_wave
A [Golly](http://golly.sourceforge.net/) script written in python2 that creates wave files from `g.getpop()`.

# Usage

```bash
$ mv Script/pop-to-wave.py /path/to/golly/Script

# Start Golly.
# Select `File` -> `Run Script...` from menu.
# Select pop-to-wave.py.

$ cp -r /path/to/golly/Script/snd .
$ python3 concat_wav.py
```

# Dependency
`pop-to-wave.py` is Python2 and dependent on [`scipy.io.wavfile.write`](https://docs.scipy.org/doc/scipy-1.0.0/reference/generated/scipy.io.wavfile.write.html#scipy.io.wavfile.write) in SciPy 1.0.0.

`concat_wav.py` is Python3 and dependent on [matplotlib](https://matplotlib.org/), [NumPy](http://www.numpy.org/), [PySoundFile](https://pysoundfile.readthedocs.io/en/0.9.0/) and `ffmpeg`.
