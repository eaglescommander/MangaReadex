import requests
import re
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from time import sleep
from tkinter import *
from tkinter.ttk import Combobox
from PIL import Image, ImageTk
from bs4 import BeautifulSoup

class MainGUI():

    def __init__(self, root):
        self.root = root

        self.create_gui()

    def create_gui(self):
        self.root.title("Mangareader v1.1 - By Nadhif")
        self.root.geometry("1000x1080")

        options = Options()
        options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=options)

        self.header = Frame(self.root, height=100, width=900)
        self.lefthead = Frame(self.header, height=80, width=465,
                              highlightbackground="green",
                              highlightcolor="green",
                              highlightthickness=1)
        self.righthead = Frame(self.header, height=80, width=465,
                               highlightbackground="green",
                               highlightcolor="green",
                               highlightthickness=1)
        self.prighthead = Frame(self.righthead, height=35, width=465)
        self.body = Frame(self.root, height=900, width=930,
                          highlightbackground="blue",
                          highlightcolor="blue",
                          highlightthickness=1)
        self.footer = Frame(self.root, height=20, width=930,
                                highlightbackground="red",
                                highlightcolor="red",
                                highlightthickness=1)

        self.header.pack_propagate(False)
        self.body.pack_propagate(False)
        self.lefthead.pack_propagate(False)
        self.righthead.pack_propagate(False)
        self.footer.pack_propagate(False)

        self.header.pack()
        self.body.pack()
        self.footer.pack()
        
        self.lefthead.grid(row=0, column=0)
        self.righthead.grid(row=0, column=1)
        self.prighthead.pack(side=BOTTOM)

        self.manga = Manga(self.body, width=907, height=1200,
                           scrollregion=(0,0,900,1300), driver=self.driver)
        
        manga_label = Label(self.lefthead,
                            text="Enter your manga title", font=(22))
        chapter_label = Label(self.righthead,
                            text="Pick your chapter", font=(14))
        page_label = Label(self.prighthead,
                           text="Page :", font=(14))

        manga_label.pack()
        chapter_label.pack()
        
        self.manga.manga_box = Combobox(self.lefthead, width=50)
        self.manga.chapter_box = Combobox(self.righthead, width=50, state='readonly')
        self.manga.page_box = Combobox(self.prighthead, width=10, state='readonly')
        
        self.manga.manga_box.pack()
        self.manga.chapter_box.pack()

        page_label.pack(side=LEFT)
        self.manga.page_box.pack(side=RIGHT)

        left_button = Button(self.footer, text="<-",
                             command = self.prev_page,
                             width=51, font=(16))
        right_button = Button(self.footer, text="->",
                              command = self.next_page,
                              width=51, font=(16))

        left_button.pack(side=LEFT)
        right_button.pack(side=RIGHT)

        scrollbar = Scrollbar(self.body, orient=VERTICAL)
        
        self.manga.config(yscrollcommand=scrollbar.set)
        self.manga.pack(side=LEFT)
        img = ImageTk.PhotoImage(file="mangareadex.png")
        self.manga.image = self.manga.create_image(450, 650, image=img)
        self.manga.img = img

        scrollbar.config(command=self.manga.yview)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.controller()

    def controller(self):

        self.manga.manga_box.bind('<Return>', self.update_manga_list)
        self.manga.manga_box.bind('<<ComboboxSelected>>',
                            self.update_chapter_list)
        self.manga.chapter_box.bind('<<ComboboxSelected>>',
                            self.update_page_list)
        self.manga.page_box.bind('<<ComboboxSelected>>',
                           self.jump_to)

        self.root.bind('<MouseWheel>', self.mousewheel)
        self.manga.bind('<Button-1>', self.click)
        
        self.root.bind('<Right>', self.next_page)
        self.root.bind('<Left>', self.prev_page)

    def mousewheel(self, event):
        self.manga.yview_scroll(-1*(int(event.delta/120)), 'units')

    def update_manga_list(self, event):
        self.title_dir = self.manga.find_manga(self.manga.manga_box.get())
        self.manga.manga_box['values'] = [title for title in self.title_dir.keys()]

    def update_chapter_list(self, event):
        self.manga.chapter_box.set('')
        self.manga.page_box.set('')
        self.manga.page_box['values'] = []
        
        title = self.manga.manga_box.get()
        href = self.title_dir[title]
        
        self.chapter_dir = self.manga.find_chapter(href)
        self.manga.chapter_box['values'] = [chapter for chapter in self.chapter_dir.keys()]

    def update_page_list(self, event):
        self.manga.current_page = 1
        self.manga.page_box.set(1)
        
        chapter = self.manga.chapter_box.get()
        
        cha_list = [chapter for chapter in self.chapter_dir.keys()]
        self.manga.current_chapter = cha_list.index(chapter)
        
        id = self.chapter_dir[chapter]
        self.page_dir = self.manga.find_image(id)
        
        self.manga.page_box['values'] = [num for num in self.page_dir.keys()]

    def click(self, event):
        if int(event.x) < 465:
            self.prev_page()
        else:
            self.next_page()

    def next_page(self, event=None):
        try:
            self.manga.change_page(1)
        except Exception:
            pass

    def prev_page(self, event=None):
        try:
            self.manga.change_page(-1)
        except Exception:
            pass

    def jump_to(self, event):
        page = self.manga.page_box.get()
        self.manga.current_page = int(page)
        self.manga.change_image()
        
    def mainloop(self):
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        self.root.mainloop()

    def quit(self):
        self.root.destroy()
        self.driver.quit()
        

