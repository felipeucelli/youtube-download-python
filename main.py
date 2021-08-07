import tkinter
from tkinter import filedialog


class Interface:
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title('Youtube Download')
        self.root.resizable(width=False, height=False)
        self.root.geometry('300x250')

        self.youtube_link_variable = tkinter.StringVar()

        self.youtube_link = tkinter.Entry(self.root, font='Arial 15', textvariable=self.youtube_link_variable)
        self.youtube_link.insert(0, 'Type here a youtube link')
        self.youtube_link.bind('<Button-1>', lambda event: self.clear_entry())
        self.youtube_link.pack(pady=20)

        self.btn_video = tkinter.Button(self.root, text='     Video     ', font='Arial 15',
                                        command=self._select_video)

        self.btn_playlist = tkinter.Button(self.root, text='    Playlist    ', font='Arial 15',
                                           command=self._select_playlist)

        self.youtube_link_variable.trace('w', self.link_verify)

    def link_verify(self, *args):
        if self.youtube_link_variable.get() != 'Type here a youtube link' and self.youtube_link_variable.get() != '':
            if self.youtube_link_variable.get() in 'https://www.youtube.com/':
                self.btn_playlist.place(x=85, y=140)
                self.btn_video.place(x=85, y=80)
            else:
                self.btn_playlist.place_forget()
                self.btn_video.place_forget()
        else:
            self.btn_playlist.place_forget()
            self.btn_video.place_forget()

    def clear_entry(self):
        self.youtube_link.delete(0, 'end')

    def _select_playlist(self):
        self.btn_playlist.place_forget()
        self.btn_video.place_forget()
        self.youtube_link.pack_forget()

        self.btn_audio_file = tkinter.Button(self.root, text='    Audio    ', font='Arial 15')
        self.btn_audio_file.place(x=85, y=80)

        self.btn_video_file = tkinter.Button(self.root, text='    Video    ', font='Arial 15')
        self.btn_video_file.place(x=85, y=140)

    def _select_video(self):
        self.btn_playlist.place_forget()
        self.btn_video.place_forget()
        self.youtube_link.pack_forget()

        self.btn_audio_file = tkinter.Button(self.root, text='    Audio    ', font='Arial 15')
        self.btn_audio_file.place(x=85, y=80)

        self.btn_video_file = tkinter.Button(self.root, text='    Video    ', font='Arial 15')
        self.btn_video_file.place(x=85, y=140)

    def start(self):
        self.root.mainloop()


if __name__ == '__main__':
    main = Interface()
    main.start()
