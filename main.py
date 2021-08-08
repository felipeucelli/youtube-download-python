import tkinter
from tkinter import filedialog
from _thread import start_new_thread
from os import rename
from pytube import YouTube, Playlist


class Interface:
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title('Youtube Download')
        self.root.resizable(width=False, height=False)
        self.root.geometry('550x500')

        self.select_type = ''
        self.youtube_type = ''
        self.youtube_link_variable = tkinter.StringVar()

        self._interface()

    def _interface(self):
        self.canvas_link = tkinter.Canvas(self.root, width=550, height=100)
        self.canvas_link.pack()

        self.youtube_link = tkinter.Entry(self.root, font='Arial 15', textvariable=self.youtube_link_variable, width=35)
        self.youtube_link.insert(0, 'Type here a youtube link')
        self.youtube_link.bind('<Button-1>', lambda event: self.clear_entry())
        self.canvas_link.create_window(200, 50, window=self.youtube_link)
        self.verify = tkinter.Button(self.root, text='    SEARCH    ', font='Arial 15', command=self._link_verify)
        self.canvas_link.create_window(470, 50, window=self.verify)
        self.label_title = tkinter.Label(self.root, font='Arial 10')
        self.canvas_link.create_window(280, 100, window=self.label_title)

        self.canvas_file_type = tkinter.Canvas(self.root, width=200, height=130)
        self.btn_video = tkinter.Button(self.root, text='     Video     ', font='Arial 15',
                                        command=self._select_video)
        self.canvas_file_type.create_window(105, 40, window=self.btn_video)
        self.btn_audio = tkinter.Button(self.root, text='     Audio     ', font='Arial 15',
                                        command=self._select_audio)
        self.canvas_file_type.create_window(105, 100, window=self.btn_audio)

        self.canvas_video_download = tkinter.Canvas(self.root, width=250, height=130)
        self.btn_highest_resolution = tkinter.Button(self.root, text='Highest Resolution', font='Arial 15',
                                                     command=self.download_highest_resolution)
        self.canvas_video_download.create_window(125, 40, window=self.btn_highest_resolution)
        self.btn_lowest_resolution = tkinter.Button(self.root, text='Lowest Resolution', font='Arial 15',
                                                    command=self.download_lowest_resolution)
        self.canvas_video_download.create_window(125, 100, window=self.btn_lowest_resolution)

        self.canvas_audio_download = tkinter.Canvas(self.root, width=250, height=100)
        self.btn_audio_file = tkinter.Button(self.root, text='    Download    ', font='Arial 15',
                                             command=self.download_audio)
        self.canvas_audio_download.create_window(125, 50, window=self.btn_audio_file)

        self.canvas_return = tkinter.Canvas(self.root, width=50, height=50)
        self.canvas_return.place(y=445, x=0)
        self.btn_return = tkinter.Button(self.root, text='<', font='Arial 15', borderwidth=0, command=self.return_page)
        self.canvas_return.create_window(25, 25, window=self.btn_return)
        self.btn_return.configure(state=tkinter.DISABLED)

    def _link_verify(self):
        self.reset_interface()
        self.label_title['text'] = ''
        if self.youtube_link_variable.get() != '' and self.youtube_link_variable.get() != 'Type here a youtube link':
            try:
                try:
                    playlist = Playlist(self.youtube_link_variable.get())
                    title = f'Playlist: {playlist.title}'
                    self.youtube_type = 'playlist'
                except:
                    youtube = YouTube(self.youtube_link_variable.get())
                    title = f'Video:  {youtube.title}'
                    self.youtube_type = 'video'
            except Exception as erro:
                print(erro)
            else:
                self.label_title['text'] = title
                self.canvas_file_type.place(x=170, y=200)
        else:
            self.label_title['text'] = ''
            self.canvas_file_type.place_forget()

    def block_interface(self):
        self.youtube_link.configure(state=tkinter.DISABLED)
        self.verify.configure(state=tkinter.DISABLED)
        self.btn_return.configure(state=tkinter.DISABLED)

    def unblock_interface(self):
        self.youtube_link.configure(state=tkinter.NORMAL)
        self.verify.configure(state=tkinter.ACTIVE)
        self.btn_return.configure(state=tkinter.ACTIVE)

    def reset_interface(self):
        if self.select_type == 'audio':
            self.btn_audio_file.place_forget()
        elif self.select_type == 'video':
            self.canvas_video_download.place_forget()
        self.btn_return.configure(state=tkinter.DISABLED)

    def return_page(self):
        self.canvas_file_type.place(x=170, y=200)
        if self.select_type == 'audio':
            self.canvas_audio_download.place_forget()
        elif self.select_type == 'video':
            self.canvas_video_download.place_forget()

        self.btn_return.configure(state=tkinter.DISABLED)

        self.select_type = ''

    def clear_entry(self):
        self.youtube_link.delete(0, 'end')

    def _thread_download_audio(self, *args):
        path = filedialog.askdirectory()
        if path != '':
            self.block_interface()
            if self.youtube_type == 'video':
                youtube = YouTube(self.youtube_link_variable.get()).streams.get_audio_only().download(path)
                rename(f'{youtube.title()}', f'{youtube.title()}.mp3')
            elif self.youtube_type == 'playlist':
                playlist = Playlist(self.youtube_link_variable.get())
                for url in playlist:
                    youtube = YouTube(url).streams.get_audio_only().download(path)
                    rename(f'{youtube.title()}', f'{youtube.title()}.mp3')
            self.unblock_interface()

    def _thread_download_highest_resolution(self, *args):
        path = filedialog.askdirectory()
        if path != '':
            self.block_interface()
            if self.youtube_type == 'video':
                YouTube(self.youtube_link_variable.get()).streams.get_highest_resolution().download(path)
            elif self.youtube_type == 'playlist':
                playlist = Playlist(self.youtube_link_variable.get())
                for url in playlist:
                    YouTube(url).streams.get_highest_resolution().download(path)
            self.unblock_interface()

    def _thread_download_lowest_resolution(self, *args):
        path = filedialog.askdirectory()
        if path != '':
            self.block_interface()
            if self.youtube_type == 'video':
                YouTube(self.youtube_link_variable.get()).streams.get_lowest_resolution().download(path)
            elif self.youtube_type == 'playlist':
                playlist = Playlist(self.youtube_link_variable.get())
                for url in playlist:
                    YouTube(url).streams.get_lowest_resolution().download(path)
            self.unblock_interface()

    def download_audio(self):
        start_new_thread(self._thread_download_audio, (None, None))

    def download_highest_resolution(self):
        start_new_thread(self._thread_download_highest_resolution, (None, None))

    def download_lowest_resolution(self):
        start_new_thread(self._thread_download_lowest_resolution, (None, None))

    def _select_audio(self):
        self.select_type = 'audio'
        self.canvas_file_type.place_forget()
        self.btn_return.configure(state=tkinter.ACTIVE)
        self.canvas_audio_download.place(x=150, y=230)

    def _select_video(self):
        self.select_type = 'video'
        self.canvas_file_type.place_forget()
        self.btn_return.configure(state=tkinter.ACTIVE)
        self.canvas_video_download.place(x=150, y=200)

    def start(self):
        self.root.mainloop()


if __name__ == '__main__':
    main = Interface()
    main.start()
