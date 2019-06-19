import os
import subprocess

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

class EntryWindow(Gtk.Window):

    def __init__(self):    
        Gtk.Window.__init__(self, title="WAC Comment")

        self.set_size_request(600,100)
        self.timeout_id = None

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(box)

        # run number part
        hbox = Gtk.HBox()
        lbl = Gtk.Label("Run Number:")
        hbox.pack_start(lbl, expand=True, fill = False, padding=0)
        text = Gtk.Entry()
        hbox.pack_start(text, expand=True, fill = True, padding=10)
        button1 = Gtk.Button("OK")
        button1.connect("clicked", self.on_button1_clicked, text)
        hbox.add(button1)

        # comment part
        vbox = Gtk.HBox()
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        scrolledwindow.set_size_request(200,100)

        text1 = Gtk.TextView()
        self.textbuffer = text1.get_buffer()
        self.textbuffer.set_text("Type Run Number and hit OK, Add your comment")

        scrolledwindow.add(text1)

        vbox.pack_start(scrolledwindow, True, True, 1)

        bbox = Gtk.HBox()
        ok_button = Gtk.Button("SAVE AND EXIT")
        ok_button.connect("clicked", self.on_ok_clicked, text)

        cancel_button = Gtk.Button("Cancel")
        cancel_button.connect("clicked", self.on_cancel_clicked)

        bbox.add(ok_button)
        bbox.add(cancel_button)

        box.add(hbox)        
        box.add(vbox)
        box.add(bbox)

    def on_button1_clicked(self, widget, value):
        run_num = value.get_text()
        comment = self.read_db_comment(run_num)
        self.textbuffer.set_text(comment)

    def on_ok_clicked(self, widget, value):
        run_num = value.get_text()
        buf = self.textbuffer
        comment = buf.get_text(buf.get_start_iter(),
                             buf.get_end_iter(),
                             True)
        self.edit_db_comment(run_num, comment)

    def on_cancel_clicked(self, widget):
        Gtk.main_quit()

    def read_db_comment(self, run):
        cmds = ["rcnd", run, "wac_comment"]
        output = subprocess.Popen(cmds, stdout=subprocess.PIPE).stdout.read()
        print output
        return output.strip()

    def edit_db_comment(self, run, comment):
        comment = comment.strip()
        cmds = ["rcnd", "--write", comment, "--replace", run, "wac_comment"]
        subprocess.call(cmds)
        # done, exit
        Gtk.main_quit()

#win = Gtk.Window(title="TEST GUI")
win = EntryWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
