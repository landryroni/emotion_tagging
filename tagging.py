# voice emotion tagging
# designed by Junyao Zhan 
# translated by Dejoli Tientcheu Touko Landry

# -*- coding:utf-8 -*-
import os
from funtion  import *

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter.filedialog import askdirectory
import sys
from threading import Thread
import wave
import pyaudio
import numpy as np

# emotions
label_item_list = ["boredom","neutral","happy", "sad","angry", "fear", "disgust", "surprise", "excited","pleasure","pain","disapointed","others"]



class Tagging(tk.Tk):
    def __init__(self):
        super().__init__()
        # self.pack() # To continue tk.Frame ，This sentence must have！
        self.title('Annotation of Human Voice Emotion Samples')

        # Parameters/data
        self.select_value = tk.IntVar()

        self.recordings_path = tk.StringVar()
        self.progress_count = tk.StringVar()

        self.all_wav_paths = []

        self.wav_dir = ""
        self.current_wav_basename = ""
        self.current_wav_path = ""

        self.current_wav_data = []
        self.current_wav_time = []
        self.current_wav_channel = 1

        # Interface
        self.setupUI()

    def setupUI(self):
        # First row select folder
        row1 = tk.Frame(self)
        row1.pack(fill="x")
        row1col1 = tk.Frame(row1)
        row1col1.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)
        tk.Label(row1col1, text="Sample Folder", width=15).pack(anchor=tk.CENTER, expand=tk.YES, fill=tk.BOTH)

        row1col2 = tk.Frame(row1)
        row1col2.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)
        self.entry1 = tk.Entry(row1col2, textvariable=self.recordings_path, width=30)
        self.entry1.pack(anchor=tk.CENTER, side=tk.TOP, fill=tk.BOTH)

        row1col3 = tk.Frame(row1)
        row1col3.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)
        self.selectbutton = tk.Button(row1col3, text='Folder Selection', command=self.selectpath_entry)
        self.selectbutton.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X, padx=15)
        self.confirmbutton = tk.Button(row1col3, text="Confirm", width=10, command=self.init_creat_files)
        self.confirmbutton.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X, padx=15)

        # Second row display number
        row2 = tk.Frame(self)
        row2.pack(fill="x")

        row2col1 = tk.Frame(row2)
        row2col1.pack(expand=tk.YES, fill=tk.BOTH)
        tk.Label(row2col1, text="Tag progress：", width=10).pack(anchor=tk.W, expand=tk.NO, fill=None)
        row2col2 = tk.Frame(row2)
        row2col2.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)
        self.entry2 = tk.Entry(row2col2, textvariable=self.progress_count, width=30)
        self.entry2.pack(anchor=tk.W, fill=None, padx=5)

        # Third row  Canvas and file list
        row3 = tk.Frame(self)
        row3.pack(fill="x")
        # Third row first column
        row3col1 = tk.Frame(row3)
        row3col1.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)
        tk.Label(row3col1, text='The audio file to tag：').pack(anchor=tk.CENTER, side=tk.TOP)
        self.listbox = tk.Listbox(row3col1)
        self.listbox.pack(anchor=tk.CENTER, expand=tk.YES, side=tk.BOTTOM, fill=tk.Y)

        # Third row second column
        fig, self.ax = plt.subplots(1, 1)
        self.ax.set_xlabel('Time/s')
        self.ax.set_ylabel('Amplitude')
        self.row3col2 = tk.LabelFrame(row3, text='waveform：')
        self.row3col2.pack(padx=5, side=tk.RIGHT, expand=tk.YES, fill=tk.BOTH)
        self.canvas = FigureCanvasTkAgg(fig, master=self.row3col2)
        self.canvas.draw()
        self.canvas._tkcanvas.pack(anchor=tk.CENTER, side=tk.BOTTOM)

        # Fourth row
        row4 = tk.Frame(self)
        row4.pack(fill="x", pady=10)
        row4col1 = tk.Frame(row4)
        row4col1.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)
        tk.Label(row4col1, text="Emotion:", width=10, font=("times new roman", 16), ).pack(anchor=tk.W, expand=tk.NO,
                                                                                           fill=None, )

        for index, item in enumerate(label_item_list):
            row4col = tk.Frame(row4)
            row4col.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)
            tk.Radiobutton(row4col, text=item, variable=self.select_value, value=index + 1,
                           font=("times new roman", 16)).pack(anchor=tk.W, fill=None)

        # Fifth row, options(display,confirm,delete,save update,exit)
        row5 = tk.Frame(self)
        row5.pack(pady=20, fill="x")
        # Fifth row first column
        row5col1 = tk.Frame(row5)
        row5col1.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)
        self.playbutton = tk.Button(row5col1, font=15, text='display', height=2, width=10, command=self.wav_play_task)
        self.playbutton.pack(anchor=tk.W, expand=tk.NO, fill=None, padx=10)

        # Fourth row second columns
        row5col2 = tk.Frame(row5)
        row5col2.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)
        self.confirmbutton_label = tk.Button(row5col2, font=15, text='next', height=2, width=10,
                                             command=self.next_tagging)
        self.confirmbutton_label.pack(anchor=tk.W, padx=5, expand=tk.NO, fill=None)

        # Fifth row fifth column
        row5col5 = tk.Frame(row5)
        row5col5.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)
        self.exitbutton = tk.Button(row5col5, font=12, text='exit', height=2, width=10, command=lambda: sys.exit(0))
        self.exitbutton.pack(anchor=tk.W, padx=5, expand=tk.NO, fill=None)

    def wav_play_task(self):
        global bool_stop_play
        bool_stop_play = False
        t1 = Thread(target=wav_play, args=(self.current_wav_basename, self.wav_dir))
        t1.start()

    def selectpath_entry(self):
        def selectpath(path):
            path_ = askdirectory()
            path.set(path_)

        selectpath(self.recordings_path)

    def init_creat_files(self):
        # 1、Update listbox data content（File Mycheckfile.check_files）
        self.wav_dir = self.entry1.get()

        all_wav_paths = get_all_wav_paths(self.wav_dir)
        all_wav_basenames = [os.path.basename(x) for x in all_wav_paths]
        self.all_wav_paths = all_wav_paths

        label_txt_path = os.path.join(self.wav_dir, 'label.txt')

        tagged_files = []
        if os.path.exists(label_txt_path):
            with open(label_txt_path, "r", encoding="utf-8") as f:
                texts = f.readlines()
                texts = [line.rstrip() for line in texts]
                tagged_files = [line.split(":")[0] for line in texts]

        if len(all_wav_basenames) < len(tagged_files):
            tk.messagebox.showerror('warning', "Total number of audio in this folder is less than the number of tagged audio")
        elif len(all_wav_basenames) == len(tagged_files):
            tk.messagebox.showinfo('Notice', "Folder tag complete！")
        else:
            rest_files = list(set(all_wav_basenames) - set(tagged_files))
            self.progress_count.set(str(len(tagged_files)) + "/" + str(len(all_wav_basenames)))

            self.listbox.delete(0, tk.END)
            for item in rest_files:
                self.listbox.insert(tk.END, item)
            if self.listbox.size() > 0:
                self.listbox.select_set(0)

                # Select the first file by default proceed waveform display
                print(self.listbox.get(self.listbox.curselection()))
                # self.listbox.bind('<FocusIn>', self.wav_dis)
                self.wav_display(self.listbox.get(self.listbox.curselection()))
                # 2、when double click on items，display text，and update waveform
                self.listbox.bind('<Double-Button-1>', self.wav_display_choose)

    def wav_display(self, wav_name_get):
        # self.curwav_name = self.listbox.get(self.listbox.curselection())
        self.current_wav_basename = str(wav_name_get).split('\n')[0]

        # Update waveform graph
        self.current_wav_path = os.path.join(self.wav_dir, self.current_wav_basename)
        wav_path = self.current_wav_path

        try:
            self.current_wav_data, self.current_wav_time, current_wav_channel = wav_read(wav_path)
            # self.fig, self.ax = plt.subplots(1, 1)
            self.ax.clear()
            self.ax.plot(self.current_wav_time, self.current_wav_data, color='green')
            self.ax.set_xlabel('Time/s')
            self.ax.set_ylabel('Amplitude')
            plt.title(self.current_wav_basename)
            self.canvas.draw()

            # Double click to display audio
            # self.wav_dp()

        except Exception as e:
            tk.messagebox.showinfo('Notice', "Unable to display file" + str(e))

    def wav_display_choose(self, event):

        self.current_wav_basename = self.listbox.get(self.listbox.curselection())
        self.current_wav_basename = str(self.current_wav_basename).split('\n')[0]

        # Update waveform graph
        self.current_wav_path = os.path.join(self.wav_dir, self.current_wav_basename)
        wav_path = self.current_wav_path

        try:
            self.current_wav_data, self.current_wav_time, current_wav_channel = wav_read(wav_path)
            # self.fig, self.ax = plt.subplots(1, 1)
            self.ax.clear()
            self.ax.plot(self.current_wav_time, self.current_wav_data, color='green')
            self.ax.set_xlabel('Time/s')
            self.ax.set_ylabel('Amplitude')
            plt.title(self.current_wav_basename)
            self.canvas.draw()

        except Exception as e:
            tk.messagebox.showinfo('Notice', "Unable to display file" + str(e))

    def next_tagging(self):
        label = int(self.select_value.get())
        if label == 0:
            emotion = ""
        else:
            emotion = label_item_list[label - 1]

        print("Current tagging audio :{}, value:{},emotion:{}".format(self.current_wav_basename, label, emotion))
        if label == 0:
            tk.messagebox.showinfo('Notice', "Please select audio and first tag emotion")
        else:
            label_txt_path = os.path.join(self.wav_dir, 'label.txt')
            with open(label_txt_path, "a", encoding="utf-8") as f:
                f.write(self.current_wav_basename + ":" + emotion + "\n")

            global bool_stop_play
            bool_stop_play = True

            # Next audio
            self.select_value.set(0)

            index = int(self.listbox.curselection()[0])
            self.listbox.delete(index)
            if self.listbox.size() > 0:
                self.listbox.select_set(0)
                print(self.listbox.get(self.listbox.curselection()))
                self.wav_display(self.listbox.get(self.listbox.curselection()))
                self.progress_count.set(
                    str(len(self.all_wav_paths) - self.listbox.size()) + '/' + str(len(self.all_wav_paths)))
            else:
                self.progress_count.set(
                    str(len(self.all_wav_paths) - self.listbox.size()) + '/' + str(len(self.all_wav_paths)))
                tk.messagebox.showinfo('Notice', "folder annotated！")


if __name__ == "__main__":
    app = Tagging()
    app.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))
    app.mainloop()
