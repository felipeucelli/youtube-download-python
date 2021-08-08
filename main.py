import tkinter
from tkinter import filedialog
from pytube import YouTube, Playlist


class Interface:
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title('Youtube Download')
        self.root.resizable(width=False, height=False)
        self.root.geometry('550x500')

        self.select_type = ''
        self.youtube_link_variable = tkinter.StringVar()

        self._interface()

    def _interface(self):
        self.canvas_1 = tkinter.Canvas(self.root, width=300, height=100)
        self.canvas_1.pack()

        self.youtube_link = tkinter.Entry(self.root, font='Arial 15', textvariable=self.youtube_link_variable, width=35)
        self.youtube_link.insert(0, 'Type here a youtube link')
        self.youtube_link.bind('<Button-1>', lambda event: self.clear_entry())
        self.canvas_1.create_window(80, 60, window=self.youtube_link)

        self.btn_video = tkinter.Button(self.root, text='     Video     ', font='Arial 15',
                                        command=self._select_video)

        self.btn_audio = tkinter.Button(self.root, text='     Audio     ', font='Arial 15',
                                        command=self._select_audio)

        self.verify = tkinter.Button(self.root, text='    SEARCH    ', font='Arial 15', command=self._link_verify)
        self.canvas_1.create_window(350, 60, window=self.verify)

        self.label_title = tkinter.Label(self.root, font='Arial 10')
        self.canvas_1.create_window(150, 100, window=self.label_title)

        self.canvas_3 = tkinter.Canvas(self.root, width=50, height=50)
        self.canvas_3.place(y=445, x=0)

        self.btn_return = tkinter.Button(self.root, text='<', font='Arial 15', borderwidth=0, command=self.return_page)
        self.canvas_3.create_window(25, 25, window=self.btn_return)
        self.btn_return.configure(state=tkinter.DISABLED)

    def _link_verify(self):
        self.reset_interface()
        self.label_title['text'] = ''
        if self.youtube_link_variable.get() != '' and self.youtube_link_variable.get() != 'Type here a youtube link':
            try:
                try:
                    playlist = Playlist(self.youtube_link_variable.get())
                    title = f'Playlist: {playlist.title}'
                except:
                    youtube = YouTube(self.youtube_link_variable.get())
                    title = f'Video:  {youtube.title}'
            except Exception as erro:
                print(erro)
            else:
                self.label_title['text'] = title

                self.btn_audio.place(x=205, y=300)
                self.btn_video.place(x=205, y=240)
        else:
            self.label_title['text'] = ''
            self.btn_audio.place_forget()
            self.btn_video.place_forget()

    def reset_interface(self):
        if self.select_type == 'audio':
            self.btn_audio_file.place_forget()
        elif self.select_type == 'video':
            self.btn_highest_resolution.place_forget()
            self.btn_lowest_resolution.place_forget()
        self.btn_return.configure(state=tkinter.DISABLED)

    def return_page(self):
        self.btn_audio.place(x=205, y=300)
        self.btn_video.place(x=205, y=240)

        if self.select_type == 'audio':
            self.btn_audio_file.place_forget()
        elif self.select_type == 'video':
            self.btn_highest_resolution.place_forget()
            self.btn_lowest_resolution.place_forget()

        self.btn_return.configure(state=tkinter.DISABLED)

        self.select_type = ''

    def clear_entry(self):
        self.youtube_link.delete(0, 'end')

    def _select_audio(self):
        self.select_type = 'audio'
        self.btn_audio.place_forget()
        self.btn_video.place_forget()
        self.btn_return.configure(state=tkinter.ACTIVE)

        self.btn_audio_file = tkinter.Button(self.root, text='    Download    ', font='Arial 15')
        self.btn_audio_file.place(x=200, y=250)

    def _select_video(self):
        self.select_type = 'video'
        self.btn_audio.place_forget()
        self.btn_video.place_forget()
        self.btn_return.configure(state=tkinter.ACTIVE)

        self.btn_highest_resolution = tkinter.Button(self.root, text='Highest Resolution', font='Arial 15')
        self.btn_highest_resolution.place(x=180, y=300)

        self.btn_lowest_resolution = tkinter.Button(self.root, text='Lowest Resolution', font='Arial 15')
        self.btn_lowest_resolution.place(x=180, y=240)

    def start(self):
        self.root.mainloop()


if __name__ == '__main__':
    main = Interface()
    main.start()
