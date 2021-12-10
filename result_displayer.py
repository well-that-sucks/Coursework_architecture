from tkinter import Frame, Toplevel, messagebox
from PIL import Image as PILImage, ImageTk as PILImageTk
from functools import partial

from tkinter import *

import os

class ResultsDisplayer:
    def __init__(self, parent_window, filenames, filenames_unmodified, results):
        self.root = Toplevel(parent_window)
        self.root.protocol("WM_DELETE_WINDOW", self.__on_closing)
        self.parent = parent_window
        self.parent.withdraw()
        self.filenames = filenames
        self.filenames_unmodified = filenames_unmodified
        self.results = results
        self.photos = []
    
    def __on_closing(self):
        self.parent.deiconify()
        self.root.destroy()

    def __on_button_click(self, filename, text_widget):
        result_filename = "results/" + filename + "_result"
        text = text_widget.get("1.0", END)

        if not os.path.exists(os.path.dirname(result_filename)):
            try:
                os.makedirs(os.path.dirname(result_filename))
            except OSError as exc: # Guard against race condition
                print("Error while creating directory")

        if os.path.exists(result_filename + ".txt"):
            i = 1
            while os.path.exists(result_filename + f"{i}.txt"):
                i += 1
            with open(result_filename + f"{i}.txt", "w+") as text_file:
                text_file.write(text)
                messagebox.showinfo('Success', 'The result has been successfully saved!')
        else:
            #save text
            with open(result_filename + ".txt", "w+") as text_file:
                text_file.write(text)

    def draw(self):
        i = 0
        for idx, filename in enumerate(self.filenames):
            if filename != '':
                frame = Frame(self.root)
                canvas = Canvas(frame, highlightthickness = 0, bd = 0)
                img_raw = PILImage.open(filename)
                scale = img_raw.size[0] / 800
                img_resized = img_raw.resize((int(800), int(img_raw.size[1] / scale)), PILImage.ANTIALIAS)
                img = PILImageTk.PhotoImage(img_resized)
                self.photos.append(img)
                canvas.config(width = img_resized.size[0], height = img_resized.size[1])
                print(img_resized.size[0], img_resized.size[1])
                canvas.create_image(0, 0, anchor = NW, image = self.photos[i])
                #canvas.create_image(img_raw.size[0]/2, 0, anchor=CENTER, image = self.photos[i])
                result_text = Text(frame, height = 5)
                result_text.insert(END, self.results[i])
                button_save = Button(frame, height = 3, text = "Save result", command = partial(self.__on_button_click, self.filenames_unmodified[idx], result_text))
                canvas.grid(row = 0, column = 0)
                result_text.grid(row = 1, column = 0, sticky = "nsew")
                button_save.grid(row = 2, column = 0, sticky = "nsew")
                #canvas.pack(fill = BOTH, expand = 1)
                #result_text.pack()
                frame.pack(fill = X, padx = 10, pady = 10)
                i += 1
                # self.root.update()

    def run(self):
        self.draw()