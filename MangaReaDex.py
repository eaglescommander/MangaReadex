# Import all libraries
import requests
import re
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from time import sleep
from tkinter import Tk, Frame, Canvas, Label, Button, Scrollbar, RIGHT, LEFT, VERTICAL, BOTTOM, Y
from tkinter.ttk import Combobox
from PIL import Image, ImageTk
from bs4 import BeautifulSoup

class MainGUI():

    def __init__(self, root):
        self.root = root
        self.create_gui()

    # Create the main window
    def create_gui(self):
        '''used to create GUI elements'''

        self.root.title("MangaReaDex v1.2 - By Nadhif")
        self.root.geometry("1000x1080")

        # Initialize the webdriver headless
        options = Options()
        options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=options)

        # Make frame for every different GUI element
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

        # Freeze the frame so it doesn't shrink
        self.header.pack_propagate(False)
        self.body.pack_propagate(False)
        self.lefthead.pack_propagate(False)
        self.righthead.pack_propagate(False)
        self.footer.pack_propagate(False)

        # Put all the frames inside the main window
        self.header.pack()
        self.body.pack()
        self.footer.pack()
        self.lefthead.grid(row=0, column=0)
        self.righthead.grid(row=0, column=1)
        self.prighthead.pack(side=BOTTOM)

        # Initialize the manga object (Canvas)
        self.manga = Manga(self.body, width=907, height=1200,
                           scrollregion=(0,0,900,1300), driver=self.driver)
        
        # Make labels and place them inside the window
        manga_label = Label(self.lefthead,
                            text="Enter your manga title", font=(22))
        chapter_label = Label(self.righthead,
                            text="Pick your chapter", font=(14))
        page_label = Label(self.prighthead,
                           text="Page :", font=(14))

        manga_label.pack()
        chapter_label.pack()
        
        # Make boxes as Manga's attribute and place them inside the window
        self.manga.manga_box = Combobox(self.lefthead, width=50)
        self.manga.chapter_box = Combobox(self.righthead, width=50, state='readonly')
        self.manga.page_box = Combobox(self.prighthead, width=10, state='readonly')
        
        self.manga.manga_box.pack()
        self.manga.chapter_box.pack()

        page_label.pack(side=LEFT)
        self.manga.page_box.pack(side=RIGHT)

        # Make buttons and place them inside the window
        left_button = Button(self.footer, text="<-",
                             command = self.prev_page,
                             width=51, font=(16))
        right_button = Button(self.footer, text="->",
                              command = self.next_page,
                              width=51, font=(16))
        search_button = Button(self.lefthead, text="Search",
                                command = self.update_manga_list)

        left_button.pack(side=LEFT)
        right_button.pack(side=RIGHT)
        search_button.pack()

        # Make a scrollbar for the canvas and pack the canvas
        scrollbar = Scrollbar(self.body, orient=VERTICAL)
        
        self.manga.config(yscrollcommand=scrollbar.set)
        self.manga.pack(side=LEFT)

        # Create a title screen image and show it in the canvas
        img = ImageTk.PhotoImage(file="mangareadex.png")
        self.manga.image = self.manga.create_image(450, 650, image=img)
        self.manga.img = img

        # Pack the scrollbar
        scrollbar.config(command=self.manga.yview)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Make the controls
        self.controller()

    def controller(self):
        '''make the necessary keyboard and mouse controls'''

        # Bind the boxes to get elements
        self.manga.manga_box.bind('<Return>', self.update_manga_list)
        self.manga.manga_box.bind('<<ComboboxSelected>>',
                            self.update_chapter_list)
        self.manga.chapter_box.bind('<<ComboboxSelected>>',
                            self.update_page_list)
        self.manga.page_box.bind('<<ComboboxSelected>>',
                           self.jump_to)

        # Bind the mouse controls
        self.root.bind('<MouseWheel>', self.mousewheel)
        self.manga.bind('<Button-1>', self.click)
        
        # Bind the keyboard controls
        self.root.bind('<Right>', self.next_page)
        self.root.bind('<Left>', self.prev_page)
        self.root.bind('<Up>',  self.scroll_up)
        self.root.bind('<Down>', self.scroll_down)

    def mousewheel(self, event):
        '''event for mousewheel scroll'''
        self.manga.yview_scroll(-1*(int(event.delta/120)), 'units')

    def scroll_up(self, event):
        '''event for keyboard press up'''
        self.manga.yview_scroll(-1, 'units')

    def scroll_down(self, event):
        '''event for keyboard press down'''
        self.manga.yview_scroll(1, 'units')

    def update_manga_list(self, event=None):
        # Call find_manga in manga object and populate box
        self.title_dir = self.manga.find_manga(self.manga.manga_box.get())
        self.manga.manga_box['values'] = [title for title in self.title_dir.keys()]

    def update_chapter_list(self, event):
        # Clear chapter and page box
        self.manga.chapter_box.set('')
        self.manga.page_box.set('')
        self.manga.page_box['values'] = []
        
        title = self.manga.manga_box.get()
        href = self.title_dir[title]
        
        # Call find_chapter in manga object and populate the box
        self.chapter_dir = self.manga.find_chapter(href)
        self.manga.chapter_box['values'] = [chapter for chapter in self.chapter_dir.keys()]

    def update_page_list(self, event):
        # Set the page to be the first page
        self.manga.current_page = 1
        self.manga.page_box.set(1)
        
        chapter = self.manga.chapter_box.get()
        cha_list = [chapter for chapter in self.chapter_dir.keys()]
        self.manga.current_chapter = cha_list.index(chapter)
        id = self.chapter_dir[chapter]

        # Call find_image in manga object and populate the box
        self.page_dir = self.manga.find_image(id)
        self.manga.page_box['values'] = [num for num in self.page_dir.keys()]

    def click(self, event):
        '''event for click on the page'''
        if int(event.x) < 465:
            self.prev_page()
        else:
            self.next_page()

    def next_page(self, event=None):
        '''event for keyboard press right'''
        try:
            self.manga.change_page(1)
        except Exception:
            pass

    def prev_page(self, event=None):
        '''event for keyboard press left'''
        try:
            self.manga.change_page(-1)
        except Exception:
            pass

    def jump_to(self, event):
        '''event for changing page via the page_box'''
        page = self.manga.page_box.get()
        self.manga.current_page = int(page)
        self.manga.change_image()
        
    def mainloop(self):
        # If you close the gui window
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        self.root.mainloop()

    def quit(self):
        # Destroy the driver and the root
        self.root.destroy()
        self.driver.quit()
        

