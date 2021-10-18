import wave
import numpy as np
import tkinter as tk
import os
import pyaudio

def wav_play(wav_name, path):
    global play_flag
    wav_path = os.path.join(path, wav_name)

    # define stream chunk
    chunk = 1024
    try:
        # open a wav format music
        f = wave.open(wav_path, "rb")
        if play_flag == 1:
            # instantiate PyAudio
            p = pyaudio.PyAudio()
            # open stream
            stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                            channels=f.getnchannels(),
                            rate=f.getframerate(),
                            output=True)
            # read data
            data = f.readframes(chunk)

            # play stream
            while data:
                stream.write(data)
                data = f.readframes(chunk)

                # stop stream

                global bool_stop_play
                if bool_stop_play:
                    break
            stream.stop_stream()
            stream.close()

            # close PyAudio
            p.terminate()
            f.close()
            # Play selected audio file
        else:
            tk.messagebox.showinfo('Notice', "Can't display file")
    except Exception as e:
        tk.messagebox.showinfo('Notice', "Can't open file" + str(e))
