# Python program to create
# a file explorer in Tkinter
  
# import all components
# from the tkinter library
from tkinter import *
  
# import filedialog module
from tkinter import filedialog
from tkinter import messagebox
from PIL.ExifTags import TAGS
from PIL import Image as PILImage, ImageTk as PILImageTk
import htr
import result_displayer as rd
import os
import shutil

class ImageCropper:
    def __init__(self, parent_window, input_filename, root_label_file, root_filenames, root_file_number):
        self.root = Toplevel(parent_window)
        self.root.protocol("WM_DELETE_WINDOW", self.__on_closing)
        self.root.bind("<Button-1>", self.__on_mouse_down)
        self.root.bind("<ButtonRelease-1>", self.__on_mouse_release)
        self.root.bind("<B1-Motion>", self.__on_mouse_move)
        # self.root.bind("<Key>", self.__on_key_down)
        self.parent = parent_window
        self.parent.withdraw()
        self.message = None
        self.rectangle = None
        self.canvas_image = None
        self.canvas_message = None
        self.input_file = input_filename
        self.rlabel = root_label_file
        self.rfilenames = root_filenames
        self.rfilenum = root_file_number
        self.is_saved = False
        self.outputname = root_filenames[root_file_number - 1][ : root_filenames[root_file_number - 1].rfind('.')]
        self.box = [0, 0, 0, 0]
        self.previous_box = [0, 0, 0, 0]
        self.button_crop = Button(self.root, height = 5, text = "Crop image", command = self.__on_button_pressed)
        self.canvas = Canvas(self.root, highlightthickness = 0, bd = 0)

    def get_image_exif(self, image):
        if image is None:
            img_exif = None
        info = image._getexif()
        if info is not None:
            img_exif = {}
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                img_exif[decoded] = value
            return img_exif
        else:
            return None

    # def set_file(self, filename):
    #     self.files = []
    #     self.files.append(filename)

    # def set_directory(self, directory):
    #     if not os.path.isdir(directory):
    #         raise IOError(directory + ' is not a directory')
    #     files = os.listdir(directory)
    #     if len(files) == 0:
    #         print('No files found in ' + directory)
    #     self.files = []
    #     for filename in files:
    #         if filename[-11:] == 'cropped.jpg':
    #             print('Ignore ' + filename)
    #             continue
    #         self.files.append(os.path.join(directory, filename))

    def roll_image(self):
        self.set_image(self.input_file)
        #while len(self.files) > 0 and self.set_image(self.files.pop(0)) == False:
            #pass

    def rotate(self, image, exif):
        if exif is None:
            return image
        if exif['Orientation'] == 6:
            return image.rotate(90)
        if exif['Orientation'] == 8:
            return image.rotate(-90) 
        return image

    def set_ratio(self, ratio):
        self.ratio = float(ratio)

    def set_image(self, filename):

        if filename == None:
            return True

        self.filename = filename
        # self.outputname = 'tmp/' + filename[filename.rfind('/') + 1 : filename.rfind('.')] + '_cropped'
        try:
            self.img = PILImage.open(filename)
        except IOError:
            self.__on_closing()
            messagebox.showerror('Failure', 'The image is corrupted! Try another one.')
            print('Ignore: ' + filename + ' cannot be opened as an image')
            return False

        exif = self.get_image_exif(self.img)
        self.img = self.rotate(self.img, exif)
        # ratio = float(self.img.size[1]) / self.img.size[0]
        # FIX RESIZE
        if self.img.size[0] > 4096 or self.img.size[1] > 4096:
            self.__on_closing()
            messagebox.showerror('Size exceeded', "The image's size exceeds 4096 pixels in one or both of the axis! Crop the image before using it again.")
            return False
        self.scale = 1
        if self.img.size[0] > 1280:
            self.scale = self.img.size[0] / 1280
            self.img = self.img.resize((int(self.img.size[0] / self.scale), int(self.img.size[1] / self.scale)), PILImage.ANTIALIAS)
        if self.img.size[1] > 720:
            self.scale = self.img.size[1] / 720
            self.img = self.img.resize((int(self.img.size[0] / self.scale), int(self.img.size[1] / self.scale)), PILImage.ANTIALIAS)
        
        print(self.scale)
        #if self.img.size[0] > 1200:
        #    self.scale = self.img.size[0] / 1200
        #    self.resized_img = self.img.resize((int(self.img.size[0] / self.scale), int(self.img.size[1] / self.scale)), PILImage.ANTIALIAS)
        #if self.img.size[1] > 800:
        #    self.scale = self.img.size[1] / 800
        #    self.resized_img = self.img.resize((int(self.img.size[0] / self.scale), int(self.img.size[1] / self.scale)), PILImage.ANTIALIAS)
        #if self.img.size[0] <= 1200 and self.img.size[1] <= 800:
        #    self.resized_img = self.img
        #    self.scale = 1
        # self.img should be replaced with the scaled version of itself

        self.photo = PILImageTk.PhotoImage(self.img)
        self.canvas.delete(self.canvas_image)
        self.canvas.config(width = self.img.size[0], height = self.img.size[1])
        self.canvas_image = self.canvas.create_image(0, 0, anchor = NW, image = self.photo)
        self.canvas.pack(fill = BOTH, expand = YES)
        self.button_crop.pack(fill = X)
        self.root.update()

        return True

    def __on_closing(self):
        if self.is_saved:
            self.rlabel.configure(text=f"Image #{self.rfilenum}: " + self.input_file)
        else:
            self.rfilenames[self.rfilenum - 1] = ''
        self.parent.deiconify()
        self.root.destroy()

    def __on_mouse_down(self, event):
        self.previous_box = self.box.copy()
        self.box[0], self.box[1] = event.x, event.y
        self.box[2], self.box[3] = event.x, event.y
        print("top left coordinates: %s/%s" % (event.x, event.y))
        self.__refresh_rectangle()
        self.canvas.delete(self.message)

    def __on_mouse_release(self, event):
        print("bottom_right coordinates: %s/%s" % (self.box[2], self.box[3]))

    def __crop_image(self):
        if self.box[0] > self.box[2]:
            t = self.box[0]
            self.box[0] = self.box[2]
            self.box[2] = t
        if self.box[1] > self.box[3]:
            t = self.box[1]
            self.box[1] = self.box[3]
            self.box[3] = t
        box = (self.box[0], self.box[1], self.box[2], self.box[3])
        try:
            cropped = self.img
            if self.box[0] != self.box[2] and self.box[1] != self.box[3]:
                cropped = self.img.crop(box) 
            if cropped.size[0] == 0 and cropped.size[1] == 0:
                raise SystemError('no size')
            if not(os.path.exists('tmp/')):
                os.makedirs('tmp/')
            cropped.save(self.outputname + '.png', 'png')
            self.message = 'Saved: ' + self.outputname + '.png'
        except SystemError as e:
            print(e)

    def __fix_ratio_point(self, px, py):
        dx = px - self.box[0]
        dy = py - self.box[1]
        #if min((dy / self.ratio), dx) == dx:
        #    dy = int(dx * self.ratio)
        #else:
        #    dx = int(dy / self.ratio)
        return self.box[0] + dx, self.box[1] + dy


    def __on_mouse_move(self, event):
        self.box[2], self.box[3] = self.__fix_ratio_point(event.x, event.y)
        self.__refresh_rectangle()

    # def __on_key_down(self, event):
    #     print(event.char)
    #     if event.char == ' ':
    #         print(self.box)
    #         self.__crop_image()
    #         self.roll_image()
    #         self.canvas.delete(self.canvas_message)
    #         self.canvas_message = self.canvas.create_text(10, 10, anchor = NW, text = self.message, fill = 'red')
    #     elif event.char == 'q':
    #         self.parent.deiconify()
    #         self.root.destroy()
    
    def __on_button_pressed(self):
        self.box = self.previous_box.copy()
        self.__refresh_rectangle()
        self.__crop_image()
        self.roll_image()
        self.is_saved = True
        #self.canvas.delete(self.canvas_message)
        messagebox.showinfo('Success', 'The image has been successfully cropped!')
        # self.canvas_message = self.canvas.create_text(10, 10, anchor = NW, text = self.message, fill = 'red')

    def __refresh_rectangle(self):
        self.canvas.delete(self.rectangle)
        if self.box[0] != self.box[2] and self.box[1] != self.box[3]:
            self.rectangle = self.canvas.create_rectangle(self.box[0], self.box[1], self.box[2], self.box[3])

    def run(self):
        self.roll_image()
        # self.root.mainloop()

