# -*- coding: utf-8 -*-

# @autor: Felipe Ucelli
# @github: github.com/felipeucelli

# Built-in
import os
import re
import sys
import time
import math
import tkinter
from html import unescape
from _thread import start_new_thread
import xml.etree.ElementTree as ElementTree
from tkinter import ttk, filedialog, messagebox, TclError

from imageio_ffmpeg import get_ffmpeg_exe
from ffmpeg_progress_yield import FfmpegProgress
from pytube import YouTube, Playlist, Search, exceptions


class ListTabs:
    def __init__(self, list_tab, root):
        self.list_tab = list_tab
        self.root = root
        self._list_tabs()

    def _list_tabs(self):
        """
        Creates a tree view that displays downloads made at runtime
        :return:
        """

        # Create a vertical scrollbar for the tree view
        self.list_scrollbar_y = tkinter.Scrollbar(self.list_tab, orient='vertical')
        self.list_scrollbar_y.pack(side="right", fill="y")

        # Create a horizontal scrollbar for the tree view
        self.list_scrollbar_x = tkinter.Scrollbar(self.list_tab, orient='horizontal')
        self.list_scrollbar_x.pack(side="bottom", fill="x")

        self.tree_view = ttk.Treeview(self.list_tab, height=2,
                                      columns=('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'),
                                      yscrollcommand=self.list_scrollbar_y.set,
                                      xscrollcommand=self.list_scrollbar_x.set)
        config_tree_view = {
            'heading': ['N', 'Status', 'Title', 'Format', 'Duration', ' Quality', 'Size', 'Extension',
                        'Progressive', 'Subtitle', 'path'],
            'column': [50, 130, 250, 100, 100, 150, 100, 120, 120, 120, 300]
        }
        self.tree_view.heading('#0', text='')
        for c in range(len(config_tree_view['heading'])):
            self.tree_view.heading(c + 1, text=config_tree_view['heading'][c], anchor=tkinter.CENTER)
        self.tree_view.column('#0', width=0, stretch=tkinter.NO)

        for c in range(len(config_tree_view['column'])):
            self.tree_view.column(c + 1, width=config_tree_view['column'][c], minwidth=config_tree_view['column'][c],
                                  anchor=tkinter.CENTER)
        self.tree_view.column(len(config_tree_view['column']) + 1, width=0, stretch=tkinter.NO)

        self.tree_view.place(x=0, y=50, height=437, width=529)

        # Configure scroll bars
        self.list_scrollbar_y.config(command=self.tree_view.yview)
        self.list_scrollbar_x.config(command=self.tree_view.xview)

        self.tree_view.bind('<Double-Button-1>', self.list_info)

    def insert_list_tab(self, *args):
        """
        Insert a new column in tree view
        :param args: Receive the value of status, title, format_file, duration, quality, size, path, url
        :return:
        """
        self.tree_view.insert(parent='', index=tkinter.END, iid=args[0][0],
                              values=[values for values in args[0]])

    def edit_list_tab(self, *args):
        """
        Edit the last column inserted in the tree view
        :param args: Receive the value of status, title, format_file, duration, quality, size, path, url
        :return:
        """
        self.tree_view.item(args[0][0], values=[values for values in args[0]])

    def list_info(self, *args):
        """
        Function responsible for generating a top level that displays download information in a listbox
        :param args:
        :return:
        """
        _none = args

        if self.tree_view.selection() != ():
            top_level = tkinter.Toplevel(self.root)
            top_level.resizable(False, False)

            list_scrollbar_x = tkinter.Scrollbar(top_level, orient='horizontal')
            list_scrollbar_x.pack(side="bottom", fill="x")

            listbox = tkinter.Listbox(top_level, width=50, height=15, font='Arial 10', borderwidth=0,
                                      highlightthickness=0, xscrollcommand=list_scrollbar_x.set)
            listbox.pack(padx=5, pady=5, ipadx=5, ipady=5)
            list_scrollbar_x.config(command=listbox.xview)

            for c in range(12):
                listbox.insert('end', self.tree_view.item(str(self.tree_view.selection()[0]), 'values')[c])

            self.tree_view.selection_remove(self.tree_view.selection())

            # Blocks user interaction with main screen while top level is open
            top_level.transient(self.root)
            top_level.wait_visibility()
            top_level.grab_set()
            self.root.wait_window(top_level)

            top_level.mainloop()


