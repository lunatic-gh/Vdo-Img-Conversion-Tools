import tkinter
import customtkinter as ctk
import os
import sys
import webbrowser
import cv2
import threading

if ctk.get_appearance_mode()=="Dark":
    o = 1
else:
    o = 0
    
def openfile():
    global file, files, batch_convert
    files = tkinter.filedialog.askopenfilenames(filetypes =[('Video', ['*.mp4','*.avi','*.mov','*.mkv','*gif']),('All Files', '*.*')])
    if files:
        if len(files)==1:
            file = files[0]
            if len(os.path.basename(file))>=20:
                open_button.configure(fg_color="grey50", text=os.path.basename(file)[:15]+"..."+os.path.basename(file)[-3:])               
            else:
                open_button.configure(fg_color="grey50", text=os.path.basename(file))
            batch_convert = False
        else:
            open_button.configure(fg_color="grey50", text=str(len(files))+" videos selected")
            batch_convert = True
    else:
        open_button.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"][o], text="Import Video")

def folder_name():
    global folder
    base_name = os.path.basename(file).split('.')[0]
    path1 = os.path.dirname(file)
    folder = os.path.join(path1, base_name + "-Image_sequence")
    
    n=1
    while True:
        if os.path.exists(folder):
            folder = os.path.join(path1, base_name + "-Image_sequence_"+str(n))
            n+=1
        else:
            break

def process():
    global file, running
    if not files:
        return
    if batch_convert:
        res = tkinter.messagebox.askquestion("Extract?", "Do you want to extract the image sequences from these videos?")       
        if res=="yes":
            pass
        else:
            return     
        for i in files:
            if running is False:
                break
            file = i
            open_button.configure(fg_color="grey50", text=str(len(files))+" videos selected \nVideo Number: "+str(files.index(i)+1))
            convert()
        open_button.configure(fg_color="grey50", text=str(len(files))+" videos selected")  
        tkinter.messagebox.showinfo("DONE", "Frames extracted! \nPlease check the respected folders.")
    else:
        convert()
    running = True
    
def convert():
    global running
    if not file:
        return
    
    folder_name()
    
    if not batch_convert:     
        res = tkinter.messagebox.askquestion("Extract?", "Do you want to extract the image sequence? \nFolder Name: " + folder)
        
        if res=="yes":
            pass
        else:
            return
    
    open_button.configure(state="disabled")
    extract_button.configure(state="disabled")
    progressbar.grid(row=4, column=1, padx=20, pady=20, sticky="we")
    
    cam = cv2.VideoCapture(file)
    currentframe = 0
    os.mkdir(folder)
    total_frames = int(cam.get(cv2.CAP_PROP_FRAME_COUNT))
    targetformat = exportbox.get()
    running = True
    
    try:
        while True:
            if running is False:
                break
            ret, frame = cam.read()
            if ret:
                N = 4
                name = os.path.join(folder, str(currentframe) +"."+ targetformat)
                cv2.imwrite(name, frame)
                currentframe += 1
                progressbar.set(currentframe/total_frames)
            else:
                break
        cam.release()
        if not batch_convert:
            tkinter.messagebox.showinfo("DONE", "Frames extracted! \nPlease check the folder: " + folder)
    except:
        cam.release()
        tkinter.messagebox.showerror("ERROR", "Something went wrong!")
        
    progressbar.grid_forget()
    open_button.configure(state="normal")
    extract_button.configure(state="normal")
    
def do_popup(event, frame):
    try:
        frame.tk_popup(event.x_root, event.y_root)
        extract_button.configure(state="disabled")
    finally:
        frame.grab_release()
        extract_button.configure(state="normal")
        
def extract_one_frame():
    global file
    if not files:
        return
    
    dialog = ctk.CTkInputDialog(text="Enter Frame Number")
    dialog.title("Extract Specific Frame")
    
    frame_num = dialog.get_input()
    
    if frame_num is None or frame_num=="":
        return
    
    if not frame_num.isdigit():
        tkinter.messagebox.showwarning("!!!", "Frame number not valid!")
        return
        
    if batch_convert:
        save_folder = tkinter.filedialog.askdirectory()
        if not save_folder:
            return

        extracted = False
        for i in files:
            file = i
            cam = cv2.VideoCapture(file)
            total_frames = int(cam.get(cv2.CAP_PROP_FRAME_COUNT))-1
            if int(frame_num)>total_frames:
                print("Frame Number " + frame_num + " is not available in " + os.path.basename(file))
                continue
            save_as = os.path.join(save_folder, os.path.basename(file)[:-4]+"_frame-"+frame_num+"."+exportbox.get())
            try:
                cam.set(1, int(frame_num))
                ret, frame = cam.read()
                if ret:
                    cv2.imwrite(save_as, frame)
                cam.release()
            except:
                pass
            extracted = True
            
        if extracted:      
            tkinter.messagebox.showinfo("DONE", "Frame "+ frame_num +" extracted for the selected videos!")
        else:
            tkinter.messagebox.showwarning("!!!", "Frame number not valid for these videos!")
        return
    
    cam = cv2.VideoCapture(file)
    total_frames = int(cam.get(cv2.CAP_PROP_FRAME_COUNT))-1
    
    if int(frame_num)>total_frames:
        tkinter.messagebox.showwarning("!!!", "Frame number not valid!")
        cam.release()
        return
    
    save_as = tkinter.filedialog.asksaveasfilename(filetypes =[('Image', ['*.png','*.jpg','*.bmp'])],
                                                 initialfile=os.path.basename(file)[:-4]+"_frame-"+frame_num+"."+exportbox.get())
    try:
        if save_as:
            cam.set(1, int(frame_num))
            ret, frame = cam.read()
            if ret:
                cv2.imwrite(save_as, frame)
            tkinter.messagebox.showinfo("DONE", "Frame "+ frame_num +" extracted!")
        cam.release()
    except:
        cam.release()
        tkinter.messagebox.showerror("ERROR", "Something went wrong!")
        
        