def button_browse1_proc():
    filename = filedialog.askopenfilename(initialdir = "/", title = "Select a File", filetypes = [("Image file", "*.png .jpg")])
    if filename != '':
        if filenames[0] != '' and os.path.exists(filenames[0]):
            os.remove(filenames[0])
        filenames_unmodified[0] = filename[filename.rfind('/') + 1 : filename.rfind('.')]
        filenames[0] = 'tmp/' + filename[filename.rfind('/') + 1 : filename.rfind('.')] + '_cropped1.png'
        # Change label contents
        # image_info = ImageInfo(filename = filenames[0])
        cropper = ImageCropper(root, filename, label_file1, filenames, 1)
        cropper.run()
        # if image_info.is_image_saved():
        #     label_file1.configure(text="Image #1: " + filename)
        # else:
        #     filenames[0] = ''

def button_browse2_proc():
    filename = filedialog.askopenfilename(initialdir = "/", title = "Select a File", filetypes = [("Image file", "*.png .jpg")])
    if filename != '':
        if filenames[1] != '' and os.path.exists(filenames[1]):
            os.remove(filenames[1])
        filenames_unmodified[1] = filename[filename.rfind('/') + 1 : filename.rfind('.')]
        filenames[1] = 'tmp/' + filename[filename.rfind('/') + 1 : filename.rfind('.')] + '_cropped2.png'
        # Change label contents
        cropper = ImageCropper(root, filename, label_file2, filenames, 2)
        cropper.run()

