#!/usr/bin/env python3
# Find out & Report Images/files as html
# Add Progress Bar to all Functions

from tkinter import *
from tkinter import filedialog, ttk
import sys, glob, os, re
import tarfile
import imghdr, shutil
import subprocess
from pathlib import Path
import collections
from PIL import Image
import PIL
from itertools import islice
from hashlib import md5
import imagehash
import time, random

root = Tk()

frame = Frame(root, height=800, width=700, bd=3, relief=RIDGE)
frame.grid()

def fullpath():
    if var2.get():
        for root,dir,fname in os.walk(en.get()):
            for file in fname:
                yield (os.path.join(root, file))
    else:
        for file in os.listdir(en.get()):
            if os.path.isfile(os.path.join(en.get(), file)):
                yield (os.path.join(en.get(), file))

def filesize(file):
    size = os.path.getsize(file)
    sizeinmb = size/1000000
    sizeflt = "{:.2f}".format(sizeinmb)
    return sizeflt

def lb(text):
    listbox.insert(END, text)
    listbox.yview(END)

def validate():
    if os.path.exists(en.get()):
        return True
    else:
        lb("Incorrect or No Path Entered")
        return False

def browse():
    try:
        dir = filedialog.askdirectory(parent=frame, initialdir='/data/.folder/', title='Please select a directory')
    except:
        dir = filedialog.askdirectory(parent=frame, initialdir=os.getcwd(), title='Please select a directory')
    en.delete(0,END)
    en.insert(0,dir)

def write():
    if var.get():
        return True
    else:
        lb("Write Access not enabled")
        return False

def ls():
    if validate():
        lb("File List:")
        for file in fullpath():
            name = os.path.relpath(file, en.get())
            lb(" - "+name)
    lb("")

def count():
    if validate():
        global leng
        x = []
        for file in fullpath():
            x.append(file)
        leng = len(x)
        lb("Count: "+str(leng))
        lb("")

def backup():
    if validate():
        try:
            os.mkdir("tmp")
        except Exception:
            pass
        tar = tarfile.open(os.path.join("tmp/" + "backup.tar.gz"), "w:gz")
        wr = open(os.path.join("tmp/" + "file_list.txt"), "w")
        wr.write("List of files:\n\n")
        frame.config(cursor="watch")
        frame.update()
        i = 1
        j = len([name for name in os.listdir(en.get()) if os.path.isfile(os.path.join(en.get(), name))])
        for name in fullpath():
            wr.write(name + '\n')
            tar.add(name)
            lb("File backup: "+name)
            bar['value'] = int(i/j*100)
            root.update_idletasks()
            i += 1
        frame.config(cursor="")
        wr.close()
        tar.close()
        lb("")

def missing():
    if validate():
        for file in fullpath():
            fn, ext = os.path.splitext(file)
            ftype = imghdr.what(file)
            if ftype == None:
                lb("Unsupported file")
            else:
                newname = file +"."+ ftype
                if not ext:
                    filechk = Path(newname)
                    if filechk.is_file():
                        lb(file+": File already EXISTS, not overwriting: "+str(filechk))
                    else:
                        lb(file+": has no ext, Appending: "+ftype)
                        if write():
                            shutil.move(file, newname)
                else:
                    continue
        lb("")

def correct():
    if validate():
        frame.config(cursor="watch")
        frame.update()
        for file in fullpath():
            # find the correct extension
            ftype = imghdr.what(file)
            ext = os.path.splitext(file)[1][1:]
            # find files with the (incorrect) extension to rename
            if ext:
                if ftype != ext:
                    if ftype != None:
                        #File type is JPG/JPEG, ignoring
                        if (ftype == "jpeg") & (ext == "jpg"):
                            continue
                        else:
                            filechk = file.replace(ext,ftype)
                            filechk2 = Path(filechk)
                            if filechk2.is_file():
                                lb(file+": File already EXISTS, not overwritting: "+str(filechk2))
                            else:
                                # rename the file
                                lb(file+ext+(" => ")+ftype)
                                if write():
                                    shutil.move(file, file.replace(ext,ftype))
                    else:
                        if ext == "png":
                            filechk = file.replace(ext,"jpg")
                            filechk2 = Path(filechk)
                            if filechk2.is_file():
                                lb(file+": File already EXISTS, not overwritting: "+filechk2)
                            else:
                                lb(file+": File type not determined for PNG => "+file.replace(ext,"jpg"))
                                if write():
                                    shutil.move(file, file.replace(ext,"jpg"))
                        else:
                            lb(file+": Could not determine file type.")
                else:
                    # Correct Extension
                    continue
            else:
                lb(file+": No Extension detected, Run Missing Extensions function.")
        frame.config(cursor="")
        lb("")

