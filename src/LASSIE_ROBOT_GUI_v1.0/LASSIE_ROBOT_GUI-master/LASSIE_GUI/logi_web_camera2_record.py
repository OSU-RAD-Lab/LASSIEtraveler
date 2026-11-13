#!/usr/bin/env python
# -*- coding: utf-8 -*-
# VideoRecorder.py

from __future__ import print_function, division
import numpy as np
import sys
import cv2
# import pyaudio
import wave
import threading
import time
import subprocess
import os
# import ffmpeg

REC_FOLDER = "experiment_video/camera_2/"
WIDTH = 1280
HEIGHT = 720
WIDTH_2K = 2560
HEIGHT_2K = 1440

class Recorder_2():
    def __init__(self, filename, running_scenario, scale_size=1):
        self.filename = filename
        REC_FOLDER = "experiment_video/" + running_scenario + "/camera_2/"
        if not os.path.exists(os.path.dirname(REC_FOLDER + filename)):
            os.makedirs(os.path.dirname(REC_FOLDER + filename))
        self.video_thread = self.VideoRecorder(self, REC_FOLDER + filename, scale_size)
        

    def startRecording(self):
        self.video_thread.start()


    def stopRecording(self):
        self.video_thread.stop()


    def saveRecording(self):

        self.video_thread.showFramesResume()


    class VideoRecorder():
        "Video class based on openCV"

        def __init__(self, recorder, name, scale_size, fourcc="MJPG", frameSize=(1920, 1080), camindex=0, fps=30):
            # self.openCvVidCapIds = []
            # for i in range(10):
            #     try:
            #         cap = cv2.VideoCapture(i)
            #         if cap is not None and cap.isOpened():
            #             self.openCvVidCapIds.append(i)
            #             print('detect camera', i)
            #         # end if
            #     except:
            #         pass
            # print('choose the first as camera2:', np.max(self.openCvVidCapIds))
            self.recorder = recorder
            self.open = True
            self.duration = 0
            self.device_index = camindex
            self.fps = fps                          # fps should be the minimum constant rate at which the camera can
            self.fourcc = fourcc                    # capture images (with no decrease in speed over time; testing is required)
            self.video_filename = name + ".avi"     # video formats and sizes also depend and vary according to the camera used
            self.video_cap = cv2.VideoCapture('/dev/video8')
            self.frame_size = frameSize
            self.scale = scale_size

            self.video_cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
            self.video_cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH*self.scale)
            self.video_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT*self.scale)
            self.video_writer = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
            self.video_out = cv2.VideoWriter(self.video_filename, self.video_writer, self.fps, self.frame_size)
            self.frame_counts = 1
            self.start_time = time.time()


        def record(self):
            width = int(self.video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = self.video_cap.get(cv2.CAP_PROP_FPS)

            # print(width, height, fps)
            "Video starts being recorded"
            counter = 1
            while self.open:
                ret, video_frame = self.video_cap.read()
                if ret:
                    # cv2.imshow('frame', video_frame)

                    # scale the frame
                    dim = tuple([int(1 * x) for x in self.frame_size])
                    frame_resized = cv2.resize(video_frame, dim)

                    # self.video_out.write(video_frame)
                    self.video_out.write(frame_resized)
                    self.frame_counts += 1
                    counter += 1
                    self.duration += 1/self.fps
                    cv2.waitKey(1)
                else:
                    break

            #Release Video
            self.video_out.release()
            self.video_cap.release()
            cv2.destroyAllWindows()
            self.video_out = None

        def stop(self):
            "Finishes the video recording therefore the thread too"
            self.open=False

        def start(self):
            "Launches the video recording function using a thread"
            self.thread = threading.Thread(target=self.record)
            self.thread.start()

        def showFramesResume(self):
            #Only stop of video has all frames
            frame_counts = self.frame_counts
            elapsed_time = time.time() - self.start_time
            recorded_fps = self.frame_counts / elapsed_time
            # print("total frames " + str(frame_counts))
            # print("elapsed time " + str(elapsed_time))
            # print("recorded fps " + str(recorded_fps))



if __name__ == '__main__':
    recorder = Recorder_2("test2", "MiniRhex")
    recorder.startRecording()
    time.sleep(5)
    recorder.stopRecording()
    recorder.saveRecording()