def button_browse3_proc():
    filename = filedialog.askopenfilename(initialdir = "/", title = "Select a File", filetypes = [("Image file", "*.png .jpg")])
    if filename != '':
        if filenames[2] != '' and os.path.exists(filenames[2]):
            os.remove(filenames[2])
        filenames_unmodified[2] = filename[filename.rfind('/') + 1 : filename.rfind('.')]
        filenames[2] = 'tmp/' + filename[filename.rfind('/') + 1 : filename.rfind('.')] + '_cropped3.png'
        # Change label contents
        cropper = ImageCropper(root, filename, label_file3, filenames, 3)
        cropper.run()

def button_browse4_proc():
    filename = filedialog.askopenfilename(initialdir = "/", title = "Select a File", filetypes = [("Image file", "*.png .jpg")])
    if filename != '':
        if filenames[3] != '' and os.path.exists(filenames[3]):
            os.remove(filenames[3])
        filenames_unmodified[3] = filename[filename.rfind('/') + 1 : filename.rfind('.')]
        filenames[3] = 'tmp/' + filename[filename.rfind('/') + 1 : filename.rfind('.')] + '_cropped4.png'
        # Change label contents
        cropper = ImageCropper(root, filename, label_file4, filenames, 4)
        cropper.run()

def button_browse5_proc():
    filename = filedialog.askopenfilename(initialdir = "/", title = "Select a File", filetypes = [("Image file", "*.png .jpg")])
    if filename != '':
        if filenames[4] != '' and os.path.exists(filenames[4]):
            os.remove(filenames[4])
        filenames_unmodified[4] = filename[filename.rfind('/') + 1 : filename.rfind('.')]
        filenames[4] = 'tmp/' + filename[filename.rfind('/') + 1 : filename.rfind('.')] + '_cropped5.png'
        # Change label contents
        cropper = ImageCropper(root, filename, label_file5, filenames, 5)
        cropper.run()

def button_process_proc():
    if filenames.count('') == 5:
        messagebox.showwarning('No images are given', 'No images were uploaded. Load at least one image to process!')
    else: 
        results = htr.run(filenames)
        rdisplayer = rd.ResultsDisplayer(root, filenames, filenames_unmodified, results)
        rdisplayer.run()

