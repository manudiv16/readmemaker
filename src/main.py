#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of readmemaker
#
# Copyright (c) 2020 Lorenzo Carbonell Cerezo <a.k.a. atareao>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import gi
try:
    gi.require_version('Gtk', '3.0')
    gi.require_version('Gio', '2.0')
except Exception as e:
    print(e)
    exit(-1)
from gi.repository import Gtk
from gi.repository import Gio
import re
import os
from bs4 import BeautifulSoup
from config import _
from config import TEMPLATE
from basedialog import BaseDialog
from box_general import BoxGeneral
from box_text import BoxText
from box_contributors import BoxContributors
from contributor import Contributor


def generate_button(icon, tooltip_text, callback):
    button = Gtk.Button()
    button.set_margin_start(10)
    button.set_margin_end(10)
    button.set_margin_top(10)
    button.set_margin_bottom(10)
    button.set_tooltip_text(tooltip_text)
    button.set_image(Gtk.Image.new_from_gicon(Gio.ThemedIcon(
        name=icon), Gtk.IconSize.BUTTON))
    button.connect('clicked', callback)
    return button


class ReadmeMaker(BaseDialog):

    """Docstring for AddContextDialog. """

    def __init__(self):
        """TODO: to be defined. """
        BaseDialog.__init__(self, _('Readme Maker. Create README'), None,
                            ok_button=True, cancel_button=True)

    def init_ui(self):
        BaseDialog.init_ui(self)

        notebook = Gtk.Notebook.new()
        self.grid.attach(notebook, 0, 0, 1, 1)

        self.boxGeneral = BoxGeneral()
        notebook.append_page(self.boxGeneral,
                             Gtk.Label.new(_('General')))

        self.boxDescription = BoxText(_('Description:'), True)
        notebook.append_page(self.boxDescription,
                             Gtk.Label.new(_('Description')))

        self.boxDependencies = BoxText(_('Prerequisites:'), True)
        notebook.append_page(self.boxDependencies,
                             Gtk.Label.new(_('Prerequisites')))

        self.boxInstalling = BoxText(_('Installing:'), True)
        notebook.append_page(self.boxInstalling,
                             Gtk.Label.new(_('Installing')))

        self.boxUsing = BoxText(_('Using:'), True)
        notebook.append_page(self.boxUsing,
                             Gtk.Label.new(_('Using')))

        self.boxContributing = BoxText(_('Contibuting:'), True)
        notebook.append_page(self.boxContributing,
                             Gtk.Label.new(_('Contributing')))

        self.boxContributors = BoxContributors(_('Contributors:'), True)
        notebook.append_page(self.boxContributors,
                             Gtk.Label.new(_('Contributors')))
        self.init_headbar()

    def init_headbar(self):
        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.set_title(self.get_title())
        self.set_titlebar(hb)

        self.popover = self.create_popover()
        button4 = Gtk.MenuButton()
        button4.set_size_request(40, 40)
        button4.set_tooltip_text(_('Options'))
        button4.set_popover(self.popover)
        button4.set_image(Gtk.Image.new_from_gicon(Gio.ThemedIcon(
            name='pan-down-symbolic'), Gtk.IconSize.BUTTON))
        hb.pack_end(button4)

    def create_popover(self):
        popover = Gtk.Popover()

        grid = Gtk.Grid.new()
        grid.set_margin_start(10)
        grid.set_margin_end(10)
        grid.set_margin_top(10)
        grid.set_margin_bottom(10)
        popover.add(grid)

        label = Gtk.Label.new(_('New Readme'))
        label.set_halign(Gtk.Align.START)
        grid.attach(label, 0, 0, 1, 1)

        button_open = generate_button('gtk-new', _('New Readme'),
                                      self.new_readme)
        grid.attach(button_open, 1, 0, 1, 1)

        grid.attach(Gtk.Separator(), 0, 1, 2, 1)

        label = Gtk.Label.new(_('Open Readme'))
        label.set_halign(Gtk.Align.START)
        grid.attach(label, 0, 1, 1, 1)

        button_open = generate_button('gtk-open', _('Open Readme'),
                                      self.open_readme)
        grid.attach(button_open, 1, 1, 1, 1)

        label = Gtk.Label.new(_('Save Readme'))
        label.set_halign(Gtk.Align.START)
        grid.attach(label, 0, 2, 1, 1)

        button_save = generate_button('gtk-save', _('Save Readme'),
                                      self.save_readme)
        grid.attach(button_save, 1, 2, 1, 1)

        grid.attach(Gtk.Separator(), 0, 3, 2, 1)

        label = Gtk.Label.new(_('Exit'))
        label.set_halign(Gtk.Align.START)
        grid.attach(label, 0, 4, 1, 1)

        button_exit = generate_button('gtk-quit', _('Exit'),
                                      self.exit_dialog)
        grid.attach(button_exit, 1, 4, 1, 1)

        popover.show_all()
        popover.hide()
        return popover

    def read_file(self, filename):
        # self.boxGeneral
        description = self.read_section('description', filename)
        self.boxDescription.set_content(description)
        prerequisites = self.read_section('prerequisites', filename)
        self.boxDependencies.set_content(prerequisites)
        installing = self.read_section('installing', filename)
        self.boxInstalling.set_content(installing)
        using = self.read_section('using', filename)
        self.boxUsing.set_content(using)
        contributing = self.read_section('contributing', filename)
        self.boxContributing.set_content(contributing)
        intro_contributors = self.read_section('contributors', filename)
        self.boxContributors.set_content(intro_contributors)
        contributors = self.read_section('table-contributors', filename)
        soup = BeautifulSoup(contributors, 'html.parser')
        for table in soup.findAll('table'):
            if table['id'] == 'contributors':
                columns = table.findAll('td')
                rows = table.findAll('tr')
                ncolumns = len(columns)
                nrows = len(rows)
                if ncolumns > 0 and nrows > 0 and ncolumns % nrows ==0:
                    ncontributors = int(ncolumns/nrows)
                pcontributors = {}
                for row in rows:
                    columns = row.findAll('td')
                    for column in columns:
                        if column['id'] and column['id'] not in pcontributors:
                            pcontributors[column['id']] = Contributor(
                                column['id'])
                        if row['id'] == 'info_avatar':
                            pcontributors[column['id']].set_url(
                                column.a['href'])
                            pcontributors[column['id']].set_avatar_url(
                                column.a.img['src'])
                        elif row['id'] == 'info_name':
                            pcontributors[column['id']].set_name(
                                column.a.get_text().strip())
                        elif row['id'] == 'info_commit':
                            pcontributors[column['id']].set_role(
                                column.a.span.get_text())
                self.boxContributors.set_contributors(pcontributors.values())
                break

    def new_readme(self, widget):
        """TODO: Docstring for new_readme.
        :returns: TODO

        """
        self.read_file(TEMPLATE)
        self.popover.hide()

    def open_readme(self, widget):
        dialog = Gtk.FileChooserDialog(_('Open File'), self,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL,
                                        Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OK,
                                        Gtk.ResponseType.ACCEPT))
        filter_md = Gtk.FileFilter()
        filter_md.set_name(_('Markdown files'))
        filter_md.add_mime_type('text/plain')
        dialog.add_filter(filter_md)
        if dialog.run() == Gtk.ResponseType.ACCEPT:
            self.read_file(dialog.get_filename())
        dialog.destroy()
        self.popover.hide()

    def save_readme(self, widget):
        dialog = Gtk.FileChooserDialog(_('Save File'), self,
                                       Gtk.FileChooserAction.SAVE,
                                       (Gtk.STOCK_CANCEL,
                                        Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OK,
                                        Gtk.ResponseType.ACCEPT))
        filter_md = Gtk.FileFilter()
        filter_md.set_name(_('Markdown files'))
        filter_md.add_mime_type('text/plain')
        dialog.add_filter(filter_md)
        if dialog.run() == Gtk.ResponseType.ACCEPT:
            filename = dialog.get_filename()
            if os.path.exists(filename):
                msg = _('The file exists, overwrite?')
                msg_dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
                                               Gtk.ButtonsType.OK_CANCEL,
                                               msg)
                if msg_dialog.run() == Gtk.ResponseType.OK:
                    self.save_filename(filename)
                msg_dialog.destroy()
            else:
                self.save_filename(filename)
        dialog.destroy()
        self.popover.hide()

    def save_filename(self, filename):
        print(filename)

    def exit_dialog(self, widtgt):
        self.popover.hide()
        exit(0)


    def read_section(self, section_name, filename):
        """Read a section

        :section: section name
        :returns: the section readed

        """
        section = ''
        is_section = False
        pattern_start = r'^<!--\s*start\s+{}\s*-->'.format(section_name)
        pattern_end = r'<!--\s*end\s+{}\s*-->'.format(section_name)
        if os.path.exists(filename):
            with open(filename, 'r') as fr:
                for line in fr.readlines():
                    if re.match(pattern_end, line,
                            flags=re.IGNORECASE):
                        break
                    if is_section:
                        section += line
                    if re.match(pattern_start, line,
                            flags=re.IGNORECASE):
                        is_section = True
        return section


def main():
    """TODO: Docstring for main.
    :returns: TODO

    """
    readmeMaker = ReadmeMaker()
    response = readmeMaker.run()
    if response == Gtk.ResponseType.ACCEPT:
        print(readmeMaker.boxDescription.get_description())
        pass
    readmeMaker.destroy()


if __name__ == '__main__':
    main()
