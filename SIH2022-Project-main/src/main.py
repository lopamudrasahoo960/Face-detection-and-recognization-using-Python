from tkinter import *
from PIL import Image, ImageTk, ImageDraw, ImageFont
from tkinter import ttk, Canvas, filedialog
import tkinter.messagebox
import cv2
import customtkinter
import face_recognition
from fpdf import FPDF
import os
from datetime import datetime
import threading
import time
import random
import string



def seperate(imagePath, dir, grp):
    image = cv2.imread(imagePath)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faceCascade = cv2.CascadeClassifier("assets/xml/haarcascade_frontalface_default.xml")
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.3,
        minNeighbors=6,
        minSize=(30, 30)
    )

    if grp:
        print(f"[INFO] Found {len(faces)} Faces.")

    file_name = None

    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        roi_color = image[y:y + h, x:x + w]
        if grp:
            print("[INFO] Object found. Saving locally.")
        name = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))
        file_name = dir + name + '_face.jpg'
        cv2.imwrite(file_name, roi_color)
    
    if grp:
        status = cv2.imwrite("faces_detected.jpg", image)
        print("[INFO] Image faces_detected.jpg written to filesystem: ", status)
    
    return file_name

def saved(date):
    time.sleep(3)
    tkinter.messagebox.showinfo("Alert", f"Saved attenedence pdf successfully!\nas: result_{date}.pdf")

def core(work):
    if work == "fill_db":
        file_paths = filedialog.askopenfilenames(initialdir="/Users/xy0ke/Downloads/", filetypes=[("Image files", ".jpg .png .jpeg")])

        for path in file_paths:
            seperate(path, dir="worker_db/", grp=False)

        tkinter.messagebox.showinfo("Alert", "Photo saved successfully to Database!")
    elif work == "upload_grp":
        file_path = filedialog.askopenfilename(initialdir="/Users/xy0ke/Downloads/", filetypes=[("Image files", ".jpg .png .jpeg")])
        seperate(file_path, dir="group_photo/", grp=True)
        group = Image.open("faces_detected.jpg")
        resize_group = group.resize((400, 280))
        grp = ImageTk.PhotoImage(resize_group)

        B2.pack_forget()
        L2.pack_forget()

        grp_vw = Label(tab2, image=grp)
        grp_vw.photo = grp
        grp_vw.pack(padx=281.5, pady=30)
        
        B3.pack(pady=0)

    elif work == "check_atendence":
        B3.pack_forget()
        print("[INFO] Checking for attendence...")

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size = 15)
        pdf.set_fill_color(0, 255, 0)

        c = 0

        list_present_1 = []
        list_present_2 = []
        list_absent = []

        for worker in os.listdir(worker_photos):
            for member in os.listdir(group_photos):
                if member.endswith((".png", ".jpg", ".jpeg")) or worker.endswith((".png", ".jpg", ".jpeg")):
                    member_photo = group_photos + member
                    worker_photo = worker_photos + worker
                    print(worker_photo)
                    print(member_photo)
                
                    picture_of_member = face_recognition.load_image_file(member_photo)
                    member_face_encoding = face_recognition.face_encodings(picture_of_member)[0]
                    picture_of_worker = face_recognition.load_image_file(worker_photo)
                    worker_face_encoding = face_recognition.face_encodings(picture_of_worker)[0]

                    results = face_recognition.compare_faces([member_face_encoding], worker_face_encoding)


                    if results[0] == True:
                        list_present_1.append(member_photo)
                        list_present_2.append(worker_photo)
                    else:
                        list_absent.append(member_photo)
                        

        for i in list_present_1:
            for j in list_absent:
                if i == j:
                    list_absent.remove(i)
        
        list_present_2 = list(set(list_present_2))
        list_present_1 = list(set(list_present_1))
        list_absent = list(set(list_absent))

        c = 0
        lp = 0

        for l in list_present_1:
            img_01 = Image.open(l)
            w = list_present_2[lp]
            lp += 1
            img_02 = Image.open(w)

            img_01 = img_01.resize((70, 70))
            img_02 = img_02.resize((70, 70))

            new_im = Image.new('RGB', (500, 70), (153, 255, 102))

            new_im.paste(img_01, (0,0))
            new_im.paste(img_02, (430,0))

            d1 = ImageDraw.Draw(new_im)
            fontx = ImageFont.truetype('assets/arial.ttf', 30)
            d1.text((200, 20), "Present", font=fontx, fill=(255, 255, 255))
            new_im.save(f"res{c}_img.jpeg", "JPEG")
            res_img = f"res{c}_img.jpeg"

            pdf.image(res_img)
            c += 1
        
        for k in list_absent:
            img_01 = Image.open(k)
            img_01 = img_01.resize((70, 70))

            new_im = Image.new('RGB', (500, 70), (255, 0, 0))

            new_im.paste(img_01, (0,0))

            d1 = ImageDraw.Draw(new_im)
            fontx = ImageFont.truetype('assets/arial.ttf', 30)
            d1.text((200, 20), "Absent", font=fontx, fill=(255, 255, 255))
            new_im.save(f"res{c}_img.jpeg", "JPEG")
            res_img = f"res{c}_img.jpeg"

            pdf.image(res_img)
            c += 1
        

        
        date = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
        pdf.output(f"result_{date}.pdf", "F")
        print("Attendence checked successfully!")

        k = 0

        while True:
            try:
                os.remove(f"res{k}_img.jpeg")
                k += 1
            except:
                break

        threading.Thread(target=saved, args=(date, )).start()

        dirx = "group_photo"
        for f in os.listdir(dirx):
            os.remove(os.path.join(dirx, f))



if __name__ == '__main__':

    root = Tk()
    root.title("Smart India Hackathon")

    root.geometry("1100x650")

    group_photos = "group_photo/"
    worker_photos = "worker_db/"


    tabControl = ttk.Notebook(root)

    tab1 = Frame(tabControl)
    tab2 = Frame(tabControl)
    tab3 = Frame(tabControl)

    tabControl.add(tab1, text ='Dashboard')
    tabControl.add(tab2, text ='Attendence')
    tabControl.add(tab3, text ='Help')
    tabControl.pack(expand = 1, fill ="both")

    image = Image.open("assets/upload.jpg")
    resize_image = image.resize((480, 280))
    img = ImageTk.PhotoImage(resize_image)
    
    


    B1 = Button(tab1, image=img, command=lambda: core(work="fill_db"))
    B1.pack(padx=281.5, pady=30)

    L1 = Label(tab1, text = "Add photos to save in the database of images\n")
    L1.pack(pady=0)

    B2 = Button(tab2, image=img, command=lambda: core(work="upload_grp"))
    B2.photo = img
    B2.pack(padx=281.5, pady=30)

    B3 = customtkinter.CTkButton(tab2, text="Check", command=lambda: core(work="check_atendence"))

    L2 = Label(tab2, text = "Add group photo to check for attendence\n")
    L2.pack(pady=0)

    Help = Label(tab3, text = "* This software is made for Ministery of Rural Development for MGNREGA Attendence. This software is developed by team Debug or die!\nThis software is solely owned by Rishub Kumar(Team leader)")
    Help.pack(padx = 30, pady = 30)


    root.mainloop()