def webpconv():
    if validate():
        frame.config(cursor="watch")
        frame.update()
        for file in fullpath():
            name, ext = os.path.splitext(file)
            if ext == ".webp":
                fnpng = name + ".jpg"
                fpath = Path(fnpng)
                if fpath.is_file():
                    lb(file+"("+filesize(file)+"MB)"+": File already EXISTS, not overwritting: "+fnpng+"("+filesize(fnpng)+"MB)")
                else:
                    try:
                        if write():
                            im = Image.open(file).convert("RGB")
                            im.save(fnpng, "jpeg")
                            if fpath.is_file():
                                lb(file+"("+filesize(file)+"MB)"+" deleted and Converted file saved as: "+fnpng+"("+filesize(fnpng)+"MB)")
                                os.remove(file)
                            else:
                                lb(file+": Conversion to JPG failed")
                        else:
                            lb(file+"("+filesize(file)+"MB)"+" WILL BE deleted and Converted file TO BE saved as: "+name+".jpg")

                    except OSError as e:
                        lb(file+": Exception occured: "+str(e))
                        pass
                    except:
                        lb("Exception error occured when processing: "+file)
                        pass
            else:
                #File is not Webp, Skipping
                continue
        frame.config(cursor="")
        lb("")

def colonrep():
    if validate():
        for file in fullpath():
            if re.search(r':', file):
                filechk = file.replace(":","_")
                filechk2 = Path(filechk)
                if filechk2.is_file():
                    lb(file+": File already EXISTS, not overwriting: "+filechk2)
                else:
                    # rename the file
                    lb(file+(" Colon => ")+file.replace(":","_"))
                    if write():
                        shutil.move(file, file.replace(":","_"))
            else:
                lb("Colon not found in file: "+file.split('/')[-1])
        lb("")

def verify():
    if validate():
        try:
            lb("Initial Count: "+str(leng))
            x = []
            for file in fullpath():
                x.append(file)
            leng2 = len(x)
            lb("Final Count: "+str(leng2))
            if leng == leng2:
                lb("Operation completed successfully")
            else:
                lb("Operation failed, some files missing, Restore from backup !!!")
        except NameError:
            lb("Count function not used before operation, cannot use this feature now")

def delete():
    if validate():
        try:
            shutil.rmtree("tmp")
            lb("Backup Directory Deleted")
        except:
            lb("Backup not found")

def duplicate():
    if validate():
        frame.config(cursor="watch")
        frame.update()
        x,y = [],[]
        for file in fullpath():
            afile = open(file, 'rb')
            hasher = md5()
            buf = afile.read(65536)
            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(65536)
            afile.close()
            hash = hasher.hexdigest()
            y.append(hash)
            x.append(file)
        a = 1
        b = [item for item, count in collections.Counter(y).items() if count > 1]
        for i in range(len(b)):
            lb("Duplicate Set: "+ str(a))
            a += 1
            c = 0
            for j in range(len(y)):
                if b[i] == y[j]:
                    if c == 0:
                        lb("Original File: "+ x[j])
                        c += 1
                    else:
                        if write():
                            os.remove(x[j])
                            lb("Deleted duplicate file: "+ x[j])
                        else:
                            lb(x[j]+" WILL BE deleted")
        frame.config(cursor="")
        lb("")

def similar():
    if validate():
        frame.config(cursor="watch")
        frame.update()
        x,y,z,a = [],[],[],1
        for file in fullpath():
            try:
                hash = imagehash.whash(Image.open(file))
                x.append(file)
                y.append(hash)
            except OSError:
                pass
        c = [item for item, count in collections.Counter(y).items() if count > 1]
        for i in range(len(c)):
            for j in range(i+1, len(c)):
                    if abs(c[i] - c[j]) < 8:
                        z.append(c[i])
        for i in range(len(z)):
            try:
                c.remove(z[i])
            except:
                pass
        for i in range(len(c)):
            lb("Duplicate set:"+ str(a))
            a += 1
            for j in range(len(y)):
                if c[i]-y[j] < 8:
                    #print(x[j], " Factor:", c[i]-y[j])
                    lb("Dupes: "+ x[j] + " Factor: "+str(c[i]-y[j]))
        frame.config(cursor="")
        lb("")

def search():
    if validate():
        frame.config(cursor="watch")
        frame.update()
        currdir = os.getcwd()
        img = filedialog.askopenfilename(parent=frame, initialdir=currdir, title='Please select an image')
        hash1 = imagehash.whash(PIL.Image.open(img))
        x,y = [],[]
        for file in fullpath():
            hash = imagehash.whash(PIL.Image.open(file))
            x.append(file)
            y.append(hash)
        for i in range(len(x)):
            if not (img == x[i]):
                if y[i]-hash1 < 8:
                    lb(x[i]+" Factor: "+str(y[i]-hash1))
        frame.config(cursor="")
        lb("")

def stats():
    if validate():
        lb("Directory Stats are below:")
        x = []
        for file in fullpath():
                ext = os.path.splitext(file)[1][1:]
                x.append(ext)
        y = set(x)
        for i in y:
            lb(i+" : "+str(x.count(i)))
        lb("")

