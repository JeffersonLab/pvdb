import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import traceback

import rcdb
from rcdb.provider import RCDBProvider
from rcdb import DefaultConditions
from rcdb.model import ConditionType, Condition

from parity_rcdb import ParityConditions

class WacTool(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="WAC DB TOOL")

        self.set_size_request(350,450)
        self.timeout_id = None
        self.set_border_width(10)

        self.run_flag_selected = None
        self.run_type_selected = ""
        self.myDBTool = None

        # First, run number 
        fixed = Gtk.Fixed()
        lbl = Gtk.Label("Run Number:")
        fixed.put(lbl, 25, 55)
        self.entry1 = Gtk.Entry()
        fixed.put(self.entry1, 125, 50)
        button1 = Gtk.Button("Connect")
        button1.connect("clicked", self.on_connect, self.entry1)
        fixed.put(button1, 300, 50)

        lbl2 = Gtk.Label("Run Type:")
        fixed.put(lbl2, 25, 100)

        self.text2 = Gtk.Entry()
        fixed.put(self.text2, 125, 100)

        type_store = Gtk.ListStore(str)
        run_types = ["Production", "Calibration", "Pedestal", "Test", "Junk", "Cosmics", "Other"]
        for run_type in run_types:
            type_store.append([run_type])

        treeView = Gtk.TreeView()
        treeView.set_model(type_store)
        rendererText = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Select New Run Types", rendererText, text=0)
        treeView.append_column(column)

        fixed.put(treeView, 127, 140)

#        self.selection.set_selectioin_function(self.select_function)
        self.selection = treeView.get_selection()
        self.selection.connect("changed", self.on_changed)

        #### RUN FLAG ###
        lbl3 = Gtk.Label("Run Flag:")
        fixed.put(lbl3, 25, 370)

        #hidden for the inital value
        self.rbutton0 = Gtk.RadioButton.new_with_label_from_widget(None, "None")
        self.rbutton0.connect("toggled", self.on_rbutton_toggled, "None")

        self.rbutton1 = Gtk.RadioButton.new_from_widget(self.rbutton0)
        self.rbutton1.set_label("Good")
        self.rbutton1.connect("toggled", self.on_rbutton_toggled, "Good")

        self.rbutton2 = Gtk.RadioButton.new_from_widget(self.rbutton0)
        self.rbutton2.set_label("NeedCut")
        self.rbutton2.connect("toggled", self.on_rbutton_toggled, "NeedCut")

        self.rbutton3 = Gtk.RadioButton.new_from_widget(self.rbutton0)
        self.rbutton3.set_label("Bad")
        self.rbutton3.connect("toggled", self.on_rbutton_toggled, "Bad")

        self.rbutton4 = Gtk.RadioButton.new_from_widget(self.rbutton0)
        self.rbutton4.set_label("Suspicous")
        self.rbutton4.connect("toggled", self.on_rbutton_toggled, "Suspicious")

        fixed.put(self.rbutton1, 110, 370)
        fixed.put(self.rbutton2, 180, 370)
        fixed.put(self.rbutton3, 270, 370)
        fixed.put(self.rbutton4, 330, 370)
        # Save and exit
        ok_button = Gtk.Button("SAVE")
        ok_button.connect("clicked", self.on_ok_clicked, self.entry1)
        ok_button.set_size_request(160, 10)

        cancel_button = Gtk.Button("CANCEL")
        cancel_button.connect("clicked", self.on_cancel_clicked)
        cancel_button.set_size_request(160, 10)

        fixed.put(ok_button, 20, 420)
        fixed.put(cancel_button, 190, 420)

        self.add(fixed)

    def on_ok_clicked(self, widget, value):
        runnum = value.get_text()
        if self.myDBTool is not None:
            if self.run_type_selected is not None:
                print "New run type:", self.run_type_selected
                self.myDBTool.save_new_run_type(runnum, self.run_type_selected)
            if self.run_flag_selected is not None:
                print "New run flag:", self.run_flag_selected
                self.myDBTool.save_new_run_flag(runnum, self.run_flag_selected)
        else:
            print "DB connection failed?"

    def on_cancel_clicked(self, widget):
        Gtk.main_quit()

    def on_rbutton_toggled(self, button, name):
        if button.get_active():
            state = "on"
        else:
            state = "off"
        self.run_flag_selected = name

    def on_connect(self, widget, value):
        con_str = "mysql://apcoda@cdaqdb1.jlab.org:3306/a-rcdb"
        self.myDBTool = DBTool(con_str)

        if not self.myDBTool.is_connected:
            print ("ERROR: Failed to connect to DB")
        else:
            read_ok = self.myDBTool.read_conditions(value.get_text())
            if read_ok:
                if self.myDBTool.run_type is not None:
                    self.run_type_selected = self.myDBTool.run_type
                    self.text2.set_text(self.run_type_selected)
                if self.myDBTool.run_flag is not None:
                    self.run_flag_selected = self.myDBTool.run_flag
                    if self.run_flag_selected == "Good":
                        self.rbutton1.set_active(True)
                    if self.run_flag_selected == "NeedCut":
                        self.rbutton2.set_active(True)
                    elif self.run_flag_selected == "Bad":
                        self.rbutton3.set_active(True)
                    elif self.run_flag_selected == "Suspicious":
                        self.rbutton4.set_active(True)
                    else:
                        print ("Warning: Invalid run flag from DB: %s" % self.run_flag_selected)

    def on_changed(self, selection):
        (model, iter) = selection.get_selected()
        if iter is not None:
            print "Run type:",  model[iter][0], "selected"
        else:
            print "MOOOOOOOOOOOOOO"
        self.run_type_selected = model[iter][0]

class DBTool(object):
    def __init__(self, con_str=None):
        self.connection_string = ""
        self.run_type = None
        self.wac_comment = None
        self.run_flag = None
        self.is_connected = None
        self.run_number = None
        self.run = None

        if con_str and self.is_connected is not True:
            print "connect to DB"
            self.db = rcdb.RCDBProvider(con_str)            
            self.is_connected = True
            
    def read_conditions(self, run_num):
        read_ok = False

        self.run_number = run_num
        self.run = self.db.get_run(run_num)
        if not self.run:
            print ("ERROR: Run %s is not found in DB" % run_num)
            return False
        else:        
            try:
                self.run_type = self.db.get_condition(self.run, "run_type").value
                read_ok = True
            except Exception as ex:
                print ("Warning: no initial run_type condition available in DB")
            try:
                self.run_flag = self.db.get_condition(self.run, "run_flag").value
                read_ok = True
            except Exception as ex:
                print ("Warning: no initial run_flag condition available in DB")
            return read_ok

    def save_new_run_type(self, runnum, new_run_type):
        if not self.is_connected:
            print ("ERROR: No DB connection?????")
            return
        if runnum != self.run_number:
            print ("Run Number mismatch! Check run number again!")
        else:
            self.db.add_condition(self.run, DefaultConditions.RUN_TYPE, new_run_type, True)
            print ("Saved to DB")

    def save_new_run_flag(self, runnum, new_run_flag):
        if not self.is_connected:
            print ("ERROR: No DB connection?????")
            return
        if runnum != self.run_number:
            print ("Run Number mismatch! Check run number again!")
        else:
            self.db.add_condition(self.run, ParityConditions.RUN_FLAG, new_run_flag, True)

win = WacTool()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