class Manga(Canvas):

    def __init__(self, root, width, height, scrollregion, driver):
        super().__init__(root, width=width, height=height, scrollregion=scrollregion)
        self.driver = driver
        self.current_page = 1

    def find_manga(self, manga):

        print('searching')
        
        link = "https://mangadex.org/quick_search/" + manga
        self.driver.get(link)
        parsed_source = BeautifulSoup(self.driver.page_source, 'lxml')

        title_dir = {}
        
        title_lst = parsed_source.find_all('a', class_="manga_title")
        
        title = [name['title'] for name in title_lst]
        link = [name['href'] for name in title_lst]

        for num in range(0, len(title)):
            title_dir[title[num]] = link[num]

        print("Done!")
        return title_dir

    def find_chapter(self, href):

        self.image_link = None
        
        link = "https://mangadex.org" + href
        self.driver.get(link)
        parsed_source = BeautifulSoup(self.driver.page_source, 'lxml')
        
        try:
            last_page = parsed_source.find('li', class_='page-item paging').a['href']
        except Exception:
            last_page = href + "/chapters/1/"

        last_page = "https://mangadex.org" + last_page

        counter = 1
        self.chapter_dir = {}
        
        while link != last_page:

            print(f'{counter} out of {last_page}')
            
            link = "https://mangadex.org" + href + "/chapters/" + str(counter) + '/'
            self.driver.get(link)
            page_source = self.driver.page_source
            parsed_source = BeautifulSoup(self.driver.page_source, 'lxml')

            chapter_lst = parsed_source.find_all('div', {'data-lang' : '1'})
            
            chapter = [num['data-chapter'] for num in chapter_lst]
            chapter_title = [title['data-title'] for title in chapter_lst]
            chapter_id = [id['data-id'] for id in chapter_lst]

            for num in range(len(chapter)):
                self.chapter_dir[chapter[num] + " - " + chapter_title[num]] = chapter_id[num]

            counter += 1

        print("Done!")
        return self.chapter_dir

    def find_image(self, id):

        link = "https://mangadex.org/chapter/" + id + "/" + str(self.current_page)
        self.driver.get(link)
        
        self.total_page, self.image_link = None, None
        
        while self.total_page == None or self.image_link == None:
            page_source = self.driver.page_source
            parsed_source = BeautifulSoup(page_source, 'lxml')
            self.image_link = parsed_source.find('img', {'data-chapter':id})
            self.total_page = parsed_source.find('div', {'role' : 'main'})
            sleep(0.5)
            print("loading")

        self.image_link = self.image_link['src']
        self.total_page = self.total_page['data-total-pages']

        self.image_ext = self.image_link[-4:]
        self.image_id = re.search("(.*)" + str(self.current_page) + self.image_ext, self.image_link, re.I|re.M).group(1)
        self.image_type = self.image_id[-1]
        self.image_id = self.image_id[:-1]
        
        self.image_link = self.image_id + self.image_type + str(self.current_page) + self.image_ext

        page_dir = {}

        for num in range(1, int(self.total_page) + 1):
            page_dir[num] = str(num)

        self.change_image()
        
        print("Done!")  
        return page_dir
    
    def change_page(self, direction):
        
        if self.image_link == None:
            return None
        
        self.current_page += direction
    
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

        self.page_box.set(self.current_page)

    def change_chapter(self, direction):
        self.current_chapter -= direction
        
        key = [key for key in self.chapter_dir.keys()]
        try:
            key = key[self.current_chapter]
        except Exceptions:
            return None

        print(key)
        id = self.chapter_dir[key]

        if direction == 1:
            self.current_page = 1
        else:
            self.current_page = int(self.total_page)
        
        page_dir = self.find_image(id)
        self.page_box['values'] = [num for num in page_dir.keys()]

        self.chapter_box.set(key)
        

    def change_image(self):
        self.image_link = self.image_id + self.image_type + str(self.current_page) + self.image_ext
        
        try:
            page = Image.open(requests.get(self.image_link, stream=True).raw)
            
        except Exception:
            try:
                self.image_link = self.image_id + self.image_type + str(self.current_page) + ".jpg"
                page = Image.open(requests.get(self.image_link, stream=True).raw)
                
            except Exception:
                try:
                    self.image_link = self.image_id + self.image_type + str(self.current_page) + ".png"
                    page = Image.open(requests.get(self.image_link, stream=True).raw)
                    
                except Exception:
                    return None
            
        page = page.resize((920, 1300), Image.LANCZOS)
        img = ImageTk.PhotoImage(page)

        self.itemconfig(self.image, image =img)
        self.img = img
        self.yview_moveto(0)

def main():
    root = Tk()
    app = MainGUI(root)
    app.mainloop()
       

if __name__ == "__main__":
    main()