# def browseFiles():
#     filename = filedialog.askopenfilename(initialdir = "/", title = "Select a File", filetypes = [("Image file", "*.png .jpg")])
#       
#     # Change label contents
#     cropper = ImageCropper(root)
#     cropper.set_file(filename)
#     cropper.run()
#     label_file_explorer1.configure(text="File Opened: "+filename)
      
def on_closing():
    if os.path.exists('tmp/'):
        shutil.rmtree("tmp/")
    root.destroy()

filenames_unmodified = ['', '', '', '', '']
filenames = ['', '', '', '', '']                                                                                  

root = Tk()
root.protocol("WM_DELETE_WINDOW", on_closing)

root.title('Handwritten text recognizer')


root.geometry("600x600")

root.config(background = "white")

frame_containter = Frame(root)
#frame_containter.columnconfigure(0, weight = 3)
#frame_containter.columnconfigure(1, weight = 1)
frame_containter.config(background="white", highlightbackground="black", highlightthickness=1)

name_label = Label(root, text = "Upload up to 5 images to extract text from them", height = 5, fg = "black")
# Create a File Explorer label
frame1 = Frame(frame_containter)
frame1.columnconfigure(0, weight = 3)
frame1.columnconfigure(1, weight = 1)
frame1.config(highlightbackground="black", highlightthickness=1)
label_file1 = Label(frame1, text = "Choose image #1", height = 4, fg = "black")
button_explore1 = Button(frame1, text = "Choose image", command = button_browse1_proc)
label_file1.grid(row = 0, column = 0)
button_explore1.grid(row = 0, column = 1)
frame1.pack(fill = X, padx=5, pady=5)

frame2 = Frame(frame_containter)
frame2.columnconfigure(0, weight = 3)
frame2.columnconfigure(1, weight = 1)
frame2.config(highlightbackground="black", highlightthickness=1)
label_file2 = Label(frame2, text = "Choose image #2", height = 4, fg = "black")
button_explore2 = Button(frame2, text = "Choose image", command = button_browse2_proc)
label_file2.grid(row = 0, column = 0)
button_explore2.grid(row = 0, column = 1)
frame2.pack(fill = X, padx=5, pady=5)

frame3 = Frame(frame_containter)
frame3.columnconfigure(0, weight = 3)
frame3.columnconfigure(1, weight = 1)
frame3.config(highlightbackground="black", highlightthickness=1)
label_file3 = Label(frame3, text = "Choose image #3", height = 4, fg = "black")
button_explore3 = Button(frame3, text = "Choose image", command = button_browse3_proc)
label_file3.grid(row = 0, column = 0)
button_explore3.grid(row = 0, column = 1)
frame3.pack(fill = X, padx=5, pady=5)

frame4 = Frame(frame_containter)
frame4.columnconfigure(0, weight = 3)
frame4.columnconfigure(1, weight = 1)
frame4.config(highlightbackground="black", highlightthickness=1)
label_file4 = Label(frame4, text = "Choose image #4", height = 4, fg = "black")
button_explore4 = Button(frame4, text = "Choose image", command = button_browse4_proc)
label_file4.grid(row = 0, column = 0)
button_explore4.grid(row = 0, column = 1)
frame4.pack(fill = X, padx=5, pady=5)

frame5 = Frame(frame_containter)
frame5.columnconfigure(0, weight = 3)
frame5.columnconfigure(1, weight = 1)
frame5.config(highlightbackground="black", highlightthickness=1)
label_file5 = Label(frame5, text = "Choose image #5", height = 4, fg = "black")
button_explore5 = Button(frame5, text = "Choose image", command = button_browse5_proc)
label_file5.grid(row = 0, column = 0)
button_explore5.grid(row = 0, column = 1)
frame5.pack(fill = X, padx=5, pady=5)

button_process = Button(root, height = 5, text = "Process image(s)!", command = button_process_proc)

name_label.pack(fill = X)
frame_containter.pack(fill = X, padx = 5, pady = 5)
button_process.pack(fill = X, padx = 5)
# Grid method is chosen for placing
# the widgets at respective positions
# in a table like structure by
# specifying rows and columns


# Let the window wait for any events
root.mainloop()