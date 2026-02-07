from gi.repository import Gtk, Adw, Gio, GObject
from datetime import datetime
from ..utils import db_to_ui_date, ui_to_db_date

class NewTopicWindow(Adw.Window):
    def __init__(self, logic, refresh_callback, **kwargs):
        super().__init__(**kwargs)
        self.logic = logic
        self.refresh_callback = refresh_callback
        
        self.set_default_size(400, -1)
        self.set_title("Novo Tópico")
        self.set_modal(True)
        
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(main_box)
        
        header = Adw.HeaderBar()
        header.set_show_start_title_buttons(False)
        header.set_show_end_title_buttons(False)
        main_box.append(header)
        
        # Header buttons
        self.cancel_btn = Gtk.Button(label="Cancelar")
        self.cancel_btn.connect("clicked", lambda x: self.close())
        header.pack_start(self.cancel_btn)
        
        self.add_btn = Gtk.Button(label="Adicionar")
        self.add_btn.add_css_class("suggested-action")
        self.add_btn.connect("clicked", self.on_add_clicked)
        header.pack_end(self.add_btn)
        
        clamp = Adw.Clamp()
        clamp.set_maximum_size(400)
        main_box.append(clamp)
        
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        content.set_margin_top(24)
        content.set_margin_bottom(24)
        content.set_margin_start(24)
        content.set_margin_end(24)
        clamp.set_child(content)
        
        group = Adw.PreferencesGroup()
        content.append(group)
        
        self.entry_title = Adw.EntryRow(title="Título")
        group.add(self.entry_title)
        
        # Area Selection
        self.areas = self.logic.db.get_areas()
        self.area_model = Gtk.StringList.new([a[1] for a in self.areas])
        
        self.entry_area_row = Adw.ComboRow(title="Área", model=self.area_model)
        group.add(self.entry_area_row)
        
        self.entry_start = Adw.EntryRow(title="Data de Início")
        self.entry_start.set_text(db_to_ui_date(datetime.now().strftime('%Y-%m-%d')))
        group.add(self.entry_start)
        
        # Tag Selection
        self.tags_data = self.logic.db.get_managed_tags()
        self.tag_names = [t[1] for t in self.tags_data]
        self.tag_model = Gtk.StringList.new(self.tag_names)
        
        self.entry_tag_row = Adw.ComboRow(title="Tag", model=self.tag_model)
        group.add(self.entry_tag_row)
        
        self.entry_desc = Adw.EntryRow(title="Descrição")
        group.add(self.entry_desc)

    def on_add_clicked(self, btn):
        title = self.entry_title.get_text()
        
        selected_area_idx = self.entry_area_row.get_selected()
        area = self.area_model.get_string(selected_area_idx) if selected_area_idx != Gtk.INVALID_LIST_POSITION else ""
        
        selected_tag_idx = self.entry_tag_row.get_selected()
        tags = self.tag_model.get_string(selected_tag_idx) if selected_tag_idx != Gtk.INVALID_LIST_POSITION else ""
        
        start_date = ui_to_db_date(self.entry_start.get_text())
        desc = self.entry_desc.get_text()
        
        if title:
            # Add color support if needed, using default for now
            self.logic.create_topic_with_revisions(title, area, start_date, tags, "#3584e4", desc)
            if self.refresh_callback:
                self.refresh_callback()
            self.close()
