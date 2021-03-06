#!/usr/bin/env python3
# coding: utf-8

# Copyright (C) 2017, 2018 Robert Griesel
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import GLib
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import Pango

import re
import time

import setzer.workspace.document_switcher.document_switcher_viewgtk as document_switcher_viewgtk
from setzer.app.service_locator import ServiceLocator


class HeaderBar(Gtk.HeaderBar):
    ''' Title bar of the app, contains global controls '''
        
    def __init__(self):
        Gtk.HeaderBar.__init__(self)
        self.pmb = ServiceLocator.get_popover_menu_builder()

        self.set_show_close_button(True)

        # sidebar toggle
        self.sidebar_toggle_revealer = Gtk.Revealer()
        self.sidebar_toggle = Gtk.ToggleButton()
        self.sidebar_toggle.set_image(Gtk.Image.new_from_icon_name('builder-view-left-pane-symbolic', Gtk.IconSize.MENU))
        self.sidebar_toggle.set_focus_on_click(False)
        self.sidebar_toggle.set_tooltip_text('Toggle sidebar (F9)')
        self.pack_start(self.sidebar_toggle)

        # open documents button
        self.document_chooser = DocumentChooser()
        self.open_document_button_label = Gtk.HBox()
        self.open_document_button_label.pack_start(Gtk.Label('Open'), False, False, 0)
        self.open_document_button_label.pack_start(Gtk.Image.new_from_icon_name('pan-down-symbolic', Gtk.IconSize.MENU), False, False, 0)
        self.open_document_button = Gtk.MenuButton()
        self.open_document_button.set_focus_on_click(False)
        self.open_document_button.set_tooltip_text('Open a document (Ctrl+Shift+O)')
        self.open_document_button.set_use_popover(True)
        self.open_document_button.add(self.open_document_button_label)
        self.open_document_button.get_style_context().add_class("text-button")
        self.open_document_button.get_style_context().add_class("image-button")
        self.open_document_button.set_popover(self.document_chooser)
        self.pack_start(self.open_document_button)
        self.open_document_blank_button = Gtk.Button.new_with_label('Open...')
        self.open_document_blank_button.set_tooltip_text('Open a document (Ctrl+O)')
        self.pack_start(self.open_document_blank_button)

        self.new_document_button = Gtk.MenuButton()
        self.new_document_button_label = Gtk.HBox()
        image = Gtk.Image.new_from_icon_name('document-new-symbolic', Gtk.IconSize.BUTTON)
        image.set_margin_right(6)
        self.new_document_button_label.pack_start(image, False, False, 0)
        image = Gtk.Image.new_from_icon_name('pan-down-symbolic', Gtk.IconSize.BUTTON)
        self.new_document_button_label.pack_start(image, False, False, 0)
        self.new_document_button.add(self.new_document_button_label)
        self.new_document_button.set_focus_on_click(False)
        self.new_document_button.set_tooltip_text('Create a new document (Ctrl+N)')
        self.new_document_button.get_style_context().add_class("text-button")
        self.new_document_button.get_style_context().add_class("image-button")
        self.pack_start(self.new_document_button)

        self.new_document_menu = Gio.Menu()
        self.new_document_menu.append_item(Gio.MenuItem.new('New LaTeX Document', 'win.new-latex-document'))
        self.new_document_menu.append_item(Gio.MenuItem.new('New BibTeX Document', 'win.new-bibtex-document'))
        self.new_document_button.set_menu_model(self.new_document_menu)

        # workspace menu
        self.insert_workspace_menu()

        # save document button
        self.save_document_button = Gtk.Button.new_with_label('Save')
        self.save_document_button.set_focus_on_click(False)
        self.save_document_button.set_tooltip_text('Save the current document (Ctrl+S)')
        self.pack_end(self.save_document_button)
        
        # preview toggle
        self.preview_toggle = Gtk.ToggleButton()
        self.preview_toggle.set_image(Gtk.Image.new_from_icon_name('view-paged-symbolic', Gtk.IconSize.MENU))
        self.preview_toggle.set_focus_on_click(False)
        self.preview_toggle.set_tooltip_text('Toggle preview (F10)')
        self.pack_end(self.preview_toggle)
        
        # build button wrapper
        self.build_wrapper = Gtk.VBox()
        self.pack_end(self.build_wrapper)

        # title / open documents popover
        self.mod_binding = None
        self.document_mod_label = Gtk.Label()
        self.name_binding = None
        self.document_name_label = Gtk.Label()
        self.document_name_label.get_style_context().add_class('title')
        self.document_name_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.folder_binding = None
        self.document_folder_label = Gtk.Label()
        self.document_folder_label.get_style_context().add_class('subtitle')
        self.document_folder_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.document_arrow = Gtk.Image.new_from_icon_name('pan-down-symbolic', Gtk.IconSize.MENU)
        vbox = Gtk.VBox()
        vbox.pack_start(self.document_name_label, False, False, 0)
        vbox.pack_start(self.document_folder_label, False, False, 0)
        hbox = Gtk.HBox()
        hbox.pack_start(vbox, False, False, 0)
        hbox.pack_start(self.document_arrow, False, False, 0)
        hbox.set_valign(Gtk.Align.CENTER)
        
        self.open_docs_popover = document_switcher_viewgtk.OpenDocsPopover()
        self.center_widget = Gtk.HBox()
        self.center_button = Gtk.MenuButton()
        self.center_button.get_style_context().add_class('flat')
        self.center_button.get_style_context().add_class('open-docs-popover-button')
        self.center_button.set_tooltip_text('Show open documents (Ctrl+T)')
        self.center_button.set_focus_on_click(False)
        self.center_button.add(hbox)
        self.center_button.set_use_popover(True)
        self.center_button.set_popover(self.open_docs_popover)
        self.center_label_welcome = Gtk.Label("Setzer")
        self.center_label_welcome.get_style_context().add_class('title')
        self.center_widget.pack_start(self.center_button, False, False, 0)
        self.center_widget.pack_start(self.center_label_welcome, False, False, 0)
        self.set_custom_title(self.center_widget)
        self.center_widget.set_valign(Gtk.Align.FILL)
        self.center_button.set_valign(Gtk.Align.FILL)
        self.center_label_welcome.set_valign(Gtk.Align.FILL)

    def insert_workspace_menu(self):
        popover = Gtk.PopoverMenu()
        stack = popover.get_child()

        box = Gtk.VBox()
        self.pmb.set_box_margin(box)
        self.pmb.add_action_button(box, 'Save Document As...', 'win.save-as', keyboard_shortcut='Ctrl+Shift+S')
        self.pmb.add_action_button(box, 'Save All Documents', 'win.save-all')
        self.pmb.add_separator(box)
        self.pmb.add_menu_button(box, 'View', 'view')
        self.pmb.add_menu_button(box, 'Tools', 'tools')
        self.pmb.add_separator(box)
        self.pmb.add_action_button(box, 'Preferences', 'win.show-preferences-dialog')
        self.pmb.add_separator(box)
        self.pmb.add_action_button(box, 'Keyboard Shortcuts', 'win.show-shortcuts-window')
        self.pmb.add_action_button(box, 'About', 'win.show-about-dialog')
        self.pmb.add_separator(box)
        self.pmb.add_action_button(box, 'Close All Documents', 'win.close-all-documents')
        self.pmb.add_action_button(box, 'Close Document', 'win.close-active-document', keyboard_shortcut='Ctrl+W')
        self.pmb.add_action_button(box, 'Quit', 'win.quit', keyboard_shortcut='Ctrl+Q')
        stack.add_named(box, 'main')
        box.show_all()

        # view submenu
        box = Gtk.VBox()
        self.pmb.set_box_margin(box)
        self.pmb.add_header_button(box, 'View')
        self.pmb.add_action_button(box, 'Dark Mode', 'win.toggle-dark-mode')
        stack.add_named(box, 'view')
        box.show_all()

        # tools submenu
        box = Gtk.VBox()
        self.pmb.set_box_margin(box)
        self.pmb.add_header_button(box, 'Tools')
        self.pmb.add_action_button(box, 'Check Spelling...', 'win.spellchecking')
        self.pmb.add_action_button(box, 'Automatic Spellchecking', 'win.toggle-spellchecking')
        self.pmb.add_action_button(box, 'Set Spellchecking Language...', 'win.set-spellchecking-language')
        stack.add_named(box, 'tools')
        box.show_all()

        self.menu_button = Gtk.MenuButton()
        image = Gtk.Image.new_from_icon_name('open-menu-symbolic', Gtk.IconSize.BUTTON)
        self.menu_button.set_image(image)
        self.menu_button.set_focus_on_click(False)
        self.menu_button.set_popover(popover)
        self.pack_end(self.menu_button)


