from gi.repository import Gtk, Adw, Gio, GObject, Gdk
import re

HEX_COLOR_REGEX = re.compile(r"^(?:#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})|rgba?\([0-9\s,.]+\))$")

class ManagementDialog(Adw.Window):
    def __init__(self, logic, refresh_callback, **kwargs):
        super().__init__(**kwargs)
        self.logic = logic
        self.refresh_callback = refresh_callback
        
        self.set_default_size(400, 500)
        self.set_title("Gerenciar Áreas e Tags")
        self.set_modal(True)
        
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(main_box)
        
        header = Adw.HeaderBar()
        header.set_show_start_title_buttons(False)
        header.set_show_end_title_buttons(False)
        main_box.append(header)
        
        self.close_btn = Gtk.Button(label="Fechar")
        self.close_btn.connect("clicked", lambda x: self.close())
        header.pack_end(self.close_btn)
        
        # View Switcher
        view_stack = Adw.ViewStack()
        # Adw.ViewStack doesn't have transition_type like Gtk.Stack in the same way, or it does?
        # Check docs or assume default is fine. Gtk.StackTransitionType might not apply directly or needs different handling.
        # Actually Adw.ViewStack is a subclass of Gtk.Widget that manages pages.
        # It usually just works. Let's remove set_transition_type for now to be safe, or check if it exists.
        # Adw.ViewStack DOES NOT have set_transition_type. It uses internal animation.
        
        switcher_title = Adw.ViewSwitcherTitle(stack=view_stack)
        header.set_title_widget(switcher_title)
        
        # Areas Page
        areas_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        areas_box.set_margin_top(12)
        areas_box.set_margin_bottom(12)
        areas_box.set_margin_start(12)
        areas_box.set_margin_end(12)
        
        # New Area Group
        new_area_group = Adw.PreferencesGroup(title="Nova Área")
        areas_box.append(new_area_group)
        
        self.area_entry = Adw.EntryRow(title="Nome")
        new_area_group.add(self.area_entry)
        
        area_color_row = Adw.ActionRow(title="Cor")
        self.area_color_btn = Gtk.ColorButton()
        self.area_color_btn.set_valign(Gtk.Align.CENTER)
        area_color_row.add_suffix(self.area_color_btn)
        new_area_group.add(area_color_row)
        
        add_area_btn = Gtk.Button(label="Adicionar Área")
        add_area_btn.add_css_class("suggested-action")
        add_area_btn.connect("clicked", self.on_add_area)
        # Wrap button in a box for alignment or just append to page box
        areas_box.append(add_area_btn)
        
        # List Group
        areas_list_group = Adw.PreferencesGroup(title="Áreas Cadastradas")
        self.areas_list = Gtk.ListBox()
        self.areas_list.add_css_class("boxed-list")
        areas_list_group.add(self.areas_list)
        
        areas_box.append(areas_list_group)
        view_stack.add_titled_with_icon(areas_box, "areas", "Áreas", "document-new-symbolic")
        
        # Tags Page
        tags_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        tags_box.set_margin_top(12)
        tags_box.set_margin_bottom(12)
        tags_box.set_margin_start(12)
        tags_box.set_margin_end(12)
        
        # New Tag Group
        new_tag_group = Adw.PreferencesGroup(title="Nova Tag")
        tags_box.append(new_tag_group)
        
        self.tag_entry = Adw.EntryRow(title="Nome")
        new_tag_group.add(self.tag_entry)
        
        tag_color_row = Adw.ActionRow(title="Cor")
        self.tag_color_btn = Gtk.ColorButton()
        self.tag_color_btn.set_valign(Gtk.Align.CENTER)
        tag_color_row.add_suffix(self.tag_color_btn)
        new_tag_group.add(tag_color_row)
        
        add_tag_btn = Gtk.Button(label="Adicionar Tag")
        add_tag_btn.add_css_class("suggested-action")
        add_tag_btn.connect("clicked", self.on_add_tag)
        tags_box.append(add_tag_btn)
        
        # List Group
        tags_list_group = Adw.PreferencesGroup(title="Tags Cadastradas")
        self.tags_list = Gtk.ListBox()
        self.tags_list.add_css_class("boxed-list")
        tags_list_group.add(self.tags_list)
        
        tags_box.append(tags_list_group)
        view_stack.add_titled_with_icon(tags_box, "tags", "Tags", "view-reveal-symbolic")
        
        main_box.append(view_stack)
        
        self.refresh_lists()

    def refresh_lists(self):
        # Refresh Areas
        child = self.areas_list.get_first_child()
        while child:
            self.areas_list.remove(child)
            child = self.areas_list.get_first_child()
            
        for area in self.logic.db.get_areas():
            # area: (id, name, color)
            row = Adw.ActionRow(title=area[1])
            
            # Color indicator
            if len(area) > 2 and area[2]:
                valid_color = False
                if isinstance(area[2], str) and HEX_COLOR_REGEX.match(area[2].strip()):
                    valid_color = True
                
                if valid_color:
                    frame = Gtk.Frame()
                    frame.set_size_request(16, 16)
                    frame.set_valign(Gtk.Align.CENTER)
                    try:
                        provider = Gtk.CssProvider()
                        css = f"* {{ background-color: {area[2]}; border-radius: 50%; }}"
                        provider.load_from_data(css.encode())
                        context = frame.get_style_context()
                        context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
                        row.add_prefix(frame)
                    except: pass
            
            # Wrapper for button alignment
            act_box = Gtk.Box(spacing=6)
            act_box.set_valign(Gtk.Align.CENTER)
            
            # Edit Button
            edit_btn = Gtk.Button(icon_name="document-edit-symbolic")
            edit_btn.add_css_class("flat")
            edit_btn.set_valign(Gtk.Align.CENTER)
            edit_btn.connect("clicked", self.on_edit_clicked, area, "area")
            act_box.append(edit_btn)
            
            del_btn = Gtk.Button(icon_name="user-trash-symbolic")
            del_btn.add_css_class("flat")
            del_btn.add_css_class("error")
            del_btn.set_valign(Gtk.Align.CENTER)
            del_btn.connect("clicked", self.on_delete_area, area[0])
            act_box.append(del_btn)
            
            row.add_suffix(act_box)
            self.areas_list.append(row)
            
        # Refresh Tags
        child = self.tags_list.get_first_child()
        while child:
            self.tags_list.remove(child)
            child = self.tags_list.get_first_child()
            
        for tag in self.logic.db.get_managed_tags():
             # tag: (id, name, color)
            row = Adw.ActionRow(title=tag[1])
            
            if len(tag) > 2 and tag[2]:
                valid_color = False
                if isinstance(tag[2], str) and HEX_COLOR_REGEX.match(tag[2].strip()):
                    valid_color = True

                if valid_color:
                    frame = Gtk.Frame()
                    frame.set_size_request(16, 16)
                    frame.set_valign(Gtk.Align.CENTER)
                    try:
                        provider = Gtk.CssProvider()
                        css = f"* {{ background-color: {tag[2]}; border-radius: 50%; }}"
                        provider.load_from_data(css.encode())
                        context = frame.get_style_context()
                        context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
                        row.add_prefix(frame)
                    except: pass

            # Wrapper for button alignment
            act_box = Gtk.Box(spacing=6)
            act_box.set_valign(Gtk.Align.CENTER)

            # Edit Button
            edit_btn = Gtk.Button(icon_name="document-edit-symbolic")
            edit_btn.add_css_class("flat")
            edit_btn.set_valign(Gtk.Align.CENTER)
            edit_btn.connect("clicked", self.on_edit_clicked, tag, "tag")
            act_box.append(edit_btn)

            del_btn = Gtk.Button(icon_name="user-trash-symbolic")
            del_btn.add_css_class("flat")
            del_btn.add_css_class("error")
            del_btn.set_valign(Gtk.Align.CENTER)
            del_btn.connect("clicked", self.on_delete_tag, tag[0])
            act_box.append(del_btn)
            
            row.add_suffix(act_box)
            self.tags_list.append(row)

    def on_edit_clicked(self, btn, item_data, type):
        # item_data: (id, name, color)
        
        # Simple Dialog for editing
        dlg = Adw.Window()
        dlg.set_transient_for(self)
        dlg.set_modal(True)
        dlg.set_title("Editar")
        dlg.set_default_size(300, 200)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(24)
        box.set_margin_bottom(24)
        box.set_margin_start(24)
        box.set_margin_end(24)
        dlg.set_content(box)
        
        entry = Adw.EntryRow(title="Nome")
        entry.set_text(item_data[1])
        
        wrapper = Adw.PreferencesGroup()
        wrapper.add(entry)
        box.append(wrapper)
        
        color_row = Adw.ActionRow(title="Cor")
        color_btn = Gtk.ColorButton()
        color = Gdk.RGBA()
        if len(item_data) > 2 and item_data[2]:
             color.parse(item_data[2])
        color_btn.set_rgba(color)
        color_btn.set_valign(Gtk.Align.CENTER)
        color_row.add_suffix(color_btn)
        
        wrapper_c = Adw.PreferencesGroup()
        wrapper_c.add(color_row)
        box.append(wrapper_c)
        
        save_btn = Gtk.Button(label="Salvar")
        save_btn.add_css_class("suggested-action")
        save_btn.set_halign(Gtk.Align.CENTER)
        save_btn.connect("clicked", self.on_save_edit_dialog, item_data[0], type, entry, color_btn, dlg)
        box.append(save_btn)
        
        dlg.present()

    def on_save_edit_dialog(self, btn, id, type, entry, color_btn, dlg):
        new_name = entry.get_text()
        new_color = self.rgba_to_hex(color_btn.get_rgba())
        
        if not new_name:
            return
            
        if type == "area":
            self.logic.db.update_area(id, new_name, new_color)
        else:
            self.logic.db.update_managed_tag(id, new_name, new_color)
            
        dlg.close()

        self.refresh_lists()
        if self.refresh_callback:
            self.refresh_callback()

    def on_add_area(self, btn):
        name = self.area_entry.get_text()
        color = self.rgba_to_hex(self.area_color_btn.get_rgba())
        if name:
            self.logic.db.add_area(name, color)
            self.area_entry.set_text("")
            self.refresh_lists()
            if self.refresh_callback:
                self.refresh_callback()

    def on_delete_area(self, btn, area_id):
        self.logic.db.delete_area(area_id)
        self.refresh_lists()
        if self.refresh_callback:
            self.refresh_callback()

    def on_add_tag(self, btn):
        name = self.tag_entry.get_text()
        color = self.rgba_to_hex(self.tag_color_btn.get_rgba())
        if name:
            self.logic.db.add_managed_tag(name, color)
            self.tag_entry.set_text("")
            self.refresh_lists()
            if self.refresh_callback:
                self.refresh_callback()

    def rgba_to_hex(self, rgba):
        return "#%02x%02x%02x" % (int(rgba.red*255), int(rgba.green*255), int(rgba.blue*255))


    def on_delete_tag(self, btn, tag_id):
        self.logic.db.delete_managed_tag(tag_id)
        self.refresh_lists()
        if self.refresh_callback:
            self.refresh_callback()
