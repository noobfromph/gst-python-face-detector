import gi
from threading import Thread
from gi.repository import GLib
import subprocess


class AudioHelper:
    greet_queue = []
    is_busy = False
    timeout = 60

    def __init__(self, conf):
        self.conf = conf
        GLib.timeout_add_seconds(0.5, self._exec_greetings)

    def greet(self, name):
        self.add_item(name)

    def _play_audio(self, file):
        subprocess.call(["play", file], subprocess.DEVNULL,
                        stderr=subprocess.STDOUT)
        subprocess.call(["play", file], subprocess.DEVNULL,
                        stderr=subprocess.STDOUT)
        subprocess.call(["play", file], subprocess.DEVNULL,
                        stderr=subprocess.STDOUT)

    def _exec_greetings(self):
        if not self.is_busy:
            self.is_busy = True
            if len(self.greet_queue) > 0:
                name, _ = self.greet_queue[0]
                pd = self.get_item(name)

                if pd is None:
                    self._play_audio()
                else:
                    self._play_audio(pd["audio"])

                del self.greet_queue[0]

            self.is_busy = False
            GLib.timeout_add_seconds(1, self._exec_greetings)

    def get_item(self, name):
        for item in self.conf:
            if item["name"] == name:
                return item

        return None

    def exist(self, name):
        for i in range(len(self.greet_queue)):
            if self.greet_queue[i][0] == name:
                return True

        return False

    def add_item(self, name):
        if not self.exist(name):
            data = (name, False)  # name, greeted
            self.greet_queue.append(data)

    def remove_item(self, name):
        for i in range(len(self.greet_queue)):
            if self.greet_queue[i][0] == name:
                del self.greet_queue[i]
                break