class DocumentChooser(Gtk.Popover):
    ''' GEdit like document chooser widget '''
    
    def __init__(self):
        Gtk.Popover.__init__(self)
        
        self.search_entry = Gtk.SearchEntry()
        self.icon_name = self.search_entry.get_icon_name(Gtk.EntryIconPosition.PRIMARY)
        
        self.auto_suggest_entries = list()
        self.auto_suggest_box = Gtk.ListBox()
        self.auto_suggest_box.set_size_request(398, -1)
        
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.add(self.auto_suggest_box)
        self.scrolled_window.get_style_context().add_class('frame')
        self.scrolled_window.set_min_content_height(295)
        self.scrolled_window.set_min_content_width(398)
        self.scrolled_window.set_max_content_height(295)
        self.scrolled_window.set_max_content_width(398)
        
        self.not_found_slate = Gtk.HBox()
        self.not_found_slate.get_style_context().add_class('not_found')
        self.not_found_slate.get_style_context().add_class('frame')
        box = Gtk.VBox()
        pixbuf = Gtk.IconTheme.get_default().load_icon('system-search-symbolic', 64, 0)
        box.pack_start(Gtk.Image.new_from_pixbuf(pixbuf), True, True, 0)
        box.pack_start(Gtk.Label("No results"), False, False, 0)
        outer_box = Gtk.VBox()
        outer_box.set_center_widget(box)
        self.not_found_slate.set_center_widget(outer_box)
        
        self.other_documents_button = Gtk.Button.new_with_label('Other Documents...')

        self.notebook = Gtk.Notebook()
        self.notebook.set_show_tabs(False)
        self.notebook.set_show_border(False)
        self.notebook.insert_page(self.scrolled_window, None, 0)
        self.notebook.insert_page(self.not_found_slate, None, 1)
        self.notebook.set_current_page(0)
        
        self.box = Gtk.VBox()
        self.box.pack_start(self.search_entry, False, False, 0)
        self.box.pack_start(self.notebook, True, True, 0)
        self.box.pack_start(self.other_documents_button, False, False, 0)
        self.box.show_all()
        self.add(self.box)
        
        self.get_style_context().add_class('documentchooser')
        
    def update_autosuggest(self, items):
        for entry in self.auto_suggest_box.get_children():
            self.auto_suggest_box.remove(entry)
        for item in items:
            entry = DocumentChooserEntry(item[0], item[1])
            self.auto_suggest_box.add(entry)
        return self.search_filter()

    def search_filter(self):
        query = self.search_entry.get_buffer().get_text()
        count = 0
        for entry in self.auto_suggest_box.get_children():
            if query == '':
                if count < 5:
                    entry.highlight_search(query)
                    entry.show_all()
                    count += 1
            elif query.lower() in entry.filename.lower() or query.lower() in entry.folder.lower():
                entry.highlight_search(query)
                entry.show_all()
                count += 1
            else:
                entry.hide()
        self.update_search_entry(count)
        
    def update_search_entry(self, results_count):
        if results_count == 0:
            self.search_entry.get_style_context().add_class('error')
            self.search_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY, 'face-uncertain-symbolic')
            self.notebook.set_current_page(1)
        else:
            self.search_entry.get_style_context().remove_class('error')
            self.search_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY, self.icon_name)
            self.notebook.set_current_page(0)


