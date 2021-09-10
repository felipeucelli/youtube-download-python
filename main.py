# -*- coding: utf-8 -*-

# @autor: Felipe Ucelli
# @github: github.com/felipeucelli

# Built-in
import sys
import os
import re
import tkinter
from tkinter import filedialog
from tkinter import messagebox
from tkinter.ttk import Combobox, Progressbar
from _thread import start_new_thread
from time import sleep

from moviepy.audio.io.AudioFileClip import AudioFileClip
from pytube import YouTube, Playlist, exceptions


class Download:
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title('Youtube Download')
        self.root.resizable(width=False, height=False)
        self.root.geometry('550x500')

        self.select_type = ''
        self.youtube_type = ''
        self.link = ''
        self.stop_download_status = False
        self.loading_link_verify_status = False
        self.youtube_link_variable = tkinter.StringVar()

        self._interface()

    def _interface(self):
        """
        Interface canvas configuration
        :return:
        """
        # Canvas configuration for insertion and search of links
        self.canvas_link = tkinter.Canvas(self.root, width=550, height=150)
        self.canvas_link.pack()
        self.entry_youtube_link = tkinter.Entry(self.root, font='Arial 15', fg='gray',
                                                textvariable=self.youtube_link_variable, width=35)
        self.entry_youtube_link.insert(0, 'Type here a youtube link')
        self.entry_youtube_link.bind('<FocusIn>', lambda event: self.focus_in())
        self.entry_youtube_link.bind('<FocusOut>', lambda event: self.focus_out())
        self.entry_youtube_link.bind('<Return>', lambda event: self._link_verify())
        self.canvas_link.create_window(200, 50, window=self.entry_youtube_link)
        self.btn_link_verify = tkinter.Button(self.root, text='    SEARCH    ', font='Arial 15',
                                              command=self._link_verify)
        self.btn_link_verify.bind('<Return>', lambda event: self._link_verify())
        self.canvas_link.create_window(470, 50, window=self.btn_link_verify)
        self.message_youtube_title = tkinter.Message(self.root, font='Arial 10', width=400)
        self.canvas_link.create_window(280, 100, window=self.message_youtube_title)

        # Animation canvas setup during link search
        self.canvas_load_link = tkinter.Canvas(self.root, width=250, height=130)
        self.label_load_link_verify = tkinter.Label(self.root, font='Arial 30 bold')
        self.canvas_load_link.create_window(125, 65, window=self.label_load_link_verify)

        # Canvas configuration for file type selection (audio, video)
        self.canvas_file_type = tkinter.Canvas(self.root, width=200, height=130)
        self.btn_video = tkinter.Button(self.root, text='     Video     ', font='Arial 15',
                                        command=self._select_video)
        self.btn_video.bind('<Return>', lambda event: self._select_video())
        self.canvas_file_type.create_window(105, 40, window=self.btn_video)
        self.btn_audio = tkinter.Button(self.root, text='     Audio     ', font='Arial 15',
                                        command=self._select_audio)
        self.btn_audio.bind('<Return>', lambda event: self._select_audio())
        self.canvas_file_type.create_window(105, 100, window=self.btn_audio)

        # Canvas setting for selecting audio file download quality
        self.canvas_audio_download = tkinter.Canvas(self.root, width=250, height=130)
        self.label_combo_audio_select = tkinter.Label(self.root, font='Arial 10', text='Select a Quality: ')
        self.canvas_audio_download.create_window(125, 10, window=self.label_combo_audio_select)
        self.combo_quality_audio = Combobox(self.root, font='Arial 15', state='readonly')
        self.canvas_audio_download.create_window(125, 40, window=self.combo_quality_audio)
        self.btn_audio_download = tkinter.Button(self.root, text='Download', font='Arial 15',
                                                 command=self.download_audio)
        self.btn_audio_download.bind('<Return>', lambda event: self.download_audio())
        self.canvas_audio_download.create_window(125, 100, window=self.btn_audio_download)

        # Canvas setting for selecting video file download quality
        self.canvas_video_download = tkinter.Canvas(self.root, width=250, height=130)
        self.label_combo_video_select = tkinter.Label(self.root, font='Arial 10', text='Select a Quality: ')
        self.canvas_video_download.create_window(125, 10, window=self.label_combo_video_select)
        self.combo_quality_video = Combobox(self.root, font='Arial 15', state='readonly')
        self.canvas_video_download.create_window(125, 40, window=self.combo_quality_video)
        self.btn_video_download = tkinter.Button(self.root, text='Download', font='Arial 15',
                                                 command=self.download_video)
        self.btn_video_download.bind('<Return>', lambda event: self.download_video())
        self.canvas_video_download.create_window(125, 100, window=self.btn_video_download)

        # Canvas setting for selecting video playlist file download quality
        self.canvas_video_playlist_download = tkinter.Canvas(self.root, width=250, height=130)
        self.btn_highest_resolution = tkinter.Button(self.root, text='Highest Resolution', font='Arial 15',
                                                     command=lambda: self.download_video_playlist('highest_resolution'))
        self.btn_highest_resolution.bind('<Return>', lambda event: self.download_video_playlist('highest_resolution'))
        self.canvas_video_playlist_download.create_window(125, 40, window=self.btn_highest_resolution)
        self.btn_lowest_resolution = tkinter.Button(self.root, text='Lowest Resolution', font='Arial 15',
                                                    command=lambda: self.download_video_playlist('lowest_resolution'))
        self.btn_lowest_resolution.bind('<Return>', lambda event: self.download_video_playlist('lowest_resolution'))
        self.canvas_video_playlist_download.create_window(125, 100, window=self.btn_lowest_resolution)

        # Canvas setting for selecting audio playlist file download
        self.canvas_audio_playlist_download = tkinter.Canvas(self.root, width=250, height=100)
        self.btn_audio_file = tkinter.Button(self.root, text='    Download    ', font='Arial 15',
                                             command=self.download_audio)
        self.btn_audio_file.bind('<Return>', lambda event: self.download_audio())
        self.canvas_audio_playlist_download.create_window(125, 50, window=self.btn_audio_file)

        # Download Status Canvas Setting
        self.canvas_download_status = tkinter.Canvas(self.root, width=500, height=300)
        self.label_count_playlist = tkinter.Label(self.root, font='Arial 15', fg='green')
        self.canvas_download_status.create_window(250, 50, window=self.label_count_playlist)
        self.label_download_name_file = tkinter.Message(self.root, font='Arial 10', fg='green', width=400)
        self.canvas_download_status.create_window(250, 100, window=self.label_download_name_file)
        self.label_download_status = tkinter.Label(self.root, font='Arial 15', fg='green')
        self.canvas_download_status.create_window(250, 150, window=self.label_download_status)
        self.btn_stop = tkinter.Button(self.root, font='Arial 15', text='    Stop    ', fg='red',
                                       disabledforeground='red', command=self.stop_download)
        self.btn_stop.bind('<Return>', lambda event: self.stop_download())
        self.canvas_download_status.create_window(250, 250, window=self.btn_stop)
        self.label_download_progress_bar = Progressbar(self.canvas_download_status, orient=tkinter.HORIZONTAL,
                                                       mode='determinate', length=400)
        self.canvas_download_status.create_window(250, 200, window=self.label_download_progress_bar)
        self.label_download_progress_bar_count = tkinter.Label(self.root, font='Arial 10', fg='green')
        self.canvas_download_status.create_window(480, 200, window=self.label_download_progress_bar_count)
        self.btn_force_stop = tkinter.Button(self.root, font='Arial 10', text='Force Stop', fg='red',
                                             disabledforeground='red', command=self.force_stop_download)
        self.btn_force_stop.bind('<Return>', lambda event: self.force_stop_download())

        # Canvas setting for the return button for selecting file type (audio, video)
        self.canvas_return = tkinter.Canvas(self.root, width=50, height=50)
        self.canvas_return.place(y=445, x=0)
        self.btn_return = tkinter.Button(self.root, text='<', font='Arial 15', borderwidth=0, command=self.return_page)
        self.btn_return.bind('<Return>', lambda event: self.return_page())
        self.canvas_return.create_window(25, 25, window=self.btn_return)
        self.btn_return.configure(state=tkinter.DISABLED)

    def _loading_link_verify(self, *args):
        """
        Generates an animation while checking the link
        :param args: None
        :return:
        """
        _none = args
        while self._loading_link_verify_status:
            time = 0.20
            self.label_load_link_verify['text'] = '|'
            sleep(time)
            self.label_load_link_verify['text'] = '/'
            sleep(time)
            self.label_load_link_verify['text'] = '-'
            sleep(time)
            self.label_load_link_verify['text'] = '\\'
            sleep(time)
            self.label_load_link_verify['text'] = '|'
            sleep(time)
            self.label_load_link_verify['text'] = '/'
            sleep(time)
            self.label_load_link_verify['text'] = '-'
            sleep(time)
            self.label_load_link_verify['text'] = '\\'
            sleep(time)
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
                    playlist = Playlist(self.youtube_link_variable.get())
                    title = f'PLAYLIST: {playlist.title}'
                    self.youtube_type = 'playlist'
                except KeyError:
                    youtube = YouTube(self.youtube_link_variable.get())
                    stream = youtube.streams
                    quality_video = self.get_video_quality(stream)
                    quality_audio = self.get_audio_quality(stream)
                    self.combo_quality_video['values'] = quality_video
                    self.combo_quality_audio['values'] = quality_audio
                    title = f'VIDEO: {youtube.title}'
                    self.youtube_type = 'video'
            except Exception as erro:
                self._loading_link_verify_status = False
                self.unblock_interface()
                messagebox.showerror('Error', erro)
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
        self.btn_link_verify.configure(state=tkinter.DISABLED)
        self.btn_return.configure(state=tkinter.DISABLED)

    def unblock_interface(self):
        """
        Unlocks interface after download finishes
        :return:
        """
        self.entry_youtube_link.configure(state=tkinter.NORMAL)
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
        self.btn_return.configure(state=tkinter.DISABLED)

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

        self.select_type = ''

    def focus_in(self):
        """
        Clean the placeholder
        :return:
        """
        if self.entry_youtube_link.get() == 'Type here a youtube link':
            self.entry_youtube_link.delete(0, 'end')
            self.entry_youtube_link['fg'] = 'black'

    def focus_out(self):
        """
        Insert placeholder
        :return:
        """
        if self.entry_youtube_link.get() == '':
            self.entry_youtube_link.insert(0, 'Type here a youtube link')
            self.entry_youtube_link['fg'] = 'gray'

    @staticmethod
    def mp4_to_mp3(mp4, mp3):
        """
        Convert mp4 file to mp3
        :param mp4: File to be converted
        :param mp3: New Converted File Name
        :return: Returns a file converted to mp3
        """
        mp4_without_frames = AudioFileClip(mp4)
        mp4_without_frames.write_audiofile(mp3, verbose=False, logger=None)
        mp4_without_frames.close()

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
        self.label_download_progress_bar_count['text'] = f'{percent}%'
        self.label_download_progress_bar['value'] = percent

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
                self.canvas_audio_playlist_download.place(x=150, y=230)

        elif self.select_type == 'video':
            if self.youtube_type == 'video':
                self.canvas_video_download.place(x=150, y=200)
            elif self.youtube_type == 'playlist':
                self.canvas_video_playlist_download.place(x=150, y=200)

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

    def _thread_download_audio(self, *args):
        """
        Download playlist audio files and videos
        :param args: None
        :return:
        """
        _none = args
        save_path = filedialog.askdirectory()  # Get the path selected by the user to save the file
        if save_path != '' and save_path != ():
            self._start_download()
            # Check the file type (video or playlist) and download
            if self.youtube_type == 'video':
                self.label_download_status['text'] = 'Downloading Audio, please wait.'
                self.label_download_progress_bar_count['text'] = '0%'
                self.label_download_progress_bar['value'] = 0
                try:
                    youtube = YouTube(self.link, on_progress_callback=self.progress_callback) \
                        .streams.filter(abr=str(self.combo_quality_audio.get()),
                                        only_audio=True, file_extension='mp4')[0].download(save_path)
                    try:
                        self.label_download_status['text'] = 'Converting Audio, please wait.'
                        self.mp4_to_mp3(str(youtube), f'{youtube.replace(".mp4", ".mp3")}')
                        os.remove(youtube)
                    except Exception as erro:
                        messagebox.showerror('Error', erro)
                        os.remove(youtube)
                        self.restart()
                except Exception as erro:
                    messagebox.showerror('Error', erro)
                    self.restart()
            elif self.youtube_type == 'playlist':
                playlist = Playlist(self.link)
                count = 0
                for url in playlist:
                    self.label_count_playlist['text'] = f'FILE: {str(count)}/{str(len(playlist))}'
                    self.label_download_status['text'] = 'Downloading Audio Playlist, please wait.'
                    self.label_download_progress_bar_count['text'] = '0%'
                    self.label_download_progress_bar['value'] = 0
                    try:
                        youtube = YouTube(url)
                        self.label_download_name_file['text'] = youtube.title
                        youtube = YouTube(url, on_progress_callback=self.progress_callback) \
                            .streams.get_audio_only().download(save_path)
                        try:
                            self.label_download_status['text'] = 'Converting Audio, please wait.'
                            self.mp4_to_mp3(str(youtube), f'{youtube.replace(".mp4", ".mp3")}')
                            os.remove(youtube)
                        except Exception as erro:
                            messagebox.showerror('Error', erro)
                            os.remove(youtube)
                            self.restart()
                    except exceptions.AgeRestrictedError:
                        continue
                    except Exception as erro:
                        messagebox.showerror('Error', erro)
                        self.restart()
                    else:
                        count += 1
                    if self.stop_download_status:
                        break
            self._download_finished()

    def _thread_download_video(self, *args):
        """
        Download video
        :param args: None
        :return:
        """
        _none = args
        save_path = filedialog.askdirectory()  # Get the path selected by the user to save the file
        if save_path != '' and save_path != ():
            self._start_download()

            # Check the file type (video) and download
            if self.youtube_type == 'video':
                self.label_download_status['text'] = 'Downloading Video, please wait.'
                self.label_download_progress_bar_count['text'] = '0%'
                self.label_download_progress_bar['value'] = 0
                try:
                    YouTube(self.link, on_progress_callback=self.progress_callback) \
                        .streams.filter(res=str(re.findall(r'^\d{3}p', self.combo_quality_video.get())[0]),
                                        progressive=True, file_extension='mp4')[0].download(save_path)
                except Exception as erro:
                    messagebox.showerror('Error', erro)
                    self.restart()
            self._download_finished()

    def _thread_download_video_playlist(self, *args):
        """
        Download playlist
        :param args: position 0 receives the chosen quality (highest_resolution or lowest_resolution)
        :return:
        """
        quality = args[0]
        save_path = filedialog.askdirectory()  # Get the path selected by the user to save the file
        if save_path != '' and save_path != ():
            self._start_download()

            # Check the video quality (highest_resolution or lowest_resolution) and download
            if quality == 'lowest_resolution':
                playlist = Playlist(self.link)
                count = 0
                for url in playlist:
                    self.label_count_playlist['text'] = f'FILE: {str(count)}/{str(len(playlist))}'
                    self.label_download_status['text'] = 'Downloading Video From Playlist, please wait.'
                    self.label_download_progress_bar_count['text'] = '0%'
                    self.label_download_progress_bar['value'] = 0
                    try:
                        youtube = YouTube(url, on_progress_callback=self.progress_callback)
                        self.label_download_name_file['text'] = youtube.title
                        youtube.streams.get_lowest_resolution().download(save_path)
                    except exceptions.AgeRestrictedError:
                        continue
                    except Exception as erro:
                        messagebox.showerror('Erro', erro)
                    else:
                        count += 1
                    if self.stop_download_status:
                        break
            elif quality == 'highest_resolution':
                playlist = Playlist(self.link)
                count = 0
                for url in playlist:
                    self.label_count_playlist['text'] = f'FILE: {str(count)}/{str(len(playlist))}'
                    self.label_download_status['text'] = 'Downloading Video From Playlist, please wait.'
                    self.label_download_progress_bar_count['text'] = '0%'
                    self.label_download_progress_bar['value'] = 0
                    try:
                        youtube = YouTube(url, on_progress_callback=self.progress_callback)
                        self.label_download_name_file['text'] = youtube.title
                        youtube.streams.get_highest_resolution().download(save_path)
                    except exceptions.AgeRestrictedError:
                        continue
                    except Exception as erro:
                        messagebox.showerror('Error', erro)
                    else:
                        count += 1
                    if self.stop_download_status:
                        break
            self._download_finished()

    def download_audio(self):
        """
        Starts the thread for downloading audio files
        :return:
        """
        if self.youtube_type == 'video':
            if self.combo_quality_audio.get() == '':
                messagebox.showerror('Error', 'Please Select a Quality')
            else:
                start_new_thread(self._thread_download_audio, (None, None))
        elif self.youtube_type == 'playlist':
            start_new_thread(self._thread_download_audio, (None, None))

    def download_video(self):
        """
        Starts the thread for downloading low quality video files
        :return:
        """
        if self.combo_quality_video.get() == '':
            messagebox.showerror('Error', 'Please Select a Quality')
        else:
            start_new_thread(self._thread_download_video, (None, None))

    def download_video_playlist(self, quality):
        """
        Start the thread for downloading high quality video files
        :return:
        """
        start_new_thread(self._thread_download_video_playlist, (quality, None))

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
            self.canvas_audio_playlist_download.place(x=150, y=230)

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
            self.canvas_video_playlist_download.place(x=150, y=200)

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
            self.btn_force_stop.place(x=230, y=430)

    def start(self):
        """
        Start tkinter mainloop
        :return:
        """
        self.root.mainloop()


if __name__ == '__main__':
    main = Download()
    main.start()