class Gui(ListTabs):
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title('Youtube Download')
        self.root.resizable(width=False, height=False)
        self.root.geometry('550x530')

        # Variables
        self.select_type = ''
        self.youtube_type = ''
        self.link = ''
        self.duration = ''
        self.stream_video = ''
        self.stream_audio = ''
        self.video_extension = ''
        self.audio_extension = ''
        self.progressive = True
        self.stop_download_status = False
        self.search_entry_status = False
        self.loading_link_verify_status = False
        self.load_list_playlist_status = False
        self.mouse_on_youtube_entry_status = False
        self.loading_link_verify_status = False
        self.youtube_link_variable = tkinter.StringVar()
        self.search_list_variable = tkinter.StringVar()
        self.select_file_playlist = tkinter.StringVar()
        self.files_count_tree_view = 1
        self.files_count_ok = 0
        self.search_link_list = []

        self.tabs = ttk.Notebook(self.root)
        self.download_tab = tkinter.Frame(self.tabs, highlightthickness=0)
        self.list_tab = tkinter.Frame(self.tabs, highlightthickness=0)

        self.tabs.add(self.download_tab, text="    Download    ")
        self.tabs.add(self.list_tab, text="    List    ")

        self.style_download_tab = ttk.Style(self.download_tab)
        self.style_download_tab.configure('TButton', font=('Arial', 15))

        self.tabs.pack(fill='both', expand=True)

        self._download_tab()
        self._create_menu()
        self._popup()
        self.root.bind("<Button-3>", self._do_popup)

        ListTabs.__init__(self, self.list_tab, self.root)  # Instantiate the main list

        self.search_pattern_index = ListTabs(self.list_tab, self.root)
        self.search_pattern_index.tree_view.destroy()
        self.search_pattern_index.list_scrollbar_x.destroy()
        self.search_pattern_index.list_scrollbar_y.destroy()

        self.search_list_entry = ttk.Entry(self.list_tab, font='Arial 15', textvariable=self.search_list_variable)
        self.search_list_entry.pack(fill='x')
        self.search_list_variable.trace('w', self.search_list)
        self.select_file_playlist.trace('w', self._validation_select_file_playlist)

    def _download_tab(self):
        """
        Interface frame configuration
        :return:
        """
        # Frame configuration for insertion and search of links
        self.frame_link = tkinter.Frame(self.download_tab, width=550, height=150)
        self.frame_link.pack(pady=30)
        self.entry_youtube_link = ttk.Entry(self.frame_link, font=('Arial', 15), foreground='gray',
                                            textvariable=self.youtube_link_variable, width=35, takefocus=False)
        self.entry_youtube_link.insert(0, 'Type here a youtube link')
        self.entry_youtube_link.bind('<FocusIn>', lambda event: self.focus_in(self.entry_youtube_link,
                                                                              'Type here a youtube link'))
        self.entry_youtube_link.bind('<FocusOut>', lambda event: self.focus_out(self.entry_youtube_link,
                                                                                'Type here a youtube link'))
        self.entry_youtube_link.bind('<Return>', lambda event: self.link_verify())
        self.entry_youtube_link.bind('<Enter>', lambda event: self._mouse_on_youtube_entry(True))
        self.entry_youtube_link.bind('<Leave>', lambda event: self._mouse_on_youtube_entry(False))
        self.entry_youtube_link.grid(row=0, column=0)
        self.btn_link_verify = ttk.Button(self.frame_link, text='    SEARCH    ',
                                          command=self.link_verify)
        self.btn_link_verify.bind('<Return>', lambda event: self.link_verify())
        self.btn_link_verify.grid(row=0, column=1, padx=5)
        self.message_youtube_title = tkinter.Message(self.frame_link, font='Arial 10', width=450)
        self.message_youtube_title.grid(row=1, columnspan=2)

        self.frame_list_search_entry = tkinter.Frame(self.download_tab)
        self.scrollbar_y_search_entry = tkinter.Scrollbar(self.frame_list_search_entry, orient='vertical')
        self.scrollbar_y_search_entry.pack(side='right', fill='y')
        self.scrollbar_x_search_entry = tkinter.Scrollbar(self.frame_list_search_entry, orient='horizontal')
        self.scrollbar_x_search_entry.pack(side="bottom", fill="x")
        self.list_box_search_entry = tkinter.Listbox(self.frame_list_search_entry, width=87, height=19, borderwidth=0,
                                                     highlightthickness=0, activestyle='none',
                                                     yscrollcommand=self.scrollbar_y_search_entry.set,
                                                     xscrollcommand=self.scrollbar_x_search_entry.set)
        self.list_box_search_entry.pack()
        self.list_box_search_entry.bind('<Double-Button-1>', self.insert_entry_search)
        self.scrollbar_y_search_entry.config(command=self.list_box_search_entry.yview)
        self.scrollbar_x_search_entry.config(command=self.list_box_search_entry.xview)

        # Animation frame setup during link search
        self.frame_load_link = tkinter.Frame(self.download_tab)
        self.progressbar_link_verify = ttk.Progressbar(self.frame_load_link, orient=tkinter.HORIZONTAL,
                                                       mode='indeterminate', length=200)
        self.progressbar_link_verify.pack(pady=50)

        # frame configuration for file type selection (audio, video)
        self.frame_file_type = tkinter.Frame(self.download_tab)
        self.btn_video = ttk.Button(self.frame_file_type, text='     Video     ',
                                    command=lambda: self.select_file_type('video'))
        self.btn_video.bind('<Return>', lambda event: self.select_file_type('video'))
        self.btn_video.pack(pady=15)
        self.btn_audio = ttk.Button(self.frame_file_type, text='     Audio     ',
                                    command=lambda: self.select_file_type('audio'))
        self.btn_audio.bind('<Return>', lambda event: self.select_file_type('audio'))
        self.btn_audio.pack(pady=15)

        # frame setting for selecting audio file download quality
        self.frame_audio_download = tkinter.Frame(self.download_tab)
        self.label_combo_audio_select = tkinter.Label(self.frame_audio_download,
                                                      font='Arial 10', text='Select a Quality: ')
        self.label_combo_audio_select.pack(pady=5)
        self.combo_quality_audio = ttk.Combobox(self.frame_audio_download, font='Arial 15', state='readonly')
        self.combo_quality_audio.pack()
        self.btn_audio_download = ttk.Button(self.frame_audio_download, text='Download', command=self.download_file)
        self.btn_audio_download.bind('<Return>', lambda event: self.download_file())
        self.btn_audio_download.pack(pady=15)

        # frame setting for selecting video file download quality
        self.frame_video_download = tkinter.Frame(self.download_tab)
        self.label_combo_video_select = tkinter.Label(self.frame_video_download,
                                                      font='Arial 10', text='Select a Quality: ')
        self.label_combo_video_select.pack(pady=5)
        self.combo_quality_video = ttk.Combobox(self.frame_video_download, font='Arial 15', state='readonly')
        self.combo_quality_video.pack()

        self.label_caption = tkinter.Label(self.frame_video_download, font='Arial 10', text='Subtitle:')
        self.label_caption.pack(pady=5)
        self.combo_subtitle = ttk.Combobox(self.frame_video_download, font='Arial 15', state='readonly')
        self.combo_subtitle.pack()

        self.btn_video_download = ttk.Button(self.frame_video_download, text='Download', command=self.download_file)
        self.btn_video_download.bind('<Return>', lambda event: self.download_file())
        self.btn_video_download.pack(pady=15)

        # frame setting for selecting video playlist file download quality
        self.frame_video_playlist_download = tkinter.Frame(self.download_tab)
        self.label_select_video_playlist = tkinter.Label(self.frame_video_playlist_download,
                                                         font='Arial 15', text='Choose Videos:')
        self.label_select_video_playlist.grid(row=0, column=0, sticky='nw', padx=1, pady=1)
        self.entry_select_video_playlist = ttk.Entry(self.frame_video_playlist_download, font=('Arial', 15),
                                                     textvariable=self.select_file_playlist, width=19)
        self.entry_select_video_playlist.grid(row=0, column=1)
        self.btn_load_video_list = ttk.Button(self.frame_video_playlist_download,
                                              text='Load List', command=self._load_list_playlist)
        self.btn_load_video_list.bind('<Return>', lambda event: self._load_list_playlist())
        self.btn_load_video_list.grid(row=1, column=0, sticky='sw', padx=1, pady=1)
        self.btn_highest_resolution = ttk.Button(self.frame_video_playlist_download, text='Highest Resolution',
                                                 command=lambda: self.download_file('highest_resolution'))
        self.btn_highest_resolution.bind('<Return>', lambda event: self.download_file('highest_resolution'))
        self.btn_highest_resolution.grid(row=0, column=2, padx=5)
        self.btn_lowest_resolution = ttk.Button(self.frame_video_playlist_download, text='Lowest Resolution',
                                                command=lambda: self.download_file('lowest_resolution'))
        self.btn_lowest_resolution.bind('<Return>', lambda event: self.download_file('lowest_resolution'))
        self.btn_lowest_resolution.grid(row=1, column=2, padx=5)

        # frame setting for selecting audio playlist file download
        self.frame_audio_playlist_download = tkinter.Frame(self.download_tab)
        self.label_select_audio_playlist = tkinter.Label(self.frame_audio_playlist_download,
                                                         font='Arial 15', text='Choose Audios:')
        self.label_select_audio_playlist.grid(row=0, column=0, sticky='nw', padx=1, pady=1)
        self.entry_select_audio_playlist = ttk.Entry(self.frame_audio_playlist_download, font=('Arial', 15),
                                                     textvariable=self.select_file_playlist, width=20)
        self.entry_select_audio_playlist.grid(row=0, column=1, sticky='n')
        self.btn_load_audio_list = ttk.Button(self.frame_audio_playlist_download,
                                              text='Load List', command=self._load_list_playlist)
        self.btn_load_audio_list.bind('<Return>', lambda event: self._load_list_playlist())
        self.btn_load_audio_list.grid(row=1, column=0, sticky='sw', padx=1, pady=1)
        self.btn_audio_file = ttk.Button(self.frame_audio_playlist_download,
                                         text='    Download    ', command=self.download_file)
        self.btn_audio_file.bind('<Return>', lambda event: self.download_file())
        self.btn_audio_file.grid(row=0, column=2, padx=5)

        # Download Status frame Setting
        self.frame_download_status = tkinter.Frame(self.download_tab)
        self.label_count_playlist = tkinter.Label(self.frame_download_status, font='Arial 15', fg='green')
        self.label_count_playlist.pack(pady=5)
        self.label_download_name_file = tkinter.Message(self.frame_download_status,
                                                        font='Arial 10', fg='green', width=400)
        self.label_download_name_file.pack(pady=25)
        self.label_download_status = tkinter.Label(self.frame_download_status, font='Arial 15', fg='green')
        self.label_download_status.pack(pady=10)
        self.label_download_progress_bar = ttk.Progressbar(self.frame_download_status, orient=tkinter.HORIZONTAL,
                                                           mode='determinate', length=400)
        self.label_download_progress_bar.pack(side='left')
        self.label_download_progress_bar_count = tkinter.Label(self.frame_download_status, font='Arial 10', fg='green')
        self.label_download_progress_bar_count.pack(side='left')

        self.frame_stop = tkinter.Frame(self.download_tab)
        self.btn_stop = ttk.Button(self.frame_stop, text='    Stop    ', style='btn_stop.TButton',
                                   command=self.stop_download, takefocus=False)
        self.btn_stop.bind('<Return>', lambda event: self.stop_download())
        self.btn_stop.pack()
        self.btn_force_stop = ttk.Button(self.frame_stop, text='Force Stop', style='btn_force_stop.TButton',
                                         command=self.force_stop_download, takefocus=False)
        self.btn_force_stop.bind('<Return>', lambda event: self.force_stop_download())
        self.style_download_tab.configure('btn_stop.TButton', font=('Arial', 15))
        self.style_download_tab.map('btn_stop.TButton', foreground=[('!disabled', 'red'), ('disabled', 'red')])
        self.style_download_tab.configure('btn_force_stop.TButton', font=('Arial', 10))
        self.style_download_tab.map('btn_force_stop.TButton', foreground=[('!disabled', 'red'), ('disabled', 'red')])

        # frame setting for the return button for selecting file type (audio, video)
        self.frame_return = tkinter.Frame(self.download_tab, width=50, height=50)
        self.frame_return.place(y=465, x=0)
        self.btn_return = tkinter.Button(self.frame_return, text='<', font='Arial 15',
                                         borderwidth=0, command=self.return_page)
        self.btn_return.bind('<Return>', lambda event: self.return_page())
        self.btn_return.pack(pady=1, padx=10)
        self.btn_return.configure(state=tkinter.DISABLED)

    def search_list(self, *args):
        """
        Function responsible for monitoring the search entry in the download list in real time
        :param args:
        :return:
        """
        _none = args

        if self.search_list_variable.get() != '':

            # Forget the main list
            self.tree_view.place_forget()
            self.list_scrollbar_x.pack_forget()
            self.list_scrollbar_y.pack_forget()

            # Destroys the secondary list if there is a new match requested
            self.search_pattern_index.tree_view.destroy()
            self.search_pattern_index.list_scrollbar_x.destroy()
            self.search_pattern_index.list_scrollbar_y.destroy()

            pattern_index = self.find_pattern_index()

            if len(pattern_index) >= 1:

                # Instantiate the secondary list to receive incoming correspondence
                self.search_pattern_index._list_tabs()
                self.search_pattern_index.list_scrollbar_y.pack(side="right", fill="y")
                self.search_pattern_index.list_scrollbar_x.pack(side="bottom", fill="x")
                self.search_pattern_index.tree_view.place(x=0, y=50, height=437, width=529)

                # Add all matches found to the secondary list
                for i in range(1, len(pattern_index) + 1):
                    values = (self.tree_view.item(str(pattern_index[i - 1]), 'values'))
                    self.search_pattern_index.insert_list_tab(values)

        elif self.search_list_variable.get() == '':

            # Destroys the secondary list if there are no matches requested
            self.search_pattern_index.tree_view.destroy()
            self.search_pattern_index.list_scrollbar_x.destroy()
            self.search_pattern_index.list_scrollbar_y.destroy()

            # Show the main list again
            self.tree_view.place(x=0, y=50, height=437, width=529)
            self.list_scrollbar_y.pack(side="right", fill="y")
            self.list_scrollbar_x.pack(side="bottom", fill="x")

    def find_pattern_index(self):
        """
        Function responsible for finding the requested correspondence in the download list
        :return: Returns the indexes of matches found
        """
        pattern_index = []
        regex = re.compile(re.escape(self.search_list_variable.get()) + '.*', re.IGNORECASE)
        for i in range(1, self.files_count_tree_view):
            tree_view_data = self.tree_view.item(str(i), 'values')
            x = regex.search(tree_view_data[2])
            if x is not None:
                pattern_index.append(i)
        return pattern_index

    def _create_menu(self):
        """
        Function responsible for creating the menu tab in the tkinter interface
        :return:
        """
        self.new_menu = tkinter.Menu(self.root)
        self.option_menu = tkinter.Menu(self.new_menu, tearoff=0)
        self.new_menu.add_cascade(label='Options', menu=self.option_menu)
        self.option_menu.add_command(label='Export list', command=lambda: self.export_list())
        self.option_menu.add_separator()
        self.option_menu.add_command(label='Exit', command=lambda: self.root.destroy())
        self.root.config(menu=self.new_menu)

    def _popup(self):
        """
        Set commands for popup menu
        :return:
        """
        self.popup_menu = tkinter.Menu(self.root, tearoff=0)

        self.popup_menu.add_command(label="Copy     ", command=self._copy_youtube_link)
        self.popup_menu.add_command(label="Paste    ", command=self._paste_youtube_link)
        self.popup_menu.add_separator()
        self.popup_menu.add_command(label="Clear    ", command=self._clear_youtube_link)

    def _do_popup(self, event):
        """
        Instantiates the _popup function when it is binding
        :param event:
        :return:
        """
        if self.mouse_on_youtube_entry_status:
            try:
                self.popup_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.popup_menu.grab_release()

    def _mouse_on_youtube_entry(self, status):
        """
        Set the mouse state over the link Entry
        :param status: Current state
        :return:
        """
        self.mouse_on_youtube_entry_status = status

    def _copy_youtube_link(self):
        """
        Add variable content to clipboard
        :return:
        """
        if self.youtube_link_variable.get() != 'Type here a youtube link':
            self.root.clipboard_append(self.youtube_link_variable.get())

    def _paste_youtube_link(self):
        """
        Set the clipboard content in the variable
        :return:
        """
        try:
            self.focus_in(self.entry_youtube_link, 'Type here a youtube link')
            self.youtube_link_variable.set(self.root.clipboard_get())
        except TclError:
            pass

    def _clear_youtube_link(self):
        """
        Clear the variable
        :return:
        """
        self.youtube_link_variable.set('')
        self.focus_out(self.entry_youtube_link, 'Type here a youtube link')

    def export_list(self):
        """
        Responsible for exporting tree view items
        :return:
        """
        if self.files_count_ok > 0:
            # Get the path to save the exported file
            path = filedialog.asksaveasfilename(defaultextension='txt',
                                                initialfile='export_list',
                                                filetypes=(('Text files', '*.txt'), ('All files', '*.*')))
            if path != '' and path != ():
                with open(path, 'w', encoding='utf-8') as save:
                    save.writelines(f'Counter: {self.files_count_ok}\n')
                    for i in range(1, self.files_count_tree_view):
                        tree_view_data = self.tree_view.item(str(i), 'values')
                        if tree_view_data[1] == 'SUCCESS':
                            save.writelines('------------------------------------------------------------\n')
                            save.writelines(f'Title: {tree_view_data[2]}\n')
                            save.writelines(f'Format: {tree_view_data[3]}\n')
                            save.writelines(f'Duration: {tree_view_data[4]}\n')
                            save.writelines(f'Quality: {tree_view_data[5]}\n')
                            save.writelines(f'Size: {tree_view_data[6]}\n')
                            save.writelines('------------------------------------------------------------\n')

    def insert_entry_search(self, *args):
        """
        Insert the link in the search entry of the selected title
        :param args: None
        :return:
        """
        _none = args
        self.youtube_link_variable.set(self.search_link_list[self.list_box_search_entry.curselection()[0]])
        self.list_box_search_entry.delete(0, 'end')
        self.search_link_list.clear()
        self.frame_list_search_entry.pack_forget()

    def search_entry(self):
        """
        Perform a YouTube search using the keyword
        :return:
        """
        pattern = r'(?:=|\/)([0-9A-Za-z_-]{11}).*'  # Just get the YouTube link
        regex = re.compile(pattern)

        self.list_box_search_entry.delete(0, 'end')
        self.search_entry_status = True

        self.frame_list_search_entry.pack()

        try:
            self.block_interface()
            yt = Search(self.youtube_link_variable.get())

            for c in yt.results:
                self.list_box_search_entry.insert('end', c.title)  # Insert the titles in the listbox

                # Insert title links into a list
                self.search_link_list.append(f'https://youtube.com/watch?v={regex.findall(str(c))[0]}')

            os.system('cls' if os.name == 'nt' else 'clear')  # Clear the console if pytube returns a match alert
            self.unblock_interface()
        except Exception as error:
            messagebox.showerror('Error', f'Pytube: {str(error)}')
            self.unblock_interface()
            self.reset_interface()

    def _thread_loading_link_verify(self, *args):
        """
        Generates an animation while checking the link
        :param args: None
        :return:
        """
        _none = args

        # while self.loading_link_verify_status:
        #    bars = ('|', '/', '-', '\\')
        #    r = 4
        #    for i in range(r):
        #        self.progressbar_link_verify['text'] = bars[i]
        #        time.sleep(0.20)
        #        if not self.loading_link_verify_status:
        #            break
        # self.frame_load_link.pack_forget()

        self.progressbar_link_verify['value'] = 0
        while self.loading_link_verify_status:
            self.progressbar_link_verify['value'] += 1
            time.sleep(0.01)
            if not self.loading_link_verify_status:
                break

        self.frame_load_link.pack_forget()

    def _thread_link_verify(self, *args):
        """
        Check the link provided
        :return: returns the file type (audio, video) and whether it belongs to a playlist or not
        """
        _none = args
        self.reset_interface()
        self.message_youtube_title['text'] = ''
        self.select_type = ''
        if self.youtube_link_variable.get() != '' and self.youtube_link_variable.get() != 'Type here a youtube link':
            self.loading_link_verify_status = True
            self.frame_load_link.pack(pady=100)
            start_new_thread(self._thread_loading_link_verify, (None, None))
            self.block_interface()
            try:
                try:
                    self.playlist = Playlist(self.youtube_link_variable.get())
                    self.youtube_type = 'playlist'
                    self.len_playlist_link = len(self.playlist)
                    title = f'Type: Playlist\n' \
                            f'Files: {self.len_playlist_link}\n' \
                            f'Title: {self.playlist.title}'
                except KeyError:
                    self.youtube = YouTube(self.youtube_link_variable.get())
                    stream = self.youtube.streams
                    self.combo_quality_video['values'] = self.get_quality(stream=stream, file_type='video')
                    self.combo_quality_audio['values'] = self.get_quality(stream=stream, file_type='audio')
                    self.combo_subtitle['values'] = self.get_subtitle_code()
                    self.stream_video = stream.filter()
                    self.stream_audio = stream.filter(only_audio=True)
                    title = f'Type: Single File\n' \
                            f'Title: {self.youtube.title}'
                    self.youtube_type = 'single_file'
            except exceptions.RegexMatchError as error:
                if 'regex_search' in str(error):
                    self.loading_link_verify_status = False
                    self.unblock_interface()
                    self.search_entry()
                else:
                    self.unblock_interface()
                    self.reset_interface()
                    messagebox.showerror('Error', f'Pytube: {str(error)}')
            except Exception as error:
                self.unblock_interface()
                self.reset_interface()
                messagebox.showerror('Error', f'Pytube: {str(error)}')
            else:
                self.search_entry_status = False
                self.loading_link_verify_status = False
                self.unblock_interface()
                self.message_youtube_title['text'] = title
                self.frame_file_type.pack(pady=50)
                self.link = self.youtube_link_variable.get()
        else:
            self.select_type = ''
            self.message_youtube_title['text'] = ''
            self.frame_file_type.pack_forget()

    def link_verify(self):
        """
        Starts thread for link verification
        :return:
        """
        start_new_thread(self._thread_link_verify, (None, None))

    def block_interface(self):
        """
        Blocks insertion of links during download
        :return:
        """
        self.entry_youtube_link.configure(state=tkinter.DISABLED)
        self.entry_youtube_link['foreground'] = 'gray'
        self.btn_link_verify.configure(state=tkinter.DISABLED)
        self.btn_return.configure(state=tkinter.DISABLED)

    def unblock_interface(self):
        """
        Unlocks interface after download finishes
        :return:
        """
        self.entry_youtube_link.configure(state=tkinter.NORMAL)
        self.entry_youtube_link['foreground'] = 'black'
        self.btn_link_verify.configure(state=tkinter.ACTIVE)
        if self.select_type != '':
            self.btn_return.configure(state=tkinter.ACTIVE)

    def reset_interface(self):
        """
        Resets interface after insertion and search for new links
        :return:
        """
        if self.select_type != '':
            self.forget_frames_downloads()
        elif self.select_type == '':
            self.frame_file_type.pack_forget()
        self.combo_quality_video.set('')
        self.combo_quality_audio.set('')
        self.combo_subtitle.set('')
        self.select_file_playlist.set('')
        self.btn_return.configure(state=tkinter.DISABLED)

        if self.loading_link_verify_status:
            self.loading_link_verify_status = False
        if self.load_list_playlist_status:
            self.load_list_playlist_status = False
            self.close_list_playlist()
        if self.search_entry_status:
            self.frame_list_search_entry.pack_forget()

    def return_page(self):
        """
        Return to file type selection menu (audio, video)
        :return:
        """
        self.forget_frames_downloads()
        if self.combo_quality_audio.get() != '':
            self.combo_quality_audio.set('')
        if self.combo_quality_video.get() != '':
            self.combo_quality_video.set('')
        if self.combo_subtitle.get() != '':
            self.combo_subtitle.set('')
        self.frame_file_type.pack(pady=50)
        self.btn_return.configure(state=tkinter.DISABLED)

        if self.load_list_playlist_status:
            self.load_list_playlist_status = False
            self.close_list_playlist()

        self.select_type = ''
        self.select_file_playlist.set('')

    @staticmethod
    def focus_in(insertion, msg: str):
        """
        Clean the placeholder
        :return:
        """
        if insertion.get() == msg:
            insertion.delete(0, 'end')
            insertion['foreground'] = 'black'

    @staticmethod
    def focus_out(insertion, msg: str):
        """
        Insert placeholder
        :return:
        """
        if insertion.get() == '':
            insertion.insert(0, msg)
            insertion['foreground'] = 'gray'

    def to_mp4(self, video: str, out_file: str, audio=None):
        """
        Convert the downloaded file to mp4
        :param audio: Full path of the audio file
        :param video: extension: File to be converted
        :param out_file: Returns a file converted to mp4
        :return:
        """
        if audio:
            command = [self.ffmpeg_path, '-i', audio, '-i', video, '-c:v', 'copy', out_file]
        else:
            command = [self.ffmpeg_path, '-i', video, '-c:v', 'copy', out_file]

        self.run_ffmpeg(command=command)

    def to_mp3(self, extension: str, mp3: str):
        """
        Convert the downloaded file to mp3
        :param extension: File to be converted
        :param mp3: New Converted File Name
        :return: Returns a file converted to mp3
        """
        command = [self.ffmpeg_path, '-i', extension, mp3]

        self.run_ffmpeg(command=command)

    def set_progress_callback(self, percent: str):
        """
        Set the download progress bar
        :param percent: Progress bar percentage
        :return:
        """
        self.label_download_progress_bar_count['text'] = f'{percent}%'
        self.label_download_progress_bar['value'] = percent

    def progress_callback(self, *args):
        """
        Shows a download progress bar
        :param args: Takes 3 arguments(stream, chunk, bytes_remaining)
        :return: Change the text of label_download_progress_bar
        """
        stream = args[0]
        bytes_remaining = args[2]
        file_size = stream.filesize
        current = ((file_size - bytes_remaining) / file_size)
        percent = '{0:.1f}'.format(current * 100)
        self.set_progress_callback(percent=percent)

    def start_download(self):
        """
        Removes options frame and added status download frame
        :return:
        """
        self.block_interface()
        self.forget_frames_downloads()

        if self.load_list_playlist_status:
            self.load_list_playlist_status = False
            self.close_list_playlist()

        self.frame_download_status.pack()
        self.frame_stop.pack(pady=20)

    def download_finished(self):
        """
        Show the options frame after the download finishes
        :return:
        """
        messagebox.showinfo('Info', 'Download Finished')
        self.frame_download_status.pack_forget()
        self.frame_stop.pack_forget()
        self.unblock_interface()
        self.show_frame_selected_type(self.select_type)

        self.label_count_playlist['text'] = ''
        self.label_download_name_file['text'] = ''
        self.label_download_status['text'] = ''
        self.label_download_progress_bar_count['text'] = ''
        self.label_download_progress_bar['value'] = 0
        self.video_extension = ''
        self.audio_extension = ''

        if self.stop_download_status:
            self.btn_stop.configure(state=tkinter.ACTIVE)
            self.btn_stop['text'] = '    Stop    '
            self.stop_download_status = False
            self.btn_force_stop.pack_forget()

        self.select_file_playlist.set('')

    def modify_data_treeview(self, modification_type: str, status: str, quality: str, size='-', path='-') -> None:
        """
        Insert and edit treeview values
        :param modification_type:
        :param status: status (DOWNLOADING, CONVERTING, SUCCESS)
        :param quality: Quality of the file to be downloaded
        :param size: Downloaded file size
        :param path: File download path
        :return:
        """
        values = [self.files_count_tree_view, status,
                  self.label_download_name_file["text"],
                  f'{self.select_type.upper()}',
                  self.duration,
                  quality,
                  size,
                  self.video_extension if self.select_type == 'video' else self.audio_extension,
                  str(self.progressive),
                  'NONE' if self.combo_subtitle.get() == '' else self.combo_subtitle.get(),
                  path,
                  self.link]

        if modification_type == 'insert':
            self.insert_list_tab(values)
        elif modification_type == 'edit':
            self.edit_list_tab(values)

    def run_ffmpeg(self, command: list):
        """
        Run the ffmpeg binary and get stdout to generate a progress bar using the ffmpeg_progress_yield library
        :param command: List containing the parameters to be passed to ffmpeg
        :return:
        """
        try:
            ffmpeg = FfmpegProgress(command)
            for progress in ffmpeg.run_command_with_progress():
                self.set_progress_callback(str(progress))
        except Exception as error:
            messagebox.showerror('Error', str(error))
            self.restart()

    @property
    def ffmpeg_path(self) -> str:
        """
        Get the ffmpeg binary and adapt it to linux and Windows systems
        :return: Returns the full path of the binary
        """
        path = f'{get_ffmpeg_exe()}'
        if os.name != 'nt':
            ffmpeg = path.split('/')[-1]
            path = path.replace(ffmpeg, f'./{ffmpeg}')

        return path

    @staticmethod
    def float_to_srt_time_format(d: float) -> str:  # pytube function
        """Convert decimal durations into proper srt format.

        :rtype: str
        :returns:
            SubRip Subtitle (str) formatted time duration.

        float_to_srt_time_format(3.89) -> '00:00:03,890'
        """
        fraction, whole = math.modf(d)
        time_fmt = time.strftime("%H:%M:%S,", time.gmtime(whole))
        ms = f"{fraction:.3f}".replace("0.", "")
        return time_fmt + ms

    def xml_caption_to_srt(self, xml_captions: str) -> str:  # pytube function
        """Convert xml caption tracks to "SubRip Subtitle (srt)".

        :param str xml_captions:
        XML formatted caption tracks.
        """
        segments = []
        root = ElementTree.fromstring(xml_captions)
        i = 0
        for child in list(root.iter("body"))[0]:
            if child.tag == 'p':
                caption = ''
                if len(list(child)) == 0:
                    # instead of 'continue'
                    caption = child.text
                for s in list(child):
                    if s.tag == 's':
                        caption += ' ' + s.text
                caption = unescape(caption.replace("\n", " ").replace("  ", " "), )
                try:
                    duration = float(child.attrib["d"]) / 1000.0
                except KeyError:
                    duration = 0.0
                start = float(child.attrib["t"]) / 1000.0
                end = start + duration
                sequence_number = i + 1  # convert from 0-indexed to 1.
                line = "{seq}\n{start} --> {end}\n{text}\n".format(
                    seq=sequence_number,
                    start=self.float_to_srt_time_format(start),
                    end=self.float_to_srt_time_format(end),
                    text=caption,
                )
                segments.append(line)
                i += 1
        return "\n".join(segments).strip()

    def get_subtitle_code(self) -> list:
        """
        Get the subtitle code and return it in a list
        :return: Returns a list of available subtitle codes
        """
        pattern = r'code=\"[a-zA-Z]+(?:-[a-zA-Z]+)?\"'  # Get the subtitle codes, example output: code="en"
        regex = re.compile(pattern)
        raw_caption_code = regex.findall(str(self.youtube.caption_tracks))

        caption_code = ['NONE']
        for c in raw_caption_code:
            caption_code.append(c.split('"')[1])

        return caption_code

    def get_srt_file(self, save_path: str) -> str:
        """
        Convert xml subtitle file to srt and return full path
        :param save_path: save path of video
        :return: Returns the full path of the subtitle.srt file
        """
        selected_caption = self.youtube.captions[self.combo_subtitle.get()]

        # Convert xml to srt using modified pytube function
        srt = self.xml_caption_to_srt(selected_caption.xml_captions)

        srt_file_path = f'{save_path}/subtitle.srt'

        with open(srt_file_path, 'a', encoding='utf-8') as file:
            file.write(srt)

        return srt_file_path

    def insert_subtitle(self, save_path, video_path):
        """
        Convert xml subtitle to srt, and with ffmpeg convert srt to ass and add to video
        :param save_path: Path where the video was saved
        :param video_path: Full path with video name
        :return:
        """
        video_path = video_path.replace(f'.{self.video_extension}', '.mp4')

        srt_file_path = self.get_srt_file(save_path=save_path)

        if os.name == 'nt':
            srt_file_path = srt_file_path.replace('C:', 'c\\:')

        os.rename(video_path, f'{save_path}/add_subtitle.mp4')
        path_in_file = f'{save_path}/add_subtitle.mp4'

        command = [self.ffmpeg_path, '-i', path_in_file, '-vf', f"subtitles='{srt_file_path}'", video_path]

        try:
            self.run_ffmpeg(command=command)
            os.remove(f'{save_path}/subtitle.srt')
            os.remove(f'{save_path}/add_subtitle.mp4')
        except Exception as error:
            messagebox.showerror('Error', str(error))
            self.restart()

    def close_list_playlist(self):
        """
        Function responsible for closing the playlist list
        :return:
        """
        if not self.load_list_playlist_status and self.select_type != '' and self.youtube_type == 'playlist':
            if self.select_type == 'audio':
                self.btn_load_audio_list['text'] = 'Load List'
            elif self.select_type == 'video':
                self.btn_load_video_list['text'] = 'Load List'
            self.frame_list_playlist.pack_forget()

    def _load_list_playlist(self):
        """
        Function responsible for creating the playlist listbox
        :return:
        """
        self.load_list_playlist_status = not self.load_list_playlist_status

        if self.load_list_playlist_status:
            if self.select_type == 'audio':
                self.btn_load_audio_list['text'] = 'Close List'
            elif self.select_type == 'video':
                self.btn_load_video_list['text'] = 'Close List'

            # Instantiation of "listbox_list_playlist" frame
            self.frame_list_playlist = tkinter.Frame(self.download_tab, width=542, height=200)

            # Instance of the scrollbars of the "listbox_list_playlist" frame
            list_playlist_scrollbar_y = tkinter.Scrollbar(self.frame_list_playlist, orient='vertical')
            list_playlist_scrollbar_y.pack(side="right", fill="y")

            list_playlist_scrollbar_x = tkinter.Scrollbar(self.frame_list_playlist, orient='horizontal')
            list_playlist_scrollbar_x.pack(side="bottom", fill="x")

            self.listbox_list_playlist = tkinter.Listbox(self.frame_list_playlist,
                                                         width=72, height=10, font='Arial 10',
                                                         yscrollcommand=list_playlist_scrollbar_y.set,
                                                         xscrollcommand=list_playlist_scrollbar_x.set,
                                                         borderwidth=0, highlightthickness=0, activestyle='none')
            self.listbox_list_playlist.pack(padx=10, pady=10)
            list_playlist_scrollbar_y.config(command=self.listbox_list_playlist.yview)
            list_playlist_scrollbar_x.config(command=self.listbox_list_playlist.xview)

            self.frame_list_playlist.pack()

            start_new_thread(self._thread_load_list_playlist, (self.listbox_list_playlist, None))
        elif not self.load_list_playlist_status:
            self.close_list_playlist()

    def _thread_load_list_playlist(self, *args):
        """
        Insert the titles of the playlist links into the listbox "listbox_list_playlist" in a new thread
        :param args: args[0] == "listbox_list_playlist"
        :return:
        """
        listbox = args[0]
        i = 1
        for url in self.playlist:
            title = YouTube(url).title
            if self.load_list_playlist_status:
                listbox.insert('end', f'{i} - {title}')
                i += 1
            else:
                break

    def get_select_file_playlist(self) -> list:
        """
        Function responsible for getting the links selected from the playlist
        :return: Returns a list of selected links
        """
        get_data_files_select = self._validation_select_file_playlist()
        flag = get_data_files_select[0]
        data = get_data_files_select[1]
        if flag and data != []:
            playlist = []
            yt = self.playlist
            for j in data:
                playlist.append(yt[int(j) - 1])

            return playlist

    def _validation_select_file_playlist(self, *args) -> bool and list:
        """
        Function responsible for verifying the chosen links
        :param args: None
        :return: Returns if the choice is valid, and a list of the chosen links indexes
        """

        def _change_state(state, fg) -> None:
            """
            Change the foreground and state of playlist download buttons
            :param state: state of the button
            :param fg: entry foreground
            :return: None
            """
            types = {
                'video': lambda: (self.btn_highest_resolution.configure(state=state),
                                  self.btn_lowest_resolution.configure(state=state),
                                  self.entry_select_video_playlist.configure(foreground=fg)),

                'audio': lambda: (self.btn_audio_file.configure(state=state),
                                  self.entry_select_audio_playlist.configure(foreground=fg))
            }

            return types[self.select_type]()

        _none = args
        if self.select_file_playlist.get() != '':
            flag = False
            select = self.select_file_playlist.get().replace(' ', '')

            # Validate entered characters
            pattern = r'^\d+(?:-\d+)?(?:,\d+(?:-\d+)?)*$'
            regex = re.compile(pattern)
            if regex.findall(select):
                flag = True

            data = []
            if flag:
                pattern = r'[\d]+|[\-]'
                regex = re.compile(pattern)
                find = regex.findall(str(select))

                # Adds a sequence of numbers when using "-"
                for k, v in enumerate(find):
                    if v == '-':
                        find.pop(k)
                        i = k
                        if int(find[k - 1]) > int(find[k]):
                            step = -1
                        else:
                            step = 1
                        for c in range(int(find[k - 1]), int(find[k]), step):
                            find.insert(i, c)
                            i += 1
                            if len(find) > self.len_playlist_link * 2:
                                break
                        find.pop(k - 1)
                # Turns all list items to integers
                swap_int = []
                for i in find:
                    swap_int.append(int(i))
                find = swap_int[:]

                # Arrange the list in ascending order using the insert method
                i = 1
                while i < len(find):
                    temp = find[i]
                    swap = False
                    j = i - 1
                    while j >= 0 and find[j] > temp:
                        find[j + 1] = find[j]
                        swap = True
                        j -= 1
                    if swap:
                        find[j + 1] = temp
                    i += 1

                # Check for any duplicate numbers
                for k, v in enumerate(find):
                    if k + 1 < len(find):
                        if find[k + 1] == v:
                            flag = False
                            break
                data = find
                # Check the maximum size of the list
                if data[len(data) - 1] > self.len_playlist_link:
                    flag = False
            if flag:
                _change_state(state=tkinter.ACTIVE, fg='green')
            else:
                _change_state(state=tkinter.DISABLED, fg='red')
            return flag, data
        elif self.select_type != '':
            _change_state(state=tkinter.ACTIVE, fg='green')

    def _download_youtube_file(self, save_path, url=None, quality=None) -> str:
        """
        Call the pytube library and download the selected file
        :param save_path: Path to save the file
        :param url: Contains playlist links
        :param quality: Selected file quality
        :return: Full path of downloaded file
        """
        youtube = ''
        if self.select_type == 'audio':
            if self.youtube_type == 'single_file':
                youtube = YouTube(self.link, on_progress_callback=self.progress_callback).streams.filter(
                    abr=str(self.combo_quality_audio.get()),
                    only_audio=True)[0].download(save_path)

            elif self.youtube_type == 'playlist':
                youtube = YouTube(url, on_progress_callback=self.progress_callback) \
                    .streams.get_audio_only().download(save_path)

        elif self.select_type == 'video':
            if self.youtube_type == 'single_file':
                youtube = YouTube(self.link, on_progress_callback=self.progress_callback) \
                    .streams.filter(
                    res=str(self.combo_quality_video.get().split(' ')[0]),
                    progressive=self.progressive)[0].download(save_path)

            elif self.youtube_type == 'playlist':
                if quality == 'lowest_resolution':
                    youtube = YouTube(url, on_progress_callback=self.progress_callback) \
                        .streams.get_lowest_resolution().download(save_path)

                elif quality == 'highest_resolution':
                    youtube = YouTube(url, on_progress_callback=self.progress_callback) \
                        .streams.get_highest_resolution().download(save_path)

        return youtube

    def _download_handling(self, save_path: str, quality: str, url=None) -> None:
        """
        Add the file details in the treeview and call the download function
        :param save_path: Path to save the file
        :param quality: Selected file quality
        :param url: Contains playlist links
        :return: None
        """
        try:
            youtube = YouTube(url) if url else self.youtube
            self.duration = time.strftime("%H:%M:%S", time.gmtime(youtube.length))
            self.label_download_name_file['text'] = youtube.title
            self.modify_data_treeview(modification_type='insert', status='DOWNLOADING', quality=quality, path=save_path)

            youtube = self._download_youtube_file(save_path=save_path, url=url, quality=quality)

            if self.select_type == 'audio':
                try:
                    self.label_download_status['text'] = f'Converting {self.select_type}, Please Wait.'
                    self.set_progress_callback(percent='0')
                    self.modify_data_treeview(modification_type='edit', status='CONVERTING',
                                              quality=quality,
                                              path=save_path)
                    self.to_mp3(str(youtube), f'{youtube.replace(f".{self.audio_extension}", ".mp3")}')
                    os.remove(youtube)
                except Exception as error:
                    messagebox.showerror('Error', str(error))
                    os.remove(youtube)
                    self.restart()

            # Convert the video to mp4 if it is not
            if self.select_type == 'video' and self.video_extension != 'mp4' and self.progressive:
                try:
                    self.label_download_status['text'] = f'Converting {self.select_type}, Please Wait.'
                    self.set_progress_callback(percent='0')
                    self.modify_data_treeview(modification_type='edit', status='CONVERTING',
                                              quality=quality,
                                              path=save_path)
                    self.to_mp4(str(youtube), f'{youtube.replace(f".{self.video_extension}", ".mp4")}')
                    os.remove(youtube)
                except Exception as error:
                    messagebox.showerror('Error', str(error))
                    os.remove(youtube)
                    self.restart()

            # Download and merge audio into non-progressive videos
            if self.select_type == 'video' and not self.progressive:
                try:
                    # Renames the downloaded non-progressive file, to avoid errors in the merge
                    merge_file = youtube.replace(os.path.basename(youtube), f'Merge_{os.path.basename(youtube)}')
                    os.rename(youtube, merge_file)

                    youtube = youtube.replace(f'.{self.video_extension}', '.mp4')

                    self.set_progress_callback(percent='0')
                    self.label_download_status['text'] = f'Downloading Audio from Video, Please Wait.'
                    self.modify_data_treeview(modification_type='edit', status='DOWNLOADING',
                                              quality=quality,
                                              path=save_path)
                    # Download audio track
                    audio = YouTube(self.link, on_progress_callback=self.progress_callback) \
                        .streams.get_audio_only().download(save_path, filename='audio.mp4')

                    self.modify_data_treeview(modification_type='edit', status='MERGING',
                                              quality=quality,
                                              path=save_path)
                    self.label_download_status['text'] = f'Merging Audio into Video, Please Wait.'

                    self.to_mp4(video=merge_file, out_file=youtube, audio=audio)

                except Exception as error:
                    messagebox.showerror('Error', str(error))
                    self.restart()
                else:
                    os.remove(merge_file)
                    os.remove(audio)
            if self.select_type == 'video' and self.combo_subtitle.get() != 'NONE' and self.combo_subtitle.get() != '':
                try:
                    self.label_download_status['text'] = f'Adding Subtitle, Please Wait.'
                    self.insert_subtitle(save_path=save_path, video_path=youtube)
                except Exception as error:
                    messagebox.showerror('Error', str(error))
                    self.restart()

        except exceptions.PytubeError:
            self.modify_data_treeview(modification_type='edit', status='FAIL', quality=quality)
            self.files_count_tree_view += 1
        except Exception as error:
            messagebox.showerror('Error', str(error))
            self.restart()
        else:
            file_size = 0
            path = ''
            if self.select_type == 'audio':
                file_size = os.path.getsize(youtube.replace(f'.{self.audio_extension}', '.mp3')) / 1048576
                path = youtube.replace(f'.{self.audio_extension}', '.mp3')
            elif self.select_type == 'video':
                file_size = os.path.getsize(youtube.replace(f'.{self.video_extension}', '.mp4')) / 1048576
                path = youtube.replace(f'.{self.video_extension}', '.mp4')

            file_size = f'{file_size:.2f} MB'
            self.modify_data_treeview(modification_type='edit',
                                      status='SUCCESS',
                                      quality=quality,
                                      size=file_size,
                                      path=str(path))
            self.files_count_tree_view += 1
            self.files_count_ok += 1

    def _thread_download_file(self, *args):
        """
        Download playlist audio files and videos
        :param args: args[0] == quality
        :return:
        """
        quality = args[0]
        save_path = filedialog.askdirectory()  # Get the path selected by the user to save the file
        if save_path != '' and save_path != ():
            self.start_download()

            # Check the file type (single_file or playlist) and download
            if self.youtube_type == 'single_file':
                self.label_download_status['text'] = f'Downloading {self.select_type.title()}, Please Wait.'
                self.set_progress_callback(percent='0')

                if self.select_type == 'audio':
                    quality = self.combo_quality_audio.get()
                    self.audio_extension = self.get_file_extension(self.stream_audio, quality)
                elif self.select_type == 'video':
                    quality = self.combo_quality_video.get()
                    self.progressive = self.is_progressive(self.stream_video, quality.split(' ')[0])
                    self.video_extension = self.get_file_extension(self.stream_video, quality.split(' ')[0])

                self._download_handling(save_path=save_path, quality=quality)

            elif self.youtube_type == 'playlist':
                if self.select_file_playlist.get() == '':
                    playlist = self.playlist
                else:
                    playlist = self.get_select_file_playlist()
                count = 0
                self.video_extension = 'mp4'
                self.audio_extension = 'mp4'
                self.progressive = True
                for url in playlist:
                    self.label_count_playlist['text'] = f'FILE: {str(count)}/{str(len(playlist))}'
                    self.label_download_status['text'] = f'Downloading {self.select_type} Playlist, Please Wait.'
                    self.set_progress_callback(percent='0')

                    self._download_handling(save_path=save_path, quality=quality, url=url)

                    count += 1
                    if self.stop_download_status:
                        break
                    self.label_count_playlist['text'] = f'FILE: {str(count)}/{str(len(playlist))}'
            self.download_finished()

    def download_file(self, quality=None) -> None:
        """
        Starts the thread for downloading audio files
        :return:
        """
        if self.youtube_type == 'single_file' and \
                ((self.select_type == 'video' and self.combo_quality_video.get() == '') or
                 (self.select_type == 'audio' and self.combo_quality_audio.get() == '')):
            messagebox.showerror('Error', 'Please Select a Quality')
        else:
            files_types = {
                'video': {
                    'single_file': lambda: start_new_thread(self._thread_download_file, (None, None)),
                    'playlist': lambda: start_new_thread(self._thread_download_file, (quality, None))
                },
                'audio': {
                    'single_file': lambda: start_new_thread(self._thread_download_file, (None, None)),
                    'playlist': lambda: start_new_thread(self._thread_download_file, ('highest_quality', None))
                }
            }

            return files_types[self.select_type][self.youtube_type]()

    def forget_frames_downloads(self) -> None:
        """
        Forget active download frame
        :return: None
        """
        files_types = {
            'video': {
                'single_file': lambda: self.frame_video_download.pack_forget(),
                'playlist': lambda: self.frame_video_playlist_download.pack_forget()
            },
            'audio': {
                'single_file': lambda: self.frame_audio_download.pack_forget(),
                'playlist': lambda: self.frame_audio_playlist_download.pack_forget()
            }
        }

        return files_types[self.select_type][self.youtube_type]()

    def show_frame_selected_type(self, selected_type: str) -> None:
        """
        Activate the download frame of the selected type
        :param selected_type: selected type
        :return: None
        """
        files_types = {
            'video': {
                'single_file': lambda: self.frame_video_download.pack(pady=50),
                'playlist': lambda: (self.frame_video_playlist_download.pack(fill='both'),
                                     self._validation_select_file_playlist())
            },
            'audio': {
                'single_file': lambda: self.frame_audio_download.pack(pady=50),
                'playlist': lambda: (self.frame_audio_playlist_download.pack(fill='both'),
                                     self._validation_select_file_playlist())
            }
        }

        return files_types[selected_type][self.youtube_type]()

    @staticmethod
    def get_stream_selected(stream: str, selected: str) -> str:
        """
        Get the stream with the selected quality
        :param stream: YouTube Streams
        :param selected: selected quality
        :return: selected stream
        """
        pos = ''
        for key, value in enumerate(stream):  # Scan the stream for the file with the selected quality
            if re.findall(selected, str(value)):
                pos = key
                break
        stream = stream[pos]
        return stream

    def is_progressive(self, stream: str, selected: str) -> bool:
        """
        Checks if the selected stream is progressive
        :param stream: YouTube Streams
        :param selected: selected quality
        :return: boolean
        """
        stream = self.get_stream_selected(stream=stream, selected=selected)

        return bool('True' in str(stream))

    def get_file_extension(self, stream: str, selected: str) -> str:
        """
        Get the selected file extension
        :param stream: YouTube Stream audio or video
        :param selected: Quality selecting
        :return: Selected file extension
        """

        stream = self.get_stream_selected(stream=stream, selected=selected)

        pattern = r'/[a-z0-9]+'  # Get only the file extension
        regex = re.compile(pattern)

        extension = str(regex.findall(str(stream))[0]).split('/')[1]

        return extension

    @staticmethod
    def get_quality(stream, file_type: str) -> list:
        """
        Get the quality of the video or audio and return it in a list to be used in the combobox
        :param stream: Stream of videos generated by pytube
        :param file_type: file type
        :return: Returns a list of the quality and fps of the videos
        """

        pattern = {'video': r'\d{3,4}p|\d{2}fps',  # Get Video Quality
                   'audio': r'\d{2,3}kbps'  # Get Audio Quality
                   }
        pattern = pattern[file_type]
        regex = re.compile(pattern)

        stream_filter = {'video': stream.filter().order_by('resolution').desc(),  # Stream Video File
                         'audio': stream.filter(only_audio=True).order_by('abr').desc()  # Stream Audio file
                         }
        yt = stream_filter[file_type]
        quality_list = []

        # Get only quality from stream
        finder = []
        for key, value in enumerate(yt):
            finder.append(str(regex.findall(str(value))))

        # Remove duplicate quality
        for k, v in enumerate(finder):
            while finder.count(v) > 1:
                finder.remove(v)

        # Extract the quality from the list
        for data in finder:
            if data != '[]':
                quality_list.append(regex.findall(str(data)))
        return quality_list

    def select_file_type(self, file_type: str):
        """
        Enable selection frame
        :return:
        """
        self.select_type = file_type
        self.frame_file_type.pack_forget()
        self.btn_return.configure(state=tkinter.ACTIVE)
        self.show_frame_selected_type(self.select_type)

    @staticmethod
    def restart():
        """
        Retrieves the path of the executed program and restarts it
        :return:
        """
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def force_stop_download(self):
        """
        Force download cancellation
        :return:
        """
        stop_download = messagebox.askokcancel('Cancel Download',
                                               'Do you want to cancel the download? it may make it unusable!')
        if stop_download:
            self.restart()

    def stop_download(self):
        """
        Stop the next download
        :return:
        """
        stop_download = messagebox.askokcancel('Cancel Download',
                                               'Do you want to cancel the download?')
        if stop_download:
            self.btn_stop['text'] = 'Stopping...'
            self.btn_stop.configure(state=tkinter.DISABLED)
            self.stop_download_status = True
            self.btn_force_stop.pack(pady=20)

    def start_mainloop(self):
        """
        Start tkinter mainloop
        :return:
        """
        self.root.mainloop()


class Main(Gui):
    def start_gui(self):
        """
        Start the graphical interface
        :return:
        """
        self.start_mainloop()


class Download(Main):
    pass


if __name__ == '__main__':
    main = Download()
    main.start_gui()
