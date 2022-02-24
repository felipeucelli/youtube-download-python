# -*- coding: utf-8 -*-

# @autor: Felipe Ucelli
# @github: github.com/felipeucelli

# Built-in
import os
import re
import sys
import time
import tkinter
from _thread import start_new_thread
from tkinter import ttk, filedialog, messagebox

from proglog import TqdmProgressBarLogger
from pytube import YouTube, Playlist, exceptions
from moviepy.audio.io.AudioFileClip import AudioFileClip


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
                                      columns=('1', '2', '3', '4', '5', '6', '7', '8', '9'),
                                      yscrollcommand=self.list_scrollbar_y.set,
                                      xscrollcommand=self.list_scrollbar_x.set)
        self.tree_view.heading('#0', text='')
        self.tree_view.heading(1, text='N', anchor=tkinter.CENTER)
        self.tree_view.heading(2, text='Status', anchor=tkinter.CENTER)
        self.tree_view.heading(3, text='Title', anchor=tkinter.CENTER)
        self.tree_view.heading(4, text='Format', anchor=tkinter.CENTER)
        self.tree_view.heading(5, text='Duration', anchor=tkinter.CENTER)
        self.tree_view.heading(6, text='Quality', anchor=tkinter.CENTER)
        self.tree_view.heading(7, text='Size', anchor=tkinter.CENTER)
        self.tree_view.heading(8, text='Path', anchor=tkinter.CENTER)
        self.tree_view.column('#0', width=0, stretch=tkinter.NO)
        self.tree_view.column(1, width=50, anchor=tkinter.CENTER)
        self.tree_view.column(2, width=130, anchor=tkinter.CENTER)
        self.tree_view.column(3, width=250, anchor=tkinter.CENTER)
        self.tree_view.column(4, width=100, anchor=tkinter.CENTER)
        self.tree_view.column(5, width=100, anchor=tkinter.CENTER)
        self.tree_view.column(6, width=150, anchor=tkinter.CENTER)
        self.tree_view.column(7, width=100, anchor=tkinter.CENTER)
        self.tree_view.column(8, width=300, anchor=tkinter.CENTER)
        self.tree_view.column(9, width=0, stretch=tkinter.NO)
        self.tree_view.place(x=0, y=50, height=437, width=529)

        # Configure scroll bars
        self.list_scrollbar_y.config(command=self.tree_view.yview)
        self.list_scrollbar_x.config(command=self.tree_view.xview)

        self.tree_view.bind('<Double-Button-1>', self._list_info)

    def _insert_list_tab(self, index: str, status: str, title: str, format_file: str, duration: str,
                         quality: str, size: str, path: str, url: str):
        """
        Insert a new column in tree view
        :param status: File status (DOWNLOADING, CONVERTING)
        :param format_file: File format that will be downloaded (AUDIO, VIDEO)
        :param duration: Media file duration
        :param quality: Quality of the file to be downloaded
        :param size: Downloaded file size
        :param path: File download path
        :param url: Video url
        :return:
        """
        self.tree_view.insert(parent='', index=tkinter.END, iid=index,
                              values=(index, status, title, format_file, duration, quality, size, path, url))

    def _edit_list_tab(self, index: str, status: str, title: str, format_file: str, duration: str,
                       quality: str, size: str, path: str, url: str):
        """
        Edit the last column inserted in the tree view
        :param status: File status (FAIL, SUCCESS)
        :param format_file: File format that will be downloaded (AUDIO, VIDEO)
        :param duration: Media file duration
        :param quality: Quality of the file to be downloaded
        :param size: Downloaded file size
        :param path: File download path
        :param url: Video url
        :return:
        """
        self.tree_view.item(index, values=(index, status, title, format_file, duration, quality, size, path, url))

    def _list_info(self, *args):
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
            listbox.pack(padx=1)
            list_scrollbar_x.config(command=listbox.xview)

            for c in range(9):
                listbox.insert('end', self.tree_view.item(str(self.tree_view.selection()[0]), 'values')[c])

            self.tree_view.selection_remove(self.tree_view.selection())

            # Blocks user interaction with main screen while top level is open
            top_level.transient(self.root)
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
        self.stop_download_status = False
        self.loading_link_verify_status = False
        self.load_list_playlist_status = False
        self.mouse_on_youtube_entry_status = False
        self.youtube_link_variable = tkinter.StringVar()
        self.search_list_variable = tkinter.StringVar()
        self.select_file_playlist = tkinter.StringVar()
        self.files_count_tree_view = 1
        self.files_count_ok = 0

        self.tabs = ttk.Notebook(self.root)
        self.download_tab = tkinter.Canvas(self.tabs, highlightthickness=0)
        self.list_tab = tkinter.Canvas(self.tabs, highlightthickness=0)

        self.tabs.add(self.download_tab, text="Download")
        self.tabs.add(self.list_tab, text="List")

        self.style_download_tab = ttk.Style(self.download_tab)
        self.style_download_tab.configure('TButton', font=('Arial', 15))

        self.tabs.place(x=0, y=0, height=530, width=550)

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
        self.search_list_entry.place(x=0, y=0, height=30, width=529)
        self.search_list_variable.trace('w', self._search_list)
        self.select_file_playlist.trace('w', self._validation_select_file_playlist)

    def _download_tab(self):
        """
        Interface canvas configuration
        :return:
        """
        # Canvas configuration for insertion and search of links
        self.canvas_link = tkinter.Canvas(self.download_tab, width=550, height=150)
        self.canvas_link.pack()
        self.entry_youtube_link = ttk.Entry(self.download_tab, font=('Arial', 15), foreground='gray',
                                            textvariable=self.youtube_link_variable, width=35)
        self.entry_youtube_link.insert(0, 'Type here a youtube link')
        self.entry_youtube_link.bind('<FocusIn>', lambda event: self.focus_in(self.entry_youtube_link,
                                                                              'Type here a youtube link'))
        self.entry_youtube_link.bind('<FocusOut>', lambda event: self.focus_out(self.entry_youtube_link,
                                                                                'Type here a youtube link'))
        self.entry_youtube_link.bind('<Return>', lambda event: self._link_verify())
        self.entry_youtube_link.bind('<Enter>', lambda event: self._mouse_on_youtube_entry(True))
        self.entry_youtube_link.bind('<Leave>', lambda event: self._mouse_on_youtube_entry(False))

        self.canvas_link.create_window(200, 50, window=self.entry_youtube_link)
        self.btn_link_verify = ttk.Button(self.download_tab, text='    SEARCH    ',
                                          command=self._link_verify)

        self.btn_link_verify.bind('<Return>', lambda event: self._link_verify())
        self.canvas_link.create_window(470, 50, window=self.btn_link_verify)
        self.message_youtube_title = tkinter.Message(self.download_tab, font='Arial 10', width=400)
        self.canvas_link.create_window(280, 100, window=self.message_youtube_title)

        # Animation canvas setup during link search
        self.canvas_load_link = tkinter.Canvas(self.download_tab, width=250, height=130)
        self.label_load_link_verify = tkinter.Label(self.download_tab, font='Arial 30 bold')
        self.canvas_load_link.create_window(125, 65, window=self.label_load_link_verify)

        # Canvas configuration for file type selection (audio, video)
        self.canvas_file_type = tkinter.Canvas(self.download_tab, width=200, height=130)
        self.btn_video = ttk.Button(self.root, text='     Video     ', command=self._select_video)
        self.btn_video.bind('<Return>', lambda event: self._select_video())
        self.canvas_file_type.create_window(105, 40, window=self.btn_video)
        self.btn_audio = ttk.Button(self.download_tab, text='     Audio     ', command=self._select_audio)
        self.btn_audio.bind('<Return>', lambda event: self._select_audio())
        self.canvas_file_type.create_window(105, 100, window=self.btn_audio)

        # Canvas setting for selecting audio file download quality
        self.canvas_audio_download = tkinter.Canvas(self.download_tab, width=250, height=130)
        self.label_combo_audio_select = tkinter.Label(self.download_tab, font='Arial 10', text='Select a Quality: ')
        self.canvas_audio_download.create_window(125, 10, window=self.label_combo_audio_select)
        self.combo_quality_audio = ttk.Combobox(self.download_tab, font='Arial 15', state='readonly')
        self.canvas_audio_download.create_window(125, 40, window=self.combo_quality_audio)
        self.btn_audio_download = ttk.Button(self.download_tab, text='Download', command=self.download_file)
        self.btn_audio_download.bind('<Return>', lambda event: self.download_file())
        self.canvas_audio_download.create_window(125, 100, window=self.btn_audio_download)

        # Canvas setting for selecting video file download quality
        self.canvas_video_download = tkinter.Canvas(self.download_tab, width=250, height=130)
        self.label_combo_video_select = tkinter.Label(self.download_tab, font='Arial 10', text='Select a Quality: ')
        self.canvas_video_download.create_window(125, 10, window=self.label_combo_video_select)
        self.combo_quality_video = ttk.Combobox(self.download_tab, font='Arial 15', state='readonly')
        self.canvas_video_download.create_window(125, 40, window=self.combo_quality_video)
        self.btn_video_download = ttk.Button(self.download_tab, text='Download', command=self.download_file)
        self.btn_video_download.bind('<Return>', lambda event: self.download_file())
        self.canvas_video_download.create_window(125, 100, window=self.btn_video_download)

        # Canvas setting for selecting video playlist file download quality
        self.canvas_video_playlist_download = tkinter.Canvas(self.download_tab, width=542, height=80)
        self.label_select_video_playlist = tkinter.Label(self.download_tab, font='Arial 15', text='Choose Videos:')
        self.canvas_video_playlist_download.create_window(75, 20, window=self.label_select_video_playlist)
        self.entry_select_video_playlist = ttk.Entry(self.download_tab, font=('Arial', 15),
                                                     textvariable=self.select_file_playlist, width=19)
        self.canvas_video_playlist_download.create_window(255, 20, window=self.entry_select_video_playlist)
        self.btn_load_video_list = ttk.Button(self.download_tab, text='Load List', command=self._load_list_playlist)
        self.btn_load_video_list.bind('<Return>', lambda event: self._load_list_playlist())
        self.canvas_video_playlist_download.create_window(75, 60, window=self.btn_load_video_list)
        self.btn_highest_resolution = ttk.Button(self.download_tab, text='Highest Resolution',
                                                 command=lambda: self.download_file('highest_resolution'))
        self.btn_highest_resolution.bind('<Return>', lambda event: self.download_file('highest_resolution'))
        self.canvas_video_playlist_download.create_window(450, 20, window=self.btn_highest_resolution)
        self.btn_lowest_resolution = ttk.Button(self.download_tab, text='Lowest Resolution',
                                                command=lambda: self.download_file('lowest_resolution'))
        self.btn_lowest_resolution.bind('<Return>', lambda event: self.download_file('lowest_resolution'))
        self.canvas_video_playlist_download.create_window(450, 60, window=self.btn_lowest_resolution)

        # Canvas setting for selecting audio playlist file download
        self.canvas_audio_playlist_download = tkinter.Canvas(self.download_tab, width=542, height=80)
        self.label_select_audio_playlist = tkinter.Label(self.download_tab, font='Arial 15', text='Choose Audios:')
        self.canvas_audio_playlist_download.create_window(80, 20, window=self.label_select_audio_playlist)
        self.entry_select_audio_playlist = ttk.Entry(self.download_tab, font=('Arial', 15),
                                                     textvariable=self.select_file_playlist, width=20)
        self.canvas_audio_playlist_download.create_window(265, 20, window=self.entry_select_audio_playlist)
        self.btn_load_audio_list = ttk.Button(self.download_tab, text='Load List', command=self._load_list_playlist)
        self.btn_load_audio_list.bind('<Return>', lambda event: self._load_list_playlist())
        self.canvas_audio_playlist_download.create_window(75, 60, window=self.btn_load_audio_list)
        self.btn_audio_file = ttk.Button(self.download_tab, text='    Download    ', command=self.download_file)
        self.btn_audio_file.bind('<Return>', lambda event: self.download_file())
        self.canvas_audio_playlist_download.create_window(465, 20, window=self.btn_audio_file)

        # Download Status Canvas Setting
        self.canvas_download_status = tkinter.Canvas(self.download_tab, width=500, height=300)
        self.label_count_playlist = tkinter.Label(self.download_tab, font='Arial 15', fg='green')
        self.canvas_download_status.create_window(250, 50, window=self.label_count_playlist)
        self.label_download_name_file = tkinter.Message(self.download_tab, font='Arial 10', fg='green', width=400)
        self.canvas_download_status.create_window(250, 100, window=self.label_download_name_file)
        self.label_download_status = tkinter.Label(self.download_tab, font='Arial 15', fg='green')
        self.canvas_download_status.create_window(250, 150, window=self.label_download_status)
        self.btn_stop = ttk.Button(self.root, text='    Stop    ', style='btn_stop.TButton', command=self.stop_download)
        self.btn_stop.bind('<Return>', lambda event: self.stop_download())
        self.canvas_download_status.create_window(250, 250, window=self.btn_stop)
        self.label_download_progress_bar = ttk.Progressbar(self.canvas_download_status, orient=tkinter.HORIZONTAL,
                                                           mode='determinate', length=400)
        self.canvas_download_status.create_window(250, 200, window=self.label_download_progress_bar)
        self.label_download_progress_bar_count = tkinter.Label(self.download_tab, font='Arial 10', fg='green')
        self.canvas_download_status.create_window(480, 200, window=self.label_download_progress_bar_count)
        self.btn_force_stop = ttk.Button(self.download_tab, text='Force Stop', style='btn_force_stop.TButton',
                                         command=self.force_stop_download)
        self.btn_force_stop.bind('<Return>', lambda event: self.force_stop_download())
        self.style_download_tab.configure('btn_stop.TButton', font=('Arial', 15))
        self.style_download_tab.map('btn_stop.TButton', foreground=[('!disabled', 'red'), ('disabled', 'red')])
        self.style_download_tab.configure('btn_force_stop.TButton', font=('Arial', 10))
        self.style_download_tab.map('btn_force_stop.TButton', foreground=[('!disabled', 'red'), ('disabled', 'red')])

        # Canvas setting for the return button for selecting file type (audio, video)
        self.canvas_return = tkinter.Canvas(self.download_tab, width=50, height=50)
        self.canvas_return.place(y=445, x=0)
        self.btn_return = tkinter.Button(self.download_tab, text='<', font='Arial 15',
                                         borderwidth=0, command=self.return_page)
        self.btn_return.bind('<Return>', lambda event: self.return_page())
        self.canvas_return.create_window(25, 25, window=self.btn_return)
        self.btn_return.configure(state=tkinter.DISABLED)

    def _search_list(self, *args):
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

            pattern_index = self._find_pattern_index()

            if len(pattern_index) >= 1:

                # Instantiate the secondary list to receive incoming correspondence
                self.search_pattern_index._list_tabs()
                self.search_pattern_index.list_scrollbar_y.pack(side="right", fill="y")
                self.search_pattern_index.list_scrollbar_x.pack(side="bottom", fill="x")
                self.search_pattern_index.tree_view.place(x=0, y=50, height=437, width=529)

                # Add all matches found to the secondary list
                for i in range(1, len(pattern_index) + 1):
                    value = (self.tree_view.item(str(pattern_index[i - 1]), 'values'))
                    self.search_pattern_index._insert_list_tab(value[0], value[1], value[2], value[3],
                                                               value[4], value[5], value[6], value[7], value[8])

        elif self.search_list_variable.get() == '':

            # Destroys the secondary list if there are no matches requested
            self.search_pattern_index.tree_view.destroy()
            self.search_pattern_index.list_scrollbar_x.destroy()
            self.search_pattern_index.list_scrollbar_y.destroy()

            # Show the main list again
            self.tree_view.place(x=0, y=50, height=437, width=529)
            self.list_scrollbar_y.pack(side="right", fill="y")
            self.list_scrollbar_x.pack(side="bottom", fill="x")

    def _find_pattern_index(self):
        """
        Function responsible for finding the requested correspondence in the download list
        :return: Returns the indexes of matches found
        """
        pattern_index = []
        pattern = re.compile(re.escape(self.search_list_variable.get()) + '.*', re.IGNORECASE)
        for i in range(1, self.files_count_tree_view):
            tree_view_data = self.tree_view.item(str(i), 'values')
            x = re.search(pattern, tree_view_data[2])
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
        self.option_menu.add_command(label='Export list',
                                     command=lambda: self.export_list())
        self.option_menu.add_separator()
        self.option_menu.add_command(label='Exit', command=lambda: self.root.destroy())
        self.root.config(menu=self.new_menu)

    def _popup(self):
        self.popup_menu = tkinter.Menu(self.root, tearoff=0)

        self.popup_menu.add_command(label="Copy",
                                    command=lambda: self._copy_youtube_link())

        self.popup_menu.add_command(label="Paste",
                                    command=lambda: self._paste_youtube_link())
        self.popup_menu.add_separator()
        self.popup_menu.add_command(label="Clear",
                                    command=lambda: self._clear_youtube_link())

    def _do_popup(self, event):
        if self.mouse_on_youtube_entry_status:
            try:
                self.popup_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.popup_menu.grab_release()

    def _mouse_on_youtube_entry(self, status):
        self.mouse_on_youtube_entry_status = status

    def _copy_youtube_link(self):
        if self.youtube_link_variable.get() != 'Type here a youtube link':
            self.root.clipboard_append(self.youtube_link_variable.get())

    def _paste_youtube_link(self):
        self.focus_in(self.entry_youtube_link, 'Type here a youtube link')
        self.youtube_link_variable.set(self.root.clipboard_get())

    def _clear_youtube_link(self):
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

    def _loading_link_verify(self, *args):
        """
        Generates an animation while checking the link
        :param args: None
        :return:
        """
        _none = args
        while self._loading_link_verify_status:
            wait = 0.20
            self.label_load_link_verify['text'] = '|'
            time.sleep(wait)
            self.label_load_link_verify['text'] = '/'
            time.sleep(wait)
            self.label_load_link_verify['text'] = '-'
            time.sleep(wait)
            self.label_load_link_verify['text'] = '\\'
            time.sleep(wait)
            self.label_load_link_verify['text'] = '|'
            time.sleep(wait)
            self.label_load_link_verify['text'] = '/'
            time.sleep(wait)
            self.label_load_link_verify['text'] = '-'
            time.sleep(wait)
            self.label_load_link_verify['text'] = '\\'
            time.sleep(wait)
        self.canvas_load_link.place_forget()

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
            self._loading_link_verify_status = True
            self.canvas_load_link.place(x=150, y=200)
            start_new_thread(self._loading_link_verify, (None, None))
            self.block_interface()
            try:
                try:
                    self.playlist = Playlist(self.youtube_link_variable.get())
                    title = f'PLAYLIST: {self.playlist.title}'
                    self.youtube_type = 'playlist'
                    self.len_playlist_link = len(self.playlist)
                except KeyError:
                    self.youtube = YouTube(self.youtube_link_variable.get())
                    stream = self.youtube.streams
                    quality_video = self.get_video_quality(stream)
                    quality_audio = self.get_audio_quality(stream)
                    self.combo_quality_video['values'] = quality_video
                    self.combo_quality_audio['values'] = quality_audio
                    title = f'VIDEO: {self.youtube.title}'
                    self.youtube_type = 'video'
            except Exception as erro:
                self._loading_link_verify_status = False
                self.unblock_interface()
                messagebox.showerror('Error', str(erro))
                self.canvas_file_type.place_forget()
                if self.select_type != '':
                    if self.select_type == 'audio':
                        self.canvas_audio_download.place_forget()
                    elif self.select_type == 'video':
                        self.canvas_video_download.place_forget()
            else:
                self._loading_link_verify_status = False
                self.unblock_interface()
                self.message_youtube_title['text'] = title
                self.canvas_file_type.place(x=170, y=200)
                self.link = self.youtube_link_variable.get()
        else:
            self.select_type = ''
            self.message_youtube_title['text'] = ''
            self.canvas_file_type.place_forget()

    def _link_verify(self):
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
        if self.select_type == 'audio':
            if self.youtube_type == 'video':
                self.canvas_audio_download.place_forget()
            elif self.youtube_type == 'playlist':
                self.canvas_audio_playlist_download.place_forget()
        elif self.select_type == 'video':
            if self.youtube_type == 'video':
                self.canvas_video_download.place_forget()
            elif self.youtube_type == 'playlist':
                self.canvas_video_playlist_download.place_forget()
        elif self.select_type == '':
            self.canvas_file_type.place_forget()
        self.combo_quality_video.set('')
        self.combo_quality_audio.set('')
        self.select_file_playlist.set('')
        self.btn_return.configure(state=tkinter.DISABLED)

        if self.load_list_playlist_status:
            self.load_list_playlist_status = False
            self._close_list_playlist()

    def return_page(self):
        """
        Return to file type selection menu (audio, video)
        :return:
        """
        if self.select_type == 'audio':
            if self.youtube_type == 'video':
                self.canvas_audio_download.place_forget()
            elif self.youtube_type == 'playlist':
                self.canvas_audio_playlist_download.place_forget()
        elif self.select_type == 'video':
            if self.youtube_type == 'video':
                self.canvas_video_download.place_forget()
            elif self.youtube_type == 'playlist':
                self.canvas_video_playlist_download.place_forget()
        if self.combo_quality_audio.get() != '':
            self.combo_quality_audio.set('')
        if self.combo_quality_video.get() != '':
            self.combo_quality_video.set('')
        self.canvas_file_type.place(x=170, y=200)
        self.btn_return.configure(state=tkinter.DISABLED)

        if self.load_list_playlist_status:
            self.load_list_playlist_status = False
            self._close_list_playlist()

        self.select_type = ''

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

    @staticmethod
    def mp4_to_mp3(mp4, mp3):
        """
        Convert mp4 file to mp3
        :param mp4: File to be converted
        :param mp3: New Converted File Name
        :return: Returns a file converted to mp3
        """
        mp4_without_frames = AudioFileClip(mp4)
        mp4_without_frames.write_audiofile(mp3, verbose=False, logger=main)
        mp4_without_frames.close()

    def set_progress_callback(self, percent: str):
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

    def _start_download(self):
        """
        Removes options canvas and added status download canvas
        :return:
        """
        self.block_interface()
        if self.select_type == 'audio':
            if self.youtube_type == 'video':
                self.canvas_audio_download.place_forget()
            elif self.youtube_type == 'playlist':
                self.canvas_audio_playlist_download.place_forget()
        elif self.select_type == 'video':
            if self.youtube_type == 'video':
                self.canvas_video_download.place_forget()
            elif self.youtube_type == 'playlist':
                self.canvas_video_playlist_download.place_forget()

        if self.load_list_playlist_status:
            self.load_list_playlist_status = False
            self._close_list_playlist()

        self.canvas_download_status.place(x=20, y=140)

    def _download_finished(self):
        """
        Show the options canvas after the download finishes
        :return:
        """
        messagebox.showinfo('Info', 'Download Finished')
        self.canvas_download_status.place_forget()
        self.unblock_interface()

        if self.select_type == 'audio':
            if self.youtube_type == 'video':
                self.canvas_audio_download.place(x=150, y=230)
            elif self.youtube_type == 'playlist':
                self.canvas_audio_playlist_download.place(x=0, y=150)

        elif self.select_type == 'video':
            if self.youtube_type == 'video':
                self.canvas_video_download.place(x=150, y=200)
            elif self.youtube_type == 'playlist':
                self.canvas_video_playlist_download.place(x=0, y=150)

        self.label_count_playlist['text'] = ''
        self.label_download_name_file['text'] = ''
        self.label_download_status['text'] = ''
        self.label_download_progress_bar_count['text'] = ''
        self.label_download_progress_bar['value'] = 0

        if self.stop_download_status:
            self.btn_stop.configure(state=tkinter.ACTIVE)
            self.btn_stop['text'] = '    Stop    '
            self.stop_download_status = False
            self.btn_force_stop.place_forget()

        self.select_file_playlist.set('')

    def _close_list_playlist(self):
        """
        Function responsible for closing the playlist list
        :return:
        """
        if not self.load_list_playlist_status and self.select_type != '' and self.youtube_type == 'playlist':
            if self.select_type == 'audio':
                self.btn_load_audio_list['text'] = 'Load List'
            elif self.select_type == 'video':
                self.btn_load_video_list['text'] = 'Load List'
            self.canvas_list_playlist.place_forget()

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

            # Instantiation of "listbox_list_playlist" canvas
            self.canvas_list_playlist = tkinter.Canvas(self.download_tab, width=542, height=200)

            # Instance of the scrollbars of the "listbox_list_playlist" canvas
            list_playlist_scrollbar_y = tkinter.Scrollbar(self.canvas_list_playlist, orient='vertical')
            list_playlist_scrollbar_y.pack(side="right", fill="y")

            list_playlist_scrollbar_x = tkinter.Scrollbar(self.canvas_list_playlist, orient='horizontal')
            list_playlist_scrollbar_x.pack(side="bottom", fill="x")

            self.listbox_list_playlist = tkinter.Listbox(self.canvas_list_playlist,
                                                         width=72, height=10, font='Arial 10',
                                                         yscrollcommand=list_playlist_scrollbar_y.set,
                                                         xscrollcommand=list_playlist_scrollbar_x.set,
                                                         activestyle='none')
            self.listbox_list_playlist.pack(padx=10, pady=10)
            list_playlist_scrollbar_y.config(command=self.listbox_list_playlist.yview)
            list_playlist_scrollbar_x.config(command=self.listbox_list_playlist.xview)

            self.canvas_list_playlist.place(x=0, y=230)

            start_new_thread(self._thread_load_list_playlist, (self.listbox_list_playlist, None))
        elif not self.load_list_playlist_status:
            self._close_list_playlist()

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

    def _get_select_file_playlist(self):
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

    def _validation_select_file_playlist(self, *args):
        """
        Function responsible for verifying the chosen links
        :param args: None
        :return: Returns if the choice is valid, and a list of the chosen links indexes
        """
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
                find = re.findall(r'[\d]+|[\-]', select)

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
                if self.select_type == 'audio':
                    self.btn_audio_file.configure(state=tkinter.ACTIVE)
                    self.entry_select_audio_playlist['foreground'] = 'green'
                elif self.select_type == 'video':
                    self.btn_highest_resolution.configure(state=tkinter.ACTIVE)
                    self.btn_lowest_resolution.configure(state=tkinter.ACTIVE)
                    self.entry_select_video_playlist['foreground'] = 'green'
            else:
                if self.select_type == 'audio':
                    self.btn_audio_file.configure(state=tkinter.DISABLED)
                    self.entry_select_audio_playlist['foreground'] = 'red'
                elif self.select_type == 'video':
                    self.btn_highest_resolution.configure(state=tkinter.DISABLED)
                    self.btn_lowest_resolution.configure(state=tkinter.DISABLED)
                    self.entry_select_video_playlist['foreground'] = 'red'
            return flag, data
        else:
            if self.select_type == 'audio':
                self.btn_audio_file.configure(state=tkinter.ACTIVE)
            elif self.select_type == 'video':
                self.btn_highest_resolution.configure(state=tkinter.ACTIVE)
                self.btn_lowest_resolution.configure(state=tkinter.ACTIVE)

    def _download_youtube_file(self, save_path, url=None, quality=None):
        youtube = ''
        if self.select_type == 'audio':
            if self.youtube_type == 'video':
                youtube = YouTube(self.link, on_progress_callback=self.progress_callback).streams.filter(
                    abr=str(self.combo_quality_audio.get()),
                    only_audio=True,
                    file_extension='mp4')[0].download(save_path)

            elif self.youtube_type == 'playlist':
                youtube = YouTube(url, on_progress_callback=self.progress_callback) \
                    .streams.get_audio_only().download(save_path)

        elif self.select_type == 'video':
            if self.youtube_type == 'video':
                youtube = YouTube(self.link, on_progress_callback=self.progress_callback) \
                    .streams.filter(res=str(re.findall(r'^\d{3}p', self.combo_quality_video.get())[0]),
                                    progressive=True, file_extension='mp4')[0].download(save_path)

            elif self.youtube_type == 'playlist':
                if quality == 'lowest_resolution':
                    youtube = YouTube(url, on_progress_callback=self.progress_callback) \
                        .streams.get_lowest_resolution().download(save_path)

                elif quality == 'highest_resolution':
                    youtube = YouTube(url, on_progress_callback=self.progress_callback) \
                        .streams.get_highest_resolution().download(save_path)

        return youtube

    def _thread_download_file(self, *args):
        """
        Download playlist audio files and videos
        :param args: None
        :return:
        """
        quality = args[0]
        save_path = filedialog.askdirectory()  # Get the path selected by the user to save the file
        if save_path != '' and save_path != ():
            self._start_download()
            # Check the file type (video or playlist) and download
            if self.youtube_type == 'video':
                self.label_download_status['text'] = f'Downloading {self.select_type.title()}, Please Wait.'
                self.label_download_progress_bar_count['text'] = '0%'
                self.label_download_progress_bar['value'] = 0
                if self.select_type == 'audio':
                    quality = self.combo_quality_audio.get()
                elif self.select_type == 'video':
                    quality = self.combo_quality_video.get()
                try:
                    youtube = self.youtube
                    self.duration = time.strftime("%H:%M:%S", time.gmtime(youtube.length))
                    self.label_download_name_file['text'] = youtube.title
                    self._insert_list_tab(index=str(self.files_count_tree_view),
                                          status='DOWNLOADING',
                                          title=self.label_download_name_file["text"],
                                          format_file=f'{self.select_type.upper()}',
                                          duration=self.duration,
                                          quality=quality,
                                          size='-',
                                          path=save_path,
                                          url=self.link)

                    youtube = self._download_youtube_file(save_path)

                    if self.select_type == 'audio':
                        try:
                            self.label_download_status['text'] = f'Converting {self.select_type}, Please Wait.'
                            self.set_progress_callback(percent='0')
                            self._edit_list_tab(index=str(self.files_count_tree_view),
                                                status='CONVERTING',
                                                title=self.label_download_name_file["text"],
                                                format_file=f'{self.select_type.upper()}',
                                                duration=self.duration,
                                                quality=quality,
                                                size='-',
                                                path=save_path,
                                                url=self.link)
                            self.mp4_to_mp3(str(youtube), f'{youtube.replace(".mp4", ".mp3")}')
                            os.remove(youtube)
                        except Exception as erro:
                            messagebox.showerror('Error', str(erro))
                            os.remove(youtube)
                            self.restart()
                except exceptions.AgeRestrictedError:
                    self._edit_list_tab(index=str(self.files_count_tree_view),
                                        status='FAIL',
                                        title=self.label_download_name_file["text"],
                                        format_file=f'{self.select_type.upper()}',
                                        duration=self.duration,
                                        quality=quality,
                                        size='-',
                                        path='-',
                                        url=self.link)
                    self.files_count_tree_view += 1
                except Exception as erro:
                    messagebox.showerror('Error', str(erro))
                    self.restart()
                else:
                    file_size = os.path.getsize(youtube.replace('.mp4', '.mp3')) / 1048576
                    file_size = f'{file_size:.2f} MB'
                    self._edit_list_tab(index=str(self.files_count_tree_view),
                                        status='SUCCESS',
                                        title=self.label_download_name_file["text"],
                                        format_file=f'{self.select_type.upper()}',
                                        duration=self.duration,
                                        quality=quality,
                                        size=file_size,
                                        path=str(youtube),
                                        url=self.link)
                    self.files_count_tree_view += 1
                    self.files_count_ok += 1
            elif self.youtube_type == 'playlist':
                if self.select_file_playlist.get() == '':
                    playlist = self.playlist
                else:
                    playlist = self._get_select_file_playlist()
                count = 0
                for url in playlist:
                    self.label_count_playlist['text'] = f'FILE: {str(count)}/{str(len(playlist))}'
                    self.label_download_status['text'] = 'Downloading Audio Playlist, please wait.'
                    self.set_progress_callback(percent='0')
                    try:
                        youtube = YouTube(url)
                        self.duration = time.strftime("%H:%M:%S", time.gmtime(youtube.length))
                        self.label_download_name_file['text'] = youtube.title
                        self._insert_list_tab(index=str(self.files_count_tree_view),
                                              status='DOWNLOADING',
                                              title=self.label_download_name_file["text"],
                                              format_file=f'{self.select_type.upper()}',
                                              duration=self.duration,
                                              quality=f'{quality.replace("_", " ").title()}',
                                              size='-',
                                              path=save_path,
                                              url=url)

                        youtube = self._download_youtube_file(save_path=save_path, url=url, quality=quality)
                        if self.select_type == 'audio':
                            try:
                                self.label_download_status['text'] = \
                                    f'Converting {self.select_type.title()}, please wait.'
                                self.label_download_progress_bar_count['text'] = f'0%'
                                self.label_download_progress_bar['value'] = 0
                                self._edit_list_tab(index=str(self.files_count_tree_view),
                                                    status='CONVERTING',
                                                    title=self.label_download_name_file["text"],
                                                    format_file=f'{self.select_type.upper()}',
                                                    duration=self.duration,
                                                    quality=f'{quality.replace("_", " ").title()}',
                                                    size='-',
                                                    path=save_path,
                                                    url=url)
                                self.mp4_to_mp3(str(youtube), f'{youtube.replace(".mp4", ".mp3")}')
                                os.remove(youtube)
                            except Exception as erro:
                                messagebox.showerror('Error', str(erro))
                                os.remove(youtube)
                                self.restart()
                    except exceptions.AgeRestrictedError:
                        self._edit_list_tab(index=str(self.files_count_tree_view),
                                            status='FAIL',
                                            title=self.label_download_name_file["text"],
                                            format_file=f'{self.select_type.upper()}',
                                            duration=self.duration,
                                            quality=f'{quality.replace("_", " ").title()}',
                                            size='-',
                                            path='-',
                                            url=url)
                        self.files_count_tree_view += 1
                    except Exception as erro:
                        messagebox.showerror('Error', str(erro))
                        self.restart()
                    else:
                        file_size = os.path.getsize(youtube.replace('.mp4', '.mp3')) / 1048576
                        file_size = f'{file_size:.2f} MB'
                        self._edit_list_tab(index=str(self.files_count_tree_view),
                                            status='SUCCESS',
                                            title=self.label_download_name_file["text"],
                                            format_file=f'{self.select_type.upper()}',
                                            duration=self.duration,
                                            quality=f'{quality.replace("_", " ").title()}',
                                            size=file_size,
                                            path=str(youtube),
                                            url=url)
                        count += 1
                        self.files_count_tree_view += 1
                        self.files_count_ok += 1
                    if self.stop_download_status:
                        break
                    self.label_count_playlist['text'] = f'FILE: {str(count)}/{str(len(playlist))}'
            self._download_finished()

    def download_file(self, quality=None):
        """
        Starts the thread for downloading audio files
        :return:
        """
        if self.select_type == 'audio':
            if self.youtube_type == 'video':
                if self.combo_quality_audio.get() == '':
                    messagebox.showerror('Error', 'Please Select a Quality')
                else:
                    start_new_thread(self._thread_download_file, (None, None))

            elif self.youtube_type == 'playlist':
                start_new_thread(self._thread_download_file, ('highest_quality', None))

        elif self.select_type == 'video':
            if self.youtube_type == 'video':
                if self.combo_quality_video.get() == '':
                    messagebox.showerror('Error', 'Please Select a Quality')
                else:
                    start_new_thread(self._thread_download_file, (None, None))

            elif self.youtube_type == 'playlist':
                start_new_thread(self._thread_download_file, (quality, None))

    @staticmethod
    def get_audio_quality(stream):
        """
        Get the audio quality and return it in a list to be used in the audio combobox
        :param stream: Stream of videos generated by pytube
        :return: Returns a list of the audio quality of the video
        """
        yt = stream.filter(file_extension='mp4', only_audio=True)
        quality_list = []
        for c in yt:
            quality_list.append(re.findall(r'\d{2,3}kbps', str(c)))
        return quality_list

    @staticmethod
    def get_video_quality(stream):
        """
        Get the quality and fps of the video and return it in a list to be used in the video combobox
        :param stream: Stream of videos generated by pytube
        :return: Returns a list of the quality and fps of the videos
        """
        yt = stream.filter(file_extension='mp4', progressive=True)
        quality_list = []
        for c in yt:
            quality_list.append(re.findall(r'\d{3}p|\d{2}fps', str(c)))
        return quality_list

    def _select_audio(self):
        """
        Enable audio canvas
        :return:
        """
        self.select_type = 'audio'
        self.canvas_file_type.place_forget()
        self.btn_return.configure(state=tkinter.ACTIVE)
        if self.youtube_type == 'video':
            self.canvas_audio_download.place(x=150, y=200)
        elif self.youtube_type == 'playlist':
            self.canvas_audio_playlist_download.place(x=0, y=150)

    def _select_video(self):
        """
        Enable video canvas
        :return:
        """
        self.select_type = 'video'
        self.canvas_file_type.place_forget()
        self.btn_return.configure(state=tkinter.ACTIVE)
        if self.youtube_type == 'video':
            self.canvas_video_download.place(x=150, y=200)
        elif self.youtube_type == 'playlist':
            self.canvas_video_playlist_download.place(x=0, y=150)

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
            self.btn_force_stop.place(x=228, y=430)

    def start_mainloop(self):
        """
        Start tkinter mainloop
        :return:
        """
        self.root.mainloop()


class Main(TqdmProgressBarLogger, Gui):
    """
    The moviepy library doesn't have a native write_audiofile callback function,
    so Proglog.TqdmProgressBarLogger is used to capture the progress bar
    """

    def callback(self, **changes):
        """
        TqdmProgressBarLogger function
        Every time the logger is updated, this function is called
        :param changes:
        :return:
        """
        if len(self.bars):
            percentage = next(reversed(self.bars.items()))[1]['index'] / next(reversed(self.bars.items()))[1]['total']
            percentage = str(percentage * 100).split('.')[0]
            self.set_progress_callback(percent=percentage)

    def start_gui(self):
        """
        Start the graphical interface
        :return:
        """
        Gui.__init__(self)
        self.start_mainloop()


class Download(Main):
    pass


if __name__ == '__main__':
    main = Download()
    main.start_gui()