def stop_process():
    global running
    running = False
    
def open_info():
    # About window 
    header.configure(state="disabled")
    
    def open_program():
        ch = "Img-to-Vdo.py"
        root.destroy()
        os.system('"%s"' % ch)     
            
    def exit_top_level():
        top_level.destroy()
        header.configure(state="normal")
        
    def web(link):
        webbrowser.open_new_tab(link)
        
    top_level = ctk.CTkToplevel(root)
    top_level.protocol("WM_DELETE_WINDOW", exit_top_level)
    top_level.title("About")
    top_level.attributes("-topmost", True)
    top_level.resizable(width=False, height=False)
    top_level.wm_iconbitmap("Programicon.ico")
    
    label_top = ctk.CTkLabel(top_level, text="VDO-IMG TOOLS", font=("Roboto",15))
    label_top.grid(padx=20, pady=(20,0), sticky="w")
        
    desc = "\n\nDeveloped by Akash Bora (Akascape)"
    
    label_disc = ctk.CTkLabel(top_level,  text=desc, justify="left", font=("Roboto",12))
    label_disc.grid(padx=20, pady=0, sticky="wn")
    
    link = ctk.CTkLabel(top_level, text="Official Page", justify="left", font=("",13), text_color="#1f6aa5")
    link.grid(padx=20, pady=0, sticky="wn")   
    link.bind("<Button-1>", lambda event: web("https://github.com/Akascape/Vdo-Img-Conversion-Tools"))
    link.bind("<Enter>", lambda event: link.configure(font=("", 13, "underline"), cursor="hand2"))
    link.bind("<Leave>", lambda event: link.configure(font=("", 13), cursor="arrow"))
    
    button_switch = ctk.CTkButton(top_level, text="Open IMG-TO-VDO", fg_color=ctk.ThemeManager.theme["CTkTextbox"]["fg_color"][o],
                        text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"][o], command=open_program)
    button_switch.grid(padx=20, pady=(10,20))
    
root= ctk.CTk()
root.geometry("450x240")
root.title("Vdo & Img Tools")
root.resizable(width=False, height=False)
root.columnconfigure((0,1),weight=1)
root.rowconfigure((0,1,2,3,4),weight=1)
root.wm_iconbitmap("Programicon.ico")
root.bind('<Escape>', lambda e: stop_process())

file = ""
files = ""
running = True

header = ctk.CTkButton(root, text="VDO TO IMG CONVERTER", fg_color=ctk.ThemeManager.theme["CTkTextbox"]["fg_color"][o],
                       text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"][o], command=open_info)
header.grid(row=0, column=1, pady=(10,0))

open_button = ctk.CTkButton(root, text="Import Video", command=openfile)
open_button.grid(row=0, column=0, rowspan=5, sticky="nsew", padx=20, pady=20)

label_2 = ctk.CTkLabel(root, text="Choose Format")
label_2.grid(row=1, column=1, pady=0)

exportchoices = ["jpg","png","bmp"]
exportbox = ctk.CTkComboBox(root, values=exportchoices, state="readonly")
exportbox.set("png")
exportbox.grid(row=2, column=1, sticky="we", padx=20)

extract_button = ctk.CTkButton(root, text="EXTRACT", command=lambda: threading.Thread(target=process).start())
extract_button.grid(row=3, column=1, padx=20, pady=(10,0), sticky="we")

RightClickMenu = tkinter.Menu(root, tearoff=False, background=ctk.ThemeManager.theme["CTkFrame"]["fg_color"][o],
                              fg=ctk.ThemeManager.theme["CTkLabel"]["text_color"][o], borderwidth=0, bd=0)
RightClickMenu.add_command(label="Extract specific frame", command=lambda: extract_one_frame())

extract_button.bind("<Button-3>", lambda event: do_popup(event, frame=RightClickMenu))

progressbar = ctk.CTkProgressBar(root, width=100, bg_color="transparent")
progressbar.set(0)

root.mainloop()
