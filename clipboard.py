#!/usr/bin/env python

import time
import os
from Tkinter import Tk

class Clipboard(object):
    def __init__(self):
        self._widget = Tk()
        self._widget.withdraw()

    def get(self):
        try:
            return self._widget.clipboard_get()
        except TclError:
            return None

    def post(self, text):
        self._widget.clipboard_clear()
        self._widget.clipboard_append(text)

    def destroy(self):
        self._widget.destroy()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.destroy()

class DropboxBackend(object):
    def __init__(self, sync_path):
        self.sync_path = sync_path
        sync_folder = os.path.dirname(sync_path)
        if not os.path.isdir(sync_folder):
            os.makedirs(sync_folder)

    def get(self):
        try:
            with open(self.sync_path) as f:
                return f.read()
        except IOError:
            return None

    def post(self, text):
        with open(self.sync_path, mode='w') as f:
            f.write(text)

    def delete(self):
        os.remove(self.sync_path)


def watch(clipboard, backend, sleep_seconds=1):
    prev = None
    current = None

    while True:
        current = clipboard.get()
        dirty = False
        if current != prev:
            backend.post(current)
            prev = current
            dirty = True
        else:
            sync_data = backend.get()
            if sync_data != current:
                clipboard.post(sync_data)
                backend.delete()
                dirty = True
        if not dirty:
            time.sleep(sleep_seconds)

def main():
    sync_path = '/Users/Michael/Dropbox/automation/clipboard_sync.txt'
    backend = DropboxBackend(sync_path)

    with Clipboard() as c:
        watch(c, backend)

if __name__ == '__main__':
    main()