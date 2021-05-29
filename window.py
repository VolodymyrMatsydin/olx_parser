from tkinter import *
from tkinter import ttk, scrolledtext
from PIL import ImageTk, Image
from io import BytesIO


COLUMNS_TABLE = {'Price':80, 'Heading':330, 'URL':40}


class Window:

        def __init__(self,  root_instance: Tk):
                root = root_instance
                root.geometry('1800x900')
                self._build_tabs(root)
                self.lframe = Frame(self.main_tab)
                self.lframe.pack(side=LEFT, padx=20, pady=20, fill='both', expand=True)#grid(row=0, column=0, padx=10)
                self.cframe = Frame(self.main_tab)
                self.cframe.pack(side=LEFT, pady=20, fill='both', expand=True)#.grid(row=0, column=1, padx=10)
                self.rframe = Frame(self.main_tab)
                self.rframe.pack(side=LEFT, padx=20, pady=20, fill='both', expand=True)#.grid(row=0, column=2, padx=10)
                self._init_left_ui(self.lframe)
                self._init_center_ui(self.cframe)
                self._init_right_ui(self.rframe)
                self._init_log(self.log_tab)

        def _build_tabs(self, root):
                """"""
                tab_control = ttk.Notebook(root)
                self.main_tab = LabelFrame(tab_control, labelanchor=NW, fg='black', text='---')
                self.log_tab = LabelFrame(tab_control, labelanchor=NW, fg='black', text='LOG')
                tab_control.add(self.main_tab, text=f"{'Main':^30s}")
                tab_control.add(self.log_tab, text=f"{'log':^30s}")
                tab_control.pack(expand=1, fill='both')
        
        def _init_left_ui(self, frame):
                #self.l_offers = Label(frame, text='Offers list')
                #self.l_offers.grid(row=0, column=0)
                self._init_table(frame)
                self._config_table(self.table)
                #self.lb_offers = Listbox(frame, height=34, width=48)
                #self.lb_offers.pack()

        def _init_center_ui(self, frame):
                img = ImageTk.PhotoImage(Image.open("1.png"))
                self.panel = Label(frame)#, height=700, width=1000)
                self.panel.image = img
                self.panel.configure(image=img)
                self.panel.pack(fill='both', expand=True)#side="bottom", fill="both", expand="yes")
                #self.panel.bind('<Button-1>', self._click_img)

                self.text = scrolledtext.ScrolledText(frame, font=('Helvetica', '11'), height=15, width=65)
                self.text.pack(pady=20, fill='x', expand=True)

        def _init_log(self, frame):
                self.text_log = Text(frame)
                self.text_log.pack(fill='both', expand=True)

        def _init_right_ui(self, frame):
                self.text_place = Text(frame, height=2, width=20)
                self.text_place.grid(row=0, column=0, pady=15)
                self.text_place.insert(END, '261')

                self.min_price = Text(frame, height=1, width=20)
                self.min_price.grid(row=1, column=0, pady=15)
                self.min_price.insert(END, '1300')

                self.max_price = Text(frame, height=1, width=20)
                self.max_price.grid(row=2, column=0, pady=15)
                self.max_price.insert(END, '1500')

                self.text_keywords = Text(frame, height=8, width=20)
                self.text_keywords.grid(row=3, column=0, pady=15)
                self.text_keywords.insert(END, 'Piltza')

                self.b_run = Button(frame, text='RUN', width=15, height=3)#, command=self._click_run)
                self.b_run.grid(row=4, column=0, pady=15)

                self.log = scrolledtext.ScrolledText(frame, height=8, width=20)
                self.log.grid(row=5, column=0, pady=23)

        def set_image_to_entry(self, raw_image):
                img = Image.open(BytesIO(raw_image))
                img.thumbnail((900, 700), Image.ANTIALIAS)
                photo = ImageTk.PhotoImage(img)
                self.panel.image = photo
                self.panel.configure(image=photo)


        def _init_table(self, frame):

                style = ttk.Style(frame)
                style.configure('Treeview', rowheight=24)

                scrolltabley = Scrollbar(frame)#, command=self.table.yview)
                #self.table.configure(yscrollcommand=scrolltabley.set)
                scrolltabley.pack(side=RIGHT, fill='y', expand=True)  # grid(row=1, column=1, sticky='ns')


                scrolltablex = Scrollbar(frame, orient=HORIZONTAL)#, command=self.table.xview)
                #self.table.configure(xscrollcommand=scrolltablex.set)
                scrolltablex.pack(side=BOTTOM, fill='x')#, expand=True)  # grid(row=2, column=0, sticky='we')

                self.table = ttk.Treeview(frame,
                                                                  show="headings",
                                                                  xscrollcommand=scrolltablex.set,
                                                                  yscrollcommand=scrolltabley.set
                                                                  )#, height=34, )
                self.table.pack(side=TOP, fill='both', expand=True)#grid(row=1, column=0, sticky='ns')
                self.table.tag_configure("default", foreground="black")
                self.table.tag_configure("green", background="SeaGreen1")
                #self.table.bind('<Button-1>', self._click_table)
                #self.table.bind('<<TreeviewSelect>>', self._click_table)

                scrolltablex.config(command=self.table.xview)
                scrolltabley.config(command=self.table.yview)

        def _config_table(self, table):
                headings = list(COLUMNS_TABLE.keys())
                table['columns'] = headings
                for head, hwidth in COLUMNS_TABLE.items():
                        table.heading(head, text=head, anchor=CENTER)
                        table.column(head, width=hwidth, minwidth=hwidth-8, anchor=W)

        def fill_table(self, table, data, tags=None):
                for values in data:
                        table.insert('', END, values=tuple(values), tags=tags)

        def clear_table(self, table):
                for i in table.get_children():
                        table.delete(i)

        def fill_listbox(self, listbox, data):
                for i in data:
                        listbox.insert(END, i)



if __name__ == '__main__':
        root = Tk()
        
        window = Window(root)

        root.mainloop()
