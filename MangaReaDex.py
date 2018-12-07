import requests
import re
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from time import sleep
from tkinter import *
from PIL import Image, ImageTk

class MainGUI():

    def __init__(self, root):
        self.root = root

        self.create_gui()

    def create_gui(self):
        self.root.title("Mangareader v1.0 - By Nadhif")
        self.root.geometry("1300x1080")

        self.header = Frame(self.root, height=100, width=1300)
        self.body = Frame(self.root, height=930, width=1300)
        self.footer = Frame(self.root, height=50, width=1300)

        self.header.pack()
        self.body.pack()
        self.footer.pack()

        manga_label = Label(self.header, text="Enter your manga title")
        chapter_label = Label(self.header, text="Enter your chapter number")

        self.manga_entry = Entry(self.header)
        self.chapter_entry = Entry(self.header)

        manga_label.pack()
        self.manga_entry.pack()
        chapter_label.pack()
        self.chapter_entry.pack()

        left_button = Button(self.header, text="<-", command=self.event_handler1)
        right_button = Button(self.header, text="->", command=self.event_handler)

        left_button.pack(side=LEFT)
        right_button.pack(side=RIGHT)


        scrollbar = Scrollbar(self.body, orient=VERTICAL)
        

        self.manga_entry.bind('<Return>', self.make_image)
        self.chapter_entry.bind('<Return>', self.make_image)

        self.root.bind('<Right>', self.event_handler)
        self.root.bind('<Left>', self.event_handler1)

        img = ImageTk.PhotoImage(file="mangareadex.png")
        self.image = Canvas(self.body, width=930, height=1200, scrollregion=(0,0,900,1400))
        scrollbar.config(command=self.image.yview)
        self.image.config(yscrollcommand=scrollbar.set)
        self.image.image = self.image.create_image(500, 650, image=img)
        self.image.img = img
        self.image.pack(side=LEFT)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        

    def mainloop(self):
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        self.root.mainloop()

    def quit(self):
        try:
            self.root.destroy()
            self.manga.driver.quit()
        except Exception:
            pass

    def make_image(self, event):
        manga = self.manga_entry.get()
        chapter = self.chapter_entry.get()  
        
        
        self.manga = Manga(manga, chapter, self.image)
        

    def event_handler(self, event=None):
        try:
            self.manga.change_page(1)
        except Exception:
            pass

    def event_handler1(self, event=None):
        try:
            self.manga.change_page(-1)
        except Exception:
            pass
        

class Manga:

    def __init__(self, manga, chapter, image):

        self.manga = manga
        self.chapter = int(chapter)
        self.image = image

        options = Options()
        options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=options)

        self.find_manga()
        self.find_chapter()
        self.current_page = 1
        self.find_image()

        
        

    def find_manga(self):
        
        link = "https://mangadex.org/quick_search/" + self.manga
        self.driver.get(link)
        page_source = self.driver.page_source
        string_to_find = '<a href="/title/(.*)"><img'
        
        self.manga_id = re.search(string_to_find, page_source,
                                  re.I|re.M).group(1)

    def find_chapter(self):

        counter = 1
        string_to_find = 'data-id="(.*)".*data-title=".*"(.*)data-chapter="' \
                             + str(self.chapter)\
                             + '".*data-volume="(.*)".*data-comments="(.*)".*'\
                             + 'data-read="(.*)".*data-lang="1"'
        chapter = None
        while chapter == None:
            link = "https://mangadex.org/title/" + self.manga_id + "/chapters/"\
                   + str(counter)
            self.driver.get(link)
            page_source = self.driver.page_source
            
            counter+=1

            chapter = re.search(string_to_find, page_source, re.M|re.I)
        
        self.chapter_id = chapter.group(1)
        self.chapter_title = chapter.group(2)

    def find_image(self):

        link = "https://mangadex.org/chapter/" + self.chapter_id + "/" + str(self.current_page)
        self.driver.get(link)
        
        self.image_link = None
        
        while self.image_link == None:
            page_source = self.driver.page_source
            self.image_link = re.search('cursor-pointer" src="(.*)" data-page', page_source, re.I|re.M)
            sleep(1)
            print("loading")

        self.image_ext = self.image_link.group(1)[-4:]
        self.image_id = re.search("(.*)" + str(self.current_page) + self.image_ext, self.image_link.group(1), re.I|re.M).group(1)
        self.image_type = self.image_id[-1]
        self.image_id = self.image_id[:-1]

        pages = re.search('"total-pages">(.*)</span>', page_source, re.M|re.I)
        self.total_page = pages.group(1)
        
        self.image_link = self.image_id + self.image_type + str(self.current_page) + self.image_ext

        self.change_image()

    def change_page(self, direction):
        self.current_page += direction
        self.image_link = self.image_id + self.image_type + str(self.current_page) + self.image_ext
    
        if direction == 1:
            if self.current_page <= int(self.total_page):
                self.change_image()
                
            elif self.current_page > int(self.total_page):
                self.change_chapter(1)
                

        else:
            if self.current_page >= 1:
                self.change_image()
                
            elif self.current_page < 1:
                self.change_chapter(-1)
                    
            

    def change_chapter(self, direction):
        self.chapter += direction

        if direction == 1:
            self.find_chapter()
            self.current_page = 1
            self.find_image()
        else:
            self.find_chapter()
            self.current_page = int(self.total_page)
            self.find_image()
        

    def change_image(self):
        print(self.image_link)
        try:
            page = Image.open(requests.get(self.image_link, stream=True).raw)
            
        except Exception:
            if self.image_ext == ".png":
                self.image_ext = ".jpg"
            else:
                self.image_ext = ".png"
                
            self.image_link = self.image_id + self.image_type + str(self.current_page) + self.image_ext
            print(self.image_link)
            page = Image.open(requests.get(self.image_link, stream=True).raw)
            
        page = page.resize((920, 1300), Image.LANCZOS)
        img = ImageTk.PhotoImage(page)

        self.image.itemconfig(self.image.image, image =img)
        self.image.img = img
        self.image.yview_moveto(0)
        
        

        

def main():
    root = Tk()
    app = MainGUI(root)
    app.mainloop()
       

if __name__ == "__main__":
    main()