class Manga(Canvas):

    def __init__(self, root=None, width=None, height=None, scrollregion=None, driver=None):
        super().__init__(root, width=width, height=height, scrollregion=scrollregion)
        # Inherit the driver
        self.driver = driver
        self.current_page = 1

    def find_manga(self, manga=''):
        '''Function for finding manga titles
        
        Example:
        >>> import requests
        >>> from bs4 import BeautifulSoup
        >>> manga = Manga()
        >>> title = "Hayate No Gotoku"
        >>> title_dir = manga.find_manga(title)
        Searching
        Done!
        >>> title_dir != {}
        True
        '''
        print('Searching')
        
        # Get the link
        link = "https://mangadex.org/quick_search/" + manga
        
        # Try to get the page
        try:
            page_source = requests.get(link).content
        # If there's no connection
        except Exception:
            print("Error : No Connection")
            return {}

        # Parse the html page
        parsed_source = BeautifulSoup(page_source, 'lxml')

        title_dir = {}
        
        # Find all titles in the source and make a list
        title_lst = parsed_source.find_all('a', class_="manga_title")
        
        title = [name['title'] for name in title_lst]
        link = [name['href'] for name in title_lst]

        # Put it in the directory
        for num in range(0, len(title)):
            title_dir[title[num]] = link[num]

        print("Done!")
        return title_dir

    def find_chapter(self, href=''):
        '''function for finding a certain manga's title
        
        Example:
        >>> import requests
        >>> from bs4 import BeautifulSoup
        >>> manga = Manga()
        >>> href = "/title/410/hayate-no-gotoku"
        >>> chapter_dir = manga.find_chapter(href)
        Loading
        1 out of https://mangadex.org/title/410/hayate-no-gotoku/chapters/6/
        2 out of https://mangadex.org/title/410/hayate-no-gotoku/chapters/6/
        3 out of https://mangadex.org/title/410/hayate-no-gotoku/chapters/6/
        4 out of https://mangadex.org/title/410/hayate-no-gotoku/chapters/6/
        5 out of https://mangadex.org/title/410/hayate-no-gotoku/chapters/6/
        6 out of https://mangadex.org/title/410/hayate-no-gotoku/chapters/6/
        Done!
        >>> chapter_dir != {}
        True
        '''
        print("Loading")

        self.image_link = None
        
        # Get the link
        link = "https://mangadex.org" + href

        # Try to get the link
        try:
            page_source = requests.get(link)
        # If there's no connection
        except Exception:
            print("Error : No Connection")
            return {}
        # Parse the page
        parsed_source = BeautifulSoup(page_source.content, 'lxml')

        # Try to find the last page of chapters
        try:
            last_page = parsed_source.find('li', class_='page-item paging').a['href']
        # If there's only one page
        except Exception:
            last_page = href + "/chapters/1/"

        last_page = "https://mangadex.org" + last_page

        counter = 1
        self.chapter_dir = {}
        
        # Loop for getting all chapters on all page
        while link != last_page:
            print(f'{counter} out of {last_page}')

            # Make link
            link = "https://mangadex.org" + href + "/chapters/" + str(counter) + '/'
            
            # Try to open the link
            try:
                page_source = requests.get(link).content
            # If there's no connection
            except Exception:
                print("Error : No Connection")
                return {}

            # Get the source and parse it
            parsed_source = BeautifulSoup(page_source, 'lxml')

            # Find all chapter in the page and make list
            chapter_lst = parsed_source.find_all('div', {'data-lang' : '1'})
            
            chapter = [num['data-chapter'] for num in chapter_lst]
            chapter_title = [title['data-title'] for title in chapter_lst]
            chapter_id = [id['data-id'] for id in chapter_lst]

            # Put every chapter inside the dictionary
            for num in range(len(chapter)):
                self.chapter_dir[chapter[num] + " - " + chapter_title[num]] = chapter_id[num]

            counter += 1

        print("Done!")
        return self.chapter_dir

    def find_image(self, id='', direction=None):
        '''function for finding image of a chapter'''

        # Make link
        link = "https://mangadex.org/chapter/" + id + "/1"
        # Try to open the link
        try:
            self.driver.get(link)
        # If there's no connection
        except Exception:
            print("Error : No Connection")
            return {}
        
        self.total_page, self.image_link = None, None
        
        # Try to see if page has loaded it's javascript
        counter = 1
        try:
            while self.total_page == None or self.image_link == None:
                print(link)
                page_source = self.driver.page_source
                parsed_source = BeautifulSoup(page_source, 'lxml')
                self.image_link = parsed_source.find('img', {'data-chapter':id})
                self.total_page = parsed_source.find('div', {'role' : 'main'})
                sleep(0.5)
                print("loading")
                counter += 1
                if counter > 60:
                    raise Exception
        # If the page doesn't load anymore
        except Exception:
            print("Error : No Connection")
            return {}

        # Get each element fromt the loaded page
        self.image_link = self.image_link['src']
        self.total_page = self.total_page['data-total-pages']

        # If it's the next chapter
        if direction == 1:
            self.current_page = 1
        # If it's the previous chapter
        elif direction == -1:
            self.current_page = int(self.total_page)

        # Get each element from the link to manipulate
        self.image_ext = self.image_link[-4:]
        self.image_id = re.search("(.*)" + "1" + self.image_ext, self.image_link, re.I|re.M).group(1)
        self.image_type = self.image_id[-1]
        self.image_id = self.image_id[:-1]
        
        # Join them together
        self.image_link = self.image_id + self.image_type + str(self.current_page) + self.image_ext

        page_dir = {}

        # Add the total page to the directory
        for num in range(1, int(self.total_page) + 1):
            page_dir[num] = str(num)

        # Call function to change image in canvas
        self.change_image(direction)
        
        print("Done!")  
        return page_dir
    
    def change_page(self, direction):
        '''function for changing page'''

        # If there's no image yet
        if self.image_link == None:
            return None
        
        self.current_page += direction
    
        # If the direction is forward
        if direction == 1:
            if self.current_page <= int(self.total_page):
                self.change_image(direction)
                
            elif self.current_page > int(self.total_page):
                # If it's the last page of a chapter
                self.change_chapter(direction)

        # If the direction is backward
        else:
            if self.current_page >= 1:
                self.change_image(direction)
                
            elif self.current_page < 1:
                # If it's the first page of a chapter
                self.change_chapter(direction)

        # Change the box display
        self.page_box.set(self.current_page)

    def change_chapter(self, direction):
        # Because the directory is reversed
        self.current_chapter -= direction
        
        key = [key for key in self.chapter_dir.keys()]
        # Try to get the key for the next/previous chapter
        try:
            key = key[self.current_chapter]
        # If this is the first or the last chapter
        except Exception:
            return None

        # Get id for the next chapter
        print(key)
        id = self.chapter_dir[key]

        # Find image id and populate the box
        page_dir = self.find_image(id, direction)
        self.page_box['values'] = [num for num in page_dir.keys()]

        # Change the box display
        self.chapter_box.set(key)
        

    def change_image(self, direction=None):
        '''function for changing the image on the canvas'''

        # Build the image link
        self.image_link = self.image_id + self.image_type + str(self.current_page) + self.image_ext

        # Try to get the image
        try :
            page_source = requests.get(self.image_link, stream=True)
        # If there's no connection
        except Exception:
            print("Error : No Connection")
            return None

        # Try to open the image
        try:
            page = Image.open(page_source.raw)
        # If it's the wrong extension
        except Exception:
            # Try .jpg
            try:
                self.image_link = self.image_id + self.image_type + str(self.current_page) + ".jpg"
                page_source = requests.get(self.image_link, stream=True)
                page = Image.open(page_source.raw)
            # If it's not .jpg
            except Exception:
                # Try .png
                try:
                    self.image_link = self.image_id + self.image_type + str(self.current_page) + ".png"
                    page_source = requests.get(self.image_link, stream=True)
                    page = Image.open(page_source.raw)  
                # If it's not .png
                except Exception:
                    # Try .jpeg
                    try :
                        self.image_link = self.image_id + self.image_type + str(self.current_page) + ".jpeg"
                        page_source = requests.get(self.image_link, stream=True)
                        page = Image.open(page_source.raw) 
                    # If it's not .jpeg, give up and change page
                    except Exception:
                        self.change_page(direction)
        
        page_source.close()
        # Resize the page to fit the canvas
        page = page.resize((920, 1300), Image.LANCZOS)
        img = ImageTk.PhotoImage(page)

        # Change the page in the canvas
        self.itemconfig(self.image, image =img)
        self.img = img

        # Reset the display
        self.yview_moveto(0)

def main():
    # Call the main GUI
    root = Tk()
    app = MainGUI(root)
    app.mainloop()
       

if __name__ == "__main__":
    main()
