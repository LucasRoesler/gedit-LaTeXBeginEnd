# -*- coding: utf-8 -*-

# This file is part of the LaTeX Begin End plugin
#
# Copyright (C) 2011 Lucas David-Roesler
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public Licence as published by
# the Free Software Foundation; either version 2 of the Licence, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public Licence for more details.
#
# You should have received a copy of the GNU General Public Licence along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA

from gi.repository import GObject, Gtk, Gdk, Gedit
import re


menu_str ="""
<ui>
  <menubar name="MenuBar">
    <menu name="ToolsMenu" action="Tools">
      <placeholder name="ToolsOps_4">
        <placeholder name="LatexBeginEnd">
           <menuitem name="CompleteBeginEnd" action="complete_begin_end"/>        
        </placeholder>
      </placeholder>
    </menu>
  </menubar>
</ui>
"""

regex = re.compile("begin\{[a-zA-Z0-9\*]+\}$")

class LatexBeginEnd(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "LatexBeginEnd"
    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)
        
    def do_activate(self):
        self.insert_menu()

    def do_deactivate(self):
        manager = self.window.get_ui_manager()
        manager.remove_action_group(self._action_group)
        self._action_group = None
        manager.ensure_update()
    
    def do_update_state(self):
        self._action_group.set_sensitive(
            self.window.get_active_document() != None)

    def insert_menu(self):
        # Get the Gtk.UIManager
        manager = self.window.get_ui_manager()

        #Create a new action group
        self._action_group = Gtk.ActionGroup(name="LatexBeginEnd")
        self._action_group.add_actions([("complete_begin_end",None,
                                         _("Complete BeginEnd block"),"Escape",
                                         _("Complete a LaTeX Begin/End block"),self.complete_begin_end)])
        manager.insert_action_group(self._action_group,-1)

        self._ui_id=manager.add_ui_from_string(menu_str)


    def get_current_line(self):
        view = self.window.get_active_view()
        doc  = self.window.get_active_document()
        doc.begin_user_action()
        itorig=doc.get_iter_at_mark(doc.get_insert())
        offset=itorig.get_line_offset()
        # GTK_MOVEMENT_PARAGRAPH_ENDS=6
        if offset:
                view.do_move_cursor(6,-1,0)
        itstart = doc.get_iter_at_mark(doc.get_insert())
        itend = doc.get_iter_at_mark(doc.get_insert())
        itend.forward_line();
        line = doc.get_slice(itstart, itend, True)
        if offset:
            view.do_move_cursor(0,offset,0)
        doc.end_user_action()

        return line

    def insert_end(self,begin_str):
        end_enviroment = "\n\n\end" + begin_str[5:]

        view = self.window.get_active_view()
        doc  = self.window.get_active_document()
        view = self.window.get_active_view()
        doc.begin_user_action()

        # make sure we are at the end of the line
        view.do_move_cursor(4,1,0)
        doc.insert_at_cursor(end_enviroment)

        # move the cursor between the begin and end statements
        view.do_move_cursor(3,-1,0)

        doc.end_user_action()
        False
        
    def complete_begin_end(self,action):
        line = self.get_current_line().strip()
        results =  regex.findall(line)
        if len(results):
            self.insert_end(results[0])
        else:
            False

