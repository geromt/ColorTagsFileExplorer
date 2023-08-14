import subprocess
import sys
from tkinter import *
import os
import ctypes
import pathlib

root = Tk()
# set a title for our file explorer main window
root.title('Simple Explorer')

root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(1, weight=1)


def pathChange(*event):
    # Get all Files and Folders from the given Directory
    directory = os.listdir(currentPath.get())
    # Clearing the list
    list.delete(0, END)
    # Inserting the files and directories into the list
    print(current_files_dict)
    for file in directory:
        file_path = os.path.join(currentPath.get(), file)
        if file_path in current_files_dict:
            if current_files_dict[file_path] == 1:
                list.insert(0, file)
                list.itemconfig(index=0, bg="#74FA46")
            elif current_files_dict[file_path] == 2:
                list.insert(0, file)
                list.itemconfig(index=0, bg="red")
            else:
                list.insert(0, file)
                list.itemconfig(index=0, bg="white")
        else:
            list.insert(0, file)
            list.itemconfig(index=0, bg="white")
            current_files_dict[file_path] = 0


def change_path_by_click(event=None):
    # Get clicked item.
    picked = list.get(list.curselection()[0])
    # get the complete path by joining the current path with the picked item
    path = os.path.join(currentPath.get(), picked)
    # Check if item is file, then open it
    if os.path.isfile(path):
        print('Opening: '+path)
        if sys.platform == "win32":
            os.startfile(path)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, path])
    # Set new path, will trigger pathChange function.
    else:
        currentPath.set(path)


def go_back(event=None):
    # get the new path
    newPath = pathlib.Path(currentPath.get()).parent
    # set it to currentPath
    currentPath.set(newPath)
    # simple message
    print('Going Back')


def open_popup():
    global top
    top = Toplevel(root)
    top.geometry("250x150")
    top.resizable(False, False)
    top.title("Child Window")
    top.columnconfigure(0, weight=1)
    Label(top, text='Enter File or Folder name').grid()
    Entry(top, textvariable=newFileName).grid(column=0, pady=10, sticky='NSEW')
    Button(top, text="Create", command=newFileOrFolder).grid(pady=10, sticky='NSEW')


def change_color(event=None):
    print("Cambia color de elemento")
    for i in list.curselection():
        file_state = current_files_dict[os.path.join(currentPath.get(), list.get(i))]
        if file_state == 0:
            list.itemconfig(index=i, bg="#74FA46")
            current_files_dict[os.path.join(currentPath.get(), list.get(i))] = 1
        elif file_state == 1:
            list.itemconfig(index=i, bg="red")
            current_files_dict[os.path.join(currentPath.get(), list.get(i))] = 2
        elif file_state == 2:
            list.itemconfig(index=i, bg="white")
            current_files_dict[os.path.join(currentPath.get(), list.get(i))] = 0
        list.select_clear(i)

    # picked.configure(bg="red")
    # event.widget.configure(bg="red")


def newFileOrFolder():
    # check if it is a file name or a folder
    if len(newFileName.get().split('.')) != 1:
        open(os.path.join(currentPath.get(), newFileName.get()), 'w').close()
    else:
        os.mkdir(os.path.join(currentPath.get(), newFileName.get()))
    # destroy the top
    top.destroy()
    pathChange()

top = ''

current_files_dict = {}
# String variables
newFileName = StringVar(root, "File.dot", 'new_name')
currentPath = StringVar(
    root,
    name='currentPath',
    value=pathlib.Path.cwd()
)
# Bind changes in this variable to the pathChange function
currentPath.trace('w', pathChange)

Button(root, text='Folder Up', command=go_back).grid(
    sticky='NSEW', column=0, row=0
)
# Keyboard shortcut for going up
root.bind("<Alt-Up>", go_back)
Entry(root, textvariable=currentPath).grid(
    sticky='NSEW', column=1, row=0, ipady=10, ipadx=10
)

# List of files and folder
list = Listbox(root, selectmode="extended")
list.grid(sticky='NSEW', column=1, row=1, ipady=10, ipadx=10)
# List Accelerators
list.bind('<Double-1>', change_path_by_click)
list.bind('<Return>', change_path_by_click)
list.bind("<Button-2>", change_color)
list.bind("<Button-3>", change_color)

# Menu
menubar = Menu(root)
# Adding a new File button
menubar.add_command(label="Add File or Folder", command=open_popup)
# Adding a quit button to the Menubar
menubar.add_command(label="Quit", command=root.quit)
# Make the menubar the Main Menu
root.config(menu=menubar)

# Call the function so the list displays
pathChange('')
# run the main program
root.mainloop()

#ctypes.windll.shcore.SetProcessDpiAwareness(True)