#!/usr/bin/python3

from helper.audio import AudioHelper
from gi.repository import Gst, GObject, GstBase, GstVideo, GLib
from utils.utils import gst_buffer_with_pad_to_ndarray
from threading import Thread
import numpy as np
import face_recognition
import time
import subprocess
import gi
import json
import os
import cv2
gi.require_version('Gst', '1.0')
gi.require_version('GstBase', '1.0')
gi.require_version('GstVideo', '1.0')

Gst.init(None)
FIXED_CAPS = Gst.Caps.from_string(
    'video/x-raw,format=BGR,width=[1,2147483647],height=[1,2147483647]')


class FaceDetectorPyPy(GstBase.BaseTransform):
    __gstmetadata__ = ('Face Detector Python', 'Transform',
                       'example element', 'payam')
    __gsttemplates__ = (
        Gst.PadTemplate.new("src", Gst.PadDirection.SRC,
                            Gst.PadPresence.ALWAYS, FIXED_CAPS),
        Gst.PadTemplate.new("sink", Gst.PadDirection.SINK,
                            Gst.PadPresence.ALWAYS, FIXED_CAPS)
    )
    _sinkpadtemplate = __gsttemplates__[1]
    __gproperties__ = {
        "scan": (str, "Scan", "Whether to register faces", None, GObject.ParamFlags.READWRITE)
    }
    caps = None
    scan_faces = False

    greeting_timeout = 69

    def __init__(self):
        # bug workaround
        self._segmentation_fault_workaround_sink = Gst.Pad.new_from_template(Gst.PadTemplate.new(
            "sink", Gst.PadDirection.SINK, Gst.PadPresence.ALWAYS, Gst.Caps.new_any()), "sink")
        self._segmentation_fault_workaround_sink.set_chain_function_full(
            self.chain)
        # end: # bug workaround

        self.faceCascade = cv2.CascadeClassifier(
            "data/haarcascade_frontalface_default.xml")

        # Initialize some variables
        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.process_this_frame = True

        self.known_face_encodings = []
        self.known_face_names = []

        self.load_faces()

    def load_faces(self):
        with open("data/faces.json", "r") as jf:
            jdata = json.loads(jf.read())

        self.audio_helper = AudioHelper(jdata["items"])

        for item in jdata["items"]:
            face_image = face_recognition.load_image_file(
                item["im_sample_path"])
            face_encoding = face_recognition.face_encodings(face_image)[0]
            self.known_face_encodings.append(face_encoding)
            self.known_face_names.append(item["name"])

    def do_set_caps(self, incaps, _):
        self.caps = incaps
        return True

    def do_get_property(self, prop: GObject.GParamSpec):
        if prop.name == 'scan':
            return self.scan_faces
        else:
            raise AttributeError("Invalid attribute")

    def do_set_property(self, prop: GObject.GParamSpec, value):
        if prop.name == 'scan':
            self.scan_faces = value
        else:
            raise AttributeError("Invalid attribute")

    is_greeting = False
    greeting_in_progress = False

    def do_transform_ip(self, buf):
        A = gst_buffer_with_pad_to_ndarray(buf, self.caps)
        small_frame = cv2.resize(A.copy(), (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]
        if self.process_this_frame:
            self.face_locations = face_recognition.face_locations(
                rgb_small_frame)
            self.face_encodings = face_recognition.face_encodings(
                rgb_small_frame, self.face_locations)

            self.face_names = []
            for face_encoding in self.face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(
                    self.known_face_encodings, face_encoding)
                name = "Unknown"

                # use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(
                    self.known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]

                self.face_names.append(name)

        self.process_this_frame = not self.process_this_frame

        # Display the results
        for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(A, (left, top), (right, bottom), (0, 255, 0), 2)

            # Draw a label with a name below the face
            cv2.rectangle(A, (left, bottom - 35),
                          (right, bottom), (0, 255, 0), 2)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(A, name, (left + 6, bottom - 6),
                        font, 1.0, (255, 255, 255), 1)

            self.audio_helper.greet(name)

        return Gst.FlowReturn.OK


GObject.type_register(FaceDetectorPyPy)
__gstelementfactory__ = ("face_detector_py", Gst.Rank.NONE, FaceDetectorPyPy)