class DocumentChooserEntry(Gtk.ListBoxRow):
    ''' an item in the document chooser '''
    
    def __init__(self, folder, filename):
        Gtk.ListBoxRow.__init__(self)
        
        self.filename = filename
        self.filename_label = Gtk.Label()
        self.filename_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.filename_label.set_use_markup(True)
        self.filename_label.set_markup(self.filename)
        self.filename_label.set_xalign(0)
        self.folder = folder
        self.folder_label = Gtk.Label()
        self.folder_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.folder_label.set_use_markup(True)
        self.folder_label.set_markup(self.folder)
        self.folder_label.set_xalign(0)
        self.folder_label.get_style_context().add_class('folder')
        
        self.box = Gtk.VBox()
        self.add(self.box)
        
        self.box.pack_start(self.filename_label, False, False, 0)
        self.box.pack_start(self.folder_label, False, False, 0)
        
    def highlight_search(self, query):
        if query != '':
            markup = self.filename
            counter = 0
            for pos in re.finditer(re.escape(query.lower()), self.filename.lower()):
                markup = markup[:pos.start()+counter] + '<b>' + markup[pos.start()+counter:pos.end()+counter] + '</b>' + markup[pos.end()+counter:]
                counter += 7
        else: 
            markup = self.filename
        self.filename_label.set_markup(markup)
        if query != '':
            markup = self.folder
            counter = 0
            for pos in re.finditer(re.escape(query.lower()), self.folder.lower()):
                markup = markup[:pos.start()+counter] + '<span alpha="100%"><b>' + markup[pos.start()+counter:pos.end()+counter] + '</b></span>' + markup[pos.end()+counter:]
                counter += 33
        else:
            markup = self.folder
        self.folder_label.set_markup(markup)