def top():
    if validate():
        frame.config(cursor="watch")
        frame.update()
        x = {}
        for file in fullpath():
            filesize = (os.path.getsize(file))
            relfile = os.path.relpath(file, en.get())
            x.update({relfile: filesize})
        # Limit iterations to 10 or less in case lesser no of files
        if (len(x) < 10):
            a = len(x)
        else:
            a = 10
        for i in range(a):
            key, value = max(x.items(), key = lambda p: p[1])
            sizeinmb = (value/1000000)
            sizeflt = "{:.2f}".format(sizeinmb)
            lb(key+" => "+sizeflt+"MB")
            x.pop((max(x, key=x.get)))
        frame.config(cursor="")
        lb("")

def hugepng():
    if validate():
        frame.config(cursor="watch")
        frame.update()
        x = {}
        for file in fullpath():
            filesz = (os.path.getsize(file))
            name, ext = os.path.splitext(file)
            # search huge PNG Files
            if (ext == ".png")|(ext == ".PNG") & (filesz > 1000000):
                fnpng = name + ".jpg"
                fpath = Path(fnpng)
                if fpath.is_file():
                    lb(file+"("+filesize(file)+"MB)"+ ": File already EXISTS, not overwritting: "+ fnpng+ "("+filesize(fnpng)+"MB)" )
                else:
                    try:
                        if write():
                            im = Image.open(file).convert("RGB")
                            im.save(fnpng, "jpeg")
                            if fpath.is_file():
                                lb(file+"("+filesize(file)+"MB)"+ " deleted and Converted file saved as: "+ fnpng+ "("+filesize(fnpng)+"MB)")
                                os.remove(file)
                            else:
                                lb(file+": Conversion to JPG failed")
                        else:
                            lb(file+"("+filesize(file)+"MB)"+" WILL BE deleted and Converted file TO BE saved as: "+fnpng)
                    except OSError as e:
                        lb(file+": Exception occured: "+str(e))
                        pass
                    except:
                        lb("Exception error occured when processing: "+file)
                        pass
            else:
                #File is not Huge PNG, Skipping
                continue
        frame.config(cursor="")
        lb("")

def clear():
    listbox.delete(0, END)

Label(frame, text="File Extension Doctor", font=("Times", 35), width=20).grid(row=0, columnspan=6)
en = Entry(frame, width=60)
en.grid(row=1, column=0,columnspan=4)
en.focus_set()

Button(frame, text="Browse", width=20, command=browse).grid(row=1, column=3)

var = IntVar()
c = Checkbutton(frame, text="Write Access", variable=var)
c.grid(row=1, column=4, rowspan=1, columnspan=1)

var2 = IntVar()
d = Checkbutton(frame, text="Recursive", variable=var2)
d.grid(row=1, column=5, rowspan=1, columnspan=1)

frame.grid_rowconfigure(2, minsize=20)

Button(frame, text="Show Files", width=20, command=ls).grid(row=3, column=0)
Button(frame, text="Count of Files", width=20, command=count).grid(row=4, column=0)
Button(frame, text="Backup Files", width=20, command=backup).grid(row=5, column=0)
Button(frame, text="Missing Extensions", width=20, command=missing).grid(row=6, column=0)
Button(frame, text="Correct Extensions", width=20, command=correct).grid(row=7, column=0)
Button(frame, text="Webp Convert", width=20, command=webpconv).grid(row=8, column=0)
Button(frame, text="Replace Colon", width=20, command=colonrep).grid(row=9, column=0)
Button(frame, text="Verify Files", width=20, command=verify).grid(row=10, column=0)
Button(frame, text="Delete Backups", width=20, command=delete).grid(row=11, column=0)
Button(frame, text="Delete Duplicate", width=20, command=duplicate).grid(row=12, column=0)
Button(frame, text="Find Similar Images", width=20, command=similar).grid(row=13, column=0)
Button(frame, text="Image Search", width=20, command=search).grid(row=14, column=0)
Button(frame, text="Show Stats", width=20, command=stats).grid(row=15, column=0)
Button(frame, text="Top 10 Files", width=20, command=top).grid(row=16, column=0)
Button(frame, text="Huge PNG Convertor", width=20, command=hugepng).grid(row=17, column=0)
Button(frame, text="Clear Log Output", width=20, command=clear).grid(row=18, column=0)
Button(frame, text="Exit", width=20, command=exit).grid(row=19, column=0)

frame.grid_rowconfigure(7, minsize=20)
frame.grid_columnconfigure(1, minsize=10)

scrollbar = Scrollbar(frame, orient=VERTICAL)
listbox = Listbox(frame, height=30, width=140, yscrollcommand=scrollbar.set)
listbox.xview_scroll(3, "pages")
listbox.yview_scroll(3, "pages")
scrollbar.config(command=listbox.yview)
scrollbar.grid(row=3, column=8, rowspan=17, columnspan=1, ipady = 226)
listbox.grid(row=3, column=2, rowspan=17, columnspan=6)

lb("Ready, Log Output: ")

# Progress Bar
bar = ttk.Progressbar(frame, length=700)
bar.grid(row=20,column=2)

root.title("Correct extensions of multiple files")

img = PhotoImage(file='icon.png')
root.tk.call('wm', 'iconphoto', root._w, img)
root.mainloop()


