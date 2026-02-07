from gi.repository import Gtk, Adw, Gio, GObject
from ..utils import db_to_ui_date, ui_to_db_date
from datetime import datetime

class TopicDetailsWindow(Adw.Window):
    def __init__(self, topic, logic, refresh_callback, **kwargs):
        super().__init__(**kwargs)
        self.topic = topic # (id, title, area, start_date, tags, color, description)
        self.logic = logic
        self.refresh_callback = refresh_callback
        
        self.set_default_size(500, 650)
        self.set_title(f"Detalhes: {topic[1]}")
        self.set_modal(True)
        
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(main_box)
        
        header = Adw.HeaderBar()
        header.set_show_start_title_buttons(False)
        header.set_show_end_title_buttons(False)
        main_box.append(header)
        
        # Action Buttons in HeaderBar
        self.cancel_btn = Gtk.Button(label="Cancelar")
        self.cancel_btn.connect("clicked", lambda x: self.close())
        header.pack_start(self.cancel_btn)
        
        self.save_btn = Gtk.Button(label="Salvar")
        self.save_btn.add_css_class("suggested-action")
        self.save_btn.connect("clicked", self.on_save_clicked)
        header.pack_end(self.save_btn)
        
        self.del_btn = Gtk.Button(icon_name="user-trash-symbolic")
        self.del_btn.set_tooltip_text("Excluir Tópico")
        self.del_btn.add_css_class("destructive-action")
        self.del_btn.connect("clicked", self.on_delete_clicked)
        header.pack_end(self.del_btn)
        
        # Scrollable Content
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        main_box.append(scrolled)
        
        clamp = Adw.Clamp()
        scrolled.set_child(clamp)
        
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        content.set_margin_top(24)
        content.set_margin_bottom(24)
        content.set_margin_start(12)
        content.set_margin_end(12)
        clamp.set_child(content)
        
        # Topic Info Section
        info_group = Adw.PreferencesGroup(title="Informações do Tópico")
        content.append(info_group)
        
        self.entry_title = Adw.EntryRow(title="Título")
        self.entry_title.set_text(topic[1])
        info_group.add(self.entry_title)
        
        # Area Selection
        self.areas_data = self.logic.db.get_areas()
        self.area_names = [a[1] for a in self.areas_data]
        self.area_model = Gtk.StringList.new(self.area_names)
        
        self.entry_area_row = Adw.ComboRow(title="Área", model=self.area_model)
        if topic[2] in self.area_names:
            self.entry_area_row.set_selected(self.area_names.index(topic[2]))
        info_group.add(self.entry_area_row)
        
        self.entry_start = Adw.EntryRow(title="Data de Início")
        self.entry_start.set_text(db_to_ui_date(topic[3]))
        info_group.add(self.entry_start)
        
        # Tag Selection
        self.tags_data = self.logic.db.get_managed_tags()
        self.tag_names = [t[1] for t in self.tags_data]
        self.tag_model = Gtk.StringList.new(self.tag_names)
        
        self.entry_tags_row = Adw.ComboRow(title="Tag", model=self.tag_model)
        if topic[4] in self.tag_names:
            self.entry_tags_row.set_selected(self.tag_names.index(topic[4]))
        info_group.add(self.entry_tags_row)

        # Color Selection
        color_row = Adw.ActionRow(title="Cor")
        self.color_btn = Gtk.ColorButton()
        rgba = Gdk.RGBA()
        rgba.parse(topic[5] if topic[5] else "#3584e4")
        self.color_btn.set_rgba(rgba)
        self.color_btn.set_valign(Gtk.Align.CENTER)
        color_row.add_suffix(self.color_btn)
        info_group.add(color_row)
        
        # Time Spent (Read Only)
        time_group = Adw.PreferencesGroup(title="Estatísticas")
        content.append(time_group)
        
        time_row = Adw.ActionRow(title="Tempo Total de Estudo")
        
        seconds = 0
        if len(topic) > 7:
             seconds = topic[7] if topic[7] else 0
             
        hours, remainder = divmod(seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        time_label = Gtk.Label(label=f"{hours}h {minutes}m")
        time_label.set_valign(Gtk.Align.CENTER)
        time_row.add_suffix(time_label)
        time_group.add(time_row)

        # Description Section
        desc_group = Adw.PreferencesGroup(title="Descrição")
        content.append(desc_group)
        
        self.txt_desc = Gtk.TextView()
        self.txt_desc.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.txt_desc.set_top_margin(6)
        self.txt_desc.set_bottom_margin(6)
        self.txt_desc.set_left_margin(6)
        self.txt_desc.set_right_margin(6)
        buf = self.txt_desc.get_buffer()
        buf.set_text(topic[6] if topic[6] else "")
        
        desc_scrolled = Gtk.ScrolledWindow()
        desc_scrolled.set_min_content_height(100)
        desc_scrolled.set_child(self.txt_desc)
        
        frame = Gtk.Frame()
        frame.set_child(desc_scrolled)
        desc_group.add(frame)

    def on_save_clicked(self, btn):
        title = self.entry_title.get_text()
        
        selected_idx = self.entry_area_row.get_selected()
        area = self.area_model.get_string(selected_idx) if selected_idx != Gtk.INVALID_LIST_POSITION else ""
        
        selected_tag_idx = self.entry_tags_row.get_selected()
        tags = self.tag_model.get_string(selected_tag_idx) if selected_tag_idx != Gtk.INVALID_LIST_POSITION else ""
        
        start_date = ui_to_db_date(self.entry_start.get_text())
        color = self.color_btn.get_rgba().to_string()
        
        buf = self.txt_desc.get_buffer()
        start_iter, end_iter = buf.get_bounds()
        description = buf.get_text(start_iter, end_iter, True)
        
        if title:
            self.logic.db.update_topic(self.topic[0], title, area, start_date, tags, color, description)
            if self.refresh_callback:
                self.refresh_callback()
            self.close()

    def on_delete_clicked(self, btn):
        dialog = Adw.MessageDialog(
            transient_for=self,
            heading="Excluir Tópico?",
            body="Isso também excluirá todos os agendamentos relacionados."
        )
        dialog.add_response("cancel", "Cancelar")
        dialog.add_response("delete", "Excluir")
        dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", self.on_delete_confirm)
        dialog.present()

    def on_delete_confirm(self, dialog, response):
        if response == "delete":
            self.logic.db.delete_topic(self.topic[0])
            if self.refresh_callback:
                self.refresh_callback()
            self.close()
        dialog.destroy()
from gi.repository import Gdk
