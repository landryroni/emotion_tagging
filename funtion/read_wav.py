import wave
import numpy as np
import tkinter as tk
import os

def wav_read(path):
    global play_flag
    try:
        f = wave.open(path, "rb")
        params = f.getparams()
        nchannels, sampwidth, framerate, nframes = params[:4]
        str_data = f.readframes(nframes)
        f.close()
        # Need to convert the binary data read into a computable array based on the number of channels and quantization units
        wave_data = np.frombuffer(str_data, dtype=np.short)
        if nchannels > 2 or sampwidth != 2 or os.path.getsize(path) <= 60:
            play_flag = 0
            tk.messagebox.showerror('错误', "wav文件格式错误")
        else:
            if nchannels == 2:
                # Change the array to two columns, and the number of rows matches automatically（-1），Total length stays the same，double channels turn into two columns[1,2,3,4,5,6]become[[1,2],[3 4],[5 6]]
                wave_data.shape = -1, 2
                # Transpose
                wave_data = wave_data.T
                wave_data = wave_data[0]

            play_flag = 1
            time = np.arange(0, nframes) / framerate
            return wave_data, time, nchannels
    except Exception as e:
        play_flag = 0
        tk.messagebox.showerror('Notice', "Error opening file" + str(e))
