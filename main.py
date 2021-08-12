# -*- coding: utf-8 -*-

# @autor: Felipe Ucelli
# @github: github.com/felipeucelli

# Built-in
import sys
import os
import tkinter
from tkinter import filedialog
from tkinter import messagebox
from _thread import start_new_thread

from moviepy.audio.io.AudioFileClip import AudioFileClip
from pytube import YouTube, Playlist


class Interface:
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title('Youtube Download')
        self.root.resizable(width=False, height=False)
        self.root.geometry('550x500')

        self.select_type = ''
        self.youtube_type = ''
        self.link = ''
        self.youtube_link_variable = tkinter.StringVar()

        self._interface()

    def _interface(self):
        """
        Interface canvas configuration
        :return:
        """
        # Canvas configuration for insertion and search of links
        self.canvas_link = tkinter.Canvas(self.root, width=550, height=100)
        self.canvas_link.pack()
        self.entry_youtube_link = tkinter.Entry(self.root, font='Arial 15',
                                                textvariable=self.youtube_link_variable, width=35)
        self.entry_youtube_link.insert(0, 'Type here a youtube link')
        self.entry_youtube_link.bind('<Button-1>', lambda event: self.clear_entry())
        self.canvas_link.create_window(200, 50, window=self.entry_youtube_link)
        self.verify = tkinter.Button(self.root, text='    SEARCH    ', font='Arial 15', command=self._link_verify)
        self.canvas_link.create_window(470, 50, window=self.verify)
        self.label_title = tkinter.Label(self.root, font='Arial 10')
        self.canvas_link.create_window(280, 100, window=self.label_title)

        # Canvas configuration for file type selection (audio, video)
        self.canvas_file_type = tkinter.Canvas(self.root, width=200, height=130)
        self.btn_video = tkinter.Button(self.root, text='     Video     ', font='Arial 15',
                                        command=self._select_video)
        self.canvas_file_type.create_window(105, 40, window=self.btn_video)
        self.btn_audio = tkinter.Button(self.root, text='     Audio     ', font='Arial 15',
                                        command=self._select_audio)
        self.canvas_file_type.create_window(105, 100, window=self.btn_audio)

        # Canvas setting for selecting video file download quality
        self.canvas_video_download = tkinter.Canvas(self.root, width=250, height=130)
        self.btn_highest_resolution = tkinter.Button(self.root, text='Highest Resolution', font='Arial 15',
                                                     command=self.download_highest_resolution)
        self.canvas_video_download.create_window(125, 40, window=self.btn_highest_resolution)
        self.btn_lowest_resolution = tkinter.Button(self.root, text='Lowest Resolution', font='Arial 15',
                                                    command=self.download_lowest_resolution)
        self.canvas_video_download.create_window(125, 100, window=self.btn_lowest_resolution)

        # Audio file download button canvas setting
        self.canvas_audio_download = tkinter.Canvas(self.root, width=250, height=100)
        self.btn_audio_file = tkinter.Button(self.root, text='    Download    ', font='Arial 15',
                                             command=self.download_audio)
        self.canvas_audio_download.create_window(125, 50, window=self.btn_audio_file)

        # Download Status Canvas Setting
        self.canvas_download_status = tkinter.Canvas(self.root, width=500, height=300)
        self.label_count_playlist = tkinter.Label(self.root, font='Arial 15', fg='green')
        self.canvas_download_status.create_window(250, 50, window=self.label_count_playlist)
        self.label_download_name_file = tkinter.Label(self.root, font='Arial 10', fg='green')
        self.canvas_download_status.create_window(250, 100, window=self.label_download_name_file)
        self.label_download_status = tkinter.Label(self.root, font='Arial 15', fg='green')
        self.canvas_download_status.create_window(250, 150, window=self.label_download_status)
        self.btn_stop = tkinter.Button(self.root, font='Arial 15', text='    Stop    ', fg='red',
                                       disabledforeground='red', command=self.stop_download)
        self.canvas_download_status.create_window(250, 250, window=self.btn_stop)

        # Canvas setting for the return button for selecting file type (audio, video)
        self.canvas_return = tkinter.Canvas(self.root, width=50, height=50)
        self.canvas_return.place(y=445, x=0)
        self.btn_return = tkinter.Button(self.root, text='<', font='Arial 15', borderwidth=0, command=self.return_page)
        self.canvas_return.create_window(25, 25, window=self.btn_return)
        self.btn_return.configure(state=tkinter.DISABLED)

    def _link_verify(self):
        """
        Check the link provided
        :return: returns the file type (audio, video) and whether it belongs to a playlist or not
        """
        self.reset_interface()
        self.label_title['text'] = ''
        if self.youtube_link_variable.get() != '' and self.youtube_link_variable.get() != 'Type here a youtube link':
            try:
                try:
                    playlist = Playlist(self.youtube_link_variable.get())
                    title = f'Playlist: {playlist.title}'
                    self.youtube_type = 'playlist'
                except KeyError:
                    youtube = YouTube(self.youtube_link_variable.get())
                    title = f'Video:  {youtube.title}'
                    self.youtube_type = 'video'
            except Exception as erro:
                messagebox.showerror('Error', erro)
                self.canvas_file_type.place_forget()
                if self.select_type != '':
                    if self.select_type == 'audio':
                        self.canvas_audio_download.place_forget()
                    elif self.select_type == 'video':
                        self.canvas_video_download.place_forget()
            else:
                self.label_title['text'] = title
                self.canvas_file_type.place(x=170, y=200)
                self.link = self.youtube_link_variable.get()
        else:
            self.label_title['text'] = ''
            self.canvas_file_type.place_forget()

    def block_interface(self):
        """
        Blocks insertion of links during download
        :return:
        """
        self.entry_youtube_link.configure(state=tkinter.DISABLED)
        self.verify.configure(state=tkinter.DISABLED)
        self.btn_return.configure(state=tkinter.DISABLED)

    def unblock_interface(self):
        """
        Unlocks interface after download finishes
        :return:
        """
        self.entry_youtube_link.configure(state=tkinter.NORMAL)
        self.verify.configure(state=tkinter.ACTIVE)
        self.btn_return.configure(state=tkinter.ACTIVE)

    def reset_interface(self):
        """
        Resets interface after insertion and search for new links
        :return:
        """
        if self.select_type == 'audio':
            self.canvas_audio_download.place_forget()
        elif self.select_type == 'video':
            self.canvas_video_download.place_forget()
        self.btn_return.configure(state=tkinter.DISABLED)

    def return_page(self):
        """
        Return to file type selection menu (audio, video)
        :return:
        """
        self.canvas_file_type.place(x=170, y=200)
        if self.select_type == 'audio':
            self.canvas_audio_download.place_forget()
        elif self.select_type == 'video':
            self.canvas_video_download.place_forget()

        self.btn_return.configure(state=tkinter.DISABLED)

        self.select_type = ''

    def clear_entry(self):
        """
        Clears the initial message indicating where the link should be pasted
        :return:
        """
        self.entry_youtube_link.delete(0, 'end')

    def stop_download(self):
        """
        Restart the application if the user requests
        :return:
        """
        stop_download = messagebox.askokcancel('Cancel Download',
                                               'Do you want to cancel the download, it may make it unusable')
        if stop_download:
            self.btn_stop['text'] = 'Stopping...'
            self.btn_stop.configure(state=tkinter.DISABLED)
            self.restart()

    @staticmethod
    def restart():
        """
        Retrieves the path of the executed program and restarts it
        :return:
        """
        python = sys.executable
        os.execl(python, python, *sys.argv)

    @staticmethod
    def mp4_to_mp3(mp4, mp3):
        """
        Convert mp4 file to mp3
        :param mp4: File to be converted
        :param mp3: New Converted File Name
        :return: Returns a file converted to mp3
        """
        mp4_without_frames = AudioFileClip(mp4)
        mp4_without_frames.write_audiofile(mp3)
        mp4_without_frames.close()

    def _thread_download_audio(self, *args):
        """
        Download playlist audio files and videos
        :param args:
        :return:
        """
        _none = args
        save_path = filedialog.askdirectory()  # Get the path selected by the user to save the file
        if save_path != '':
            self.block_interface()
            self.canvas_audio_download.place_forget()
            self.canvas_download_status.place(x=20, y=140)

            # Check the file type (video, playlist) and download
            if self.youtube_type == 'video':
                self.label_download_status['text'] = 'Downloading Audio, please wait.'
                youtube = YouTube(self.link).streams.get_audio_only().download(save_path)
                try:
                    self.mp4_to_mp3(str(youtube.title()), f'{youtube.title().replace(".Mp4", "")}.mp3')
                    os.remove(youtube.title())
                except Exception as erro:
                    messagebox.showerror(erro)
                    os.remove(youtube.title())
            elif self.youtube_type == 'playlist':
                playlist = Playlist(self.link)
                count = -1
                for url in playlist:
                    count += 1
                    self.label_count_playlist['text'] = f'FILE: {str(count)}/{str(len(playlist))}'
                    self.label_download_status['text'] = 'Downloading Audio Playlist, please wait.'
                    youtube = YouTube(url)
                    self.label_download_name_file['text'] = youtube.title
                    youtube = YouTube(url).streams.get_audio_only().download(save_path)
                    try:
                        self.mp4_to_mp3(str(youtube.title()), f'{youtube.title().replace(".Mp4", "")}.mp3')
                        os.remove(youtube.title())
                    except Exception as erro:
                        messagebox.showerror(erro)
                        os.remove(youtube.title())
            self.canvas_download_status.place_forget()
            messagebox.showinfo('Info', 'Download Finished')
            self.unblock_interface()
            self.canvas_audio_download.place(x=150, y=230)

    def _thread_download_highest_resolution(self, *args):
        """
        Download playlist and video in high quality
        :param args:
        :return:
        """
        _none = args
        save_path = filedialog.askdirectory()  # Get the path selected by the user to save the file
        if save_path != '':
            self.block_interface()
            self.canvas_video_download.place_forget()
            self.canvas_download_status.place(x=20, y=140)

            # Check the file type (video, playlist) and download
            if self.youtube_type == 'video':
                self.label_download_status['text'] = 'Downloading Video, please wait.'
                YouTube(self.link).streams.get_highest_resolution().download(save_path)
            elif self.youtube_type == 'playlist':
                playlist = Playlist(self.link)
                count = -1
                for url in playlist:
                    count += 1
                    self.label_count_playlist['text'] = f'FILE: {str(count)}/{str(len(playlist))}'
                    self.label_download_status['text'] = 'Downloading Video Playlist, please wait.'
                    youtube = YouTube(url)
                    self.label_download_name_file['text'] = youtube.title
                    YouTube(url).streams.get_highest_resolution().download(save_path)
            self.canvas_download_status.place_forget()
            messagebox.showinfo('Info', 'Download Finished')
            self.unblock_interface()
            self.canvas_video_download.place(x=150, y=200)

    def _thread_download_lowest_resolution(self, *args):
        """
        Download playlist and video in low quality
        :param args:
        :return:
        """
        _none = args
        save_path = filedialog.askdirectory()  # Get the path selected by the user to save the file
        if save_path != '':
            self.block_interface()
            self.canvas_video_download.place_forget()
            self.canvas_download_status.place(x=20, y=140)

            # Check the file type (video, playlist) and download
            if self.youtube_type == 'video':
                self.label_download_status['text'] = 'Downloading Video, please wait.'
                YouTube(self.link).streams.get_lowest_resolution().download(save_path)
            elif self.youtube_type == 'playlist':
                playlist = Playlist(self.link)
                count = -1
                for url in playlist:
                    count += 1
                    self.label_count_playlist['text'] = f'FILE: {str(count)}/{str(len(playlist))}'
                    self.label_download_status['text'] = 'Downloading Video Playlist, please wait.'
                    youtube = YouTube(url)
                    self.label_download_name_file['text'] = youtube.title
                    YouTube(url).streams.get_lowest_resolution().download(save_path)
            self.canvas_download_status.place_forget()
            messagebox.showinfo('Info', 'Download Finished')
            self.unblock_interface()
            self.canvas_video_download.place(x=150, y=200)

    def download_audio(self):
        """
        Starts the thread for downloading audio files
        :return:
        """
        start_new_thread(self._thread_download_audio, (None, None))

    def download_highest_resolution(self):
        """
        Start the thread for downloading high quality video files
        :return:
        """
        start_new_thread(self._thread_download_highest_resolution, (None, None))

    def download_lowest_resolution(self):
        """
        Starts the thread for downloading low quality video files
        :return:
        """
        start_new_thread(self._thread_download_lowest_resolution, (None, None))

    def _select_audio(self):
        """
        Enable audio canvas
        :return:
        """
        self.select_type = 'audio'
        self.canvas_file_type.place_forget()
        self.btn_return.configure(state=tkinter.ACTIVE)
        self.canvas_audio_download.place(x=150, y=230)

    def _select_video(self):
        """
        Enable video canvas
        :return:
        """
        self.select_type = 'video'
        self.canvas_file_type.place_forget()
        self.btn_return.configure(state=tkinter.ACTIVE)
        self.canvas_video_download.place(x=150, y=200)

    def start(self):
        """
        Start tkinter mainloop
        :return:
        """
        self.root.mainloop()


if __name__ == '__main__':
    main = Interface()
    main.start()
