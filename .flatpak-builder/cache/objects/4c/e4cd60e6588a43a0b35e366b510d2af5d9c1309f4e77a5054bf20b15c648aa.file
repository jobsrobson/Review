from gi.repository import Gtk, Adw, Gio, GObject, Gdk
from ..models import RevisionLogic
from datetime import datetime
from .topic_details import TopicDetailsWindow
from .new_topic_dialog import NewTopicWindow
from ..utils import db_to_ui_date, normalize_str

class TopicRow(Adw.ActionRow):
    def __init__(self, topic, logic, refresh_callback, **kwargs):
        super().__init__(**kwargs)
        self.topic_id = topic[0]
        self.logic = logic
        self.refresh_callback = refresh_callback
        
        self.add_css_class("card")
        self.set_margin_bottom(8)
        self.set_activatable(True)
        
        self.set_title(topic[1])
        self.set_subtitle(topic[2]) # Subtitle is just the Area name
        
        # Color indicator
        color_dot = Gtk.Box()
        color_dot.set_size_request(10, 10)
        color_dot.set_valign(Gtk.Align.CENTER)
        color_dot.add_css_class("indicator-dot")
        
        display_color = topic[5]
        if len(topic) > 7 and topic[7]:
            display_color = topic[7]
            
        if display_color:
            provider = Gtk.CssProvider()
            css = f"* {{ background-color: {display_color}; border-radius: 50%; }}"
            provider.load_from_data(css.encode())
            color_dot.get_style_context().add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            
        self.add_prefix(color_dot)
        
        # Suffix components
        suffix_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        suffix_box.set_valign(Gtk.Align.CENTER)
        
        # Next Revision Info
        next_rev = self.get_next_revision(topic[0])
        if next_rev:
            next_date_ui = db_to_ui_date(next_rev[2])
            today = datetime.now().strftime('%Y-%m-%d')
            
            next_lbl = Gtk.Label()
            next_lbl.add_css_class("caption")
            
            if next_rev[2] < today:
                next_lbl.set_label(f"Atrasado: {next_date_ui}")
                next_lbl.add_css_class("error")
            elif next_rev[2] == today:
                next_lbl.set_label("Revisão Hoje")
                next_lbl.add_css_class("success")
            else:
                next_lbl.set_label(f"Próxima: {next_date_ui}")
                next_lbl.add_css_class("dim-label")
            
            suffix_box.append(next_lbl)
        
        # Time Spent
        time_spent = topic[7] if len(topic) > 7 and topic[7] is not None else 0
        hours, remainder = divmod(time_spent, 3600)
        minutes, _ = divmod(remainder, 60)
        
        time_lbl = Gtk.Label(label=f"{hours}h {minutes}m")
        time_lbl.add_css_class("dim-label")
        time_lbl.add_css_class("caption")
        suffix_box.append(time_lbl)

        self.add_suffix(suffix_box)

    def get_next_revision(self, topic_id):
        cursor = self.logic.db.conn.cursor()
        cursor.execute('''
            SELECT * FROM revisions 
            WHERE topic_id = ? AND status = 'pending' 
            ORDER BY scheduled_date ASC LIMIT 1
        ''', (topic_id,))
        return cursor.fetchone()


class TopicsView(Gtk.Box):
    def __init__(self, refresh_callback=None, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0, **kwargs)
        self.logic = RevisionLogic()
        self.refresh_all_external = refresh_callback
        self.current_area_filter = None
        
        self.set_margin_top(0) 
        self.set_margin_bottom(0)
        
        self.split_view = Adw.NavigationSplitView()
        self.split_view.set_vexpand(True)
        self.append(self.split_view)
        
        # Sidebar Page
        sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        sidebar_box.add_css_class("navigation-sidebar")
        sidebar_box.set_margin_top(0)
        
        self.sidebar_list = Gtk.ListBox()
        self.sidebar_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.sidebar_list.add_css_class("sidebar")
        self.sidebar_list.connect("row-activated", self.on_area_selected)
        
        self.sidebar_gesture = Gtk.GestureClick()
        self.sidebar_gesture.set_button(3)
        self.sidebar_gesture.connect("pressed", self.on_sidebar_right_click)
        self.sidebar_list.add_controller(self.sidebar_gesture)
        
        scrolled_sidebar = Gtk.ScrolledWindow()
        scrolled_sidebar.set_vexpand(True)
        scrolled_sidebar.set_child(self.sidebar_list)
        sidebar_box.append(scrolled_sidebar)
        
        # Use ToolbarView to ensure no extra header padding is added
        sidebar_toolbar = Adw.ToolbarView()
        sidebar_toolbar.set_content(sidebar_box)
        
        sidebar_page = Adw.NavigationPage(child=sidebar_toolbar, title="")
        self.split_view.set_sidebar(sidebar_page)
        
        # Content Page
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content_box.set_margin_top(12) 
        
        content_toolbar = Adw.ToolbarView()
        content_toolbar.set_content(content_box)
        
        content_page = Adw.NavigationPage(child=content_toolbar, title="")
        self.split_view.set_content(content_page)
        
        # Control Bar (Search + Sort)
        control_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        control_bar.set_margin_start(24)
        control_bar.set_margin_end(24)
        control_bar.set_margin_top(18)
        control_bar.set_margin_bottom(6)
        content_box.append(control_bar)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_hexpand(True)
        self.search_entry.set_placeholder_text("Pesquisar tópicos...")
        self.search_entry.connect("search-changed", self.on_search_changed)
        control_bar.append(self.search_entry)

        self.sort_dropdown = Gtk.DropDown.new_from_strings(["Título (A-Z)", "Por Área", "Mais Recentes Primeiro"])
        self.sort_dropdown.connect("notify::selected", self.on_sort_changed)
        control_bar.append(self.sort_dropdown)
        
        # List Container
        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolled.set_vexpand(True)
        content_box.append(self.scrolled)
        
        clamp = Adw.Clamp()
        clamp.set_maximum_size(800)
        self.scrolled.set_child(clamp)
        
        self.list_box = Gtk.ListBox()
        self.list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        self.list_box.set_margin_top(12)
        self.list_box.set_margin_bottom(32)
        self.list_box.set_margin_start(12)
        self.list_box.set_margin_end(12)
        self.list_box.connect("row-activated", self.on_row_activated)
        
        provider = Gtk.CssProvider()
        provider.load_from_data("list { background-color: transparent; }".encode())
        self.list_box.get_style_context().add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        
        clamp.set_child(self.list_box)

        # Empty State
        self.empty_page = Adw.StatusPage()
        self.empty_page.set_title("Nenhum Tópico Encontrado")
        self.empty_page.set_description("Tente ajustar seus filtros ou adicione um novo tópico.")
        self.empty_page.set_icon_name("view-list-bullet-symbolic")
        content_box.append(self.empty_page)
        
        self.refresh_whole_view()

    def refresh_whole_view(self):
        self.refresh_sidebar()
        self.refresh_topic_list()

    def refresh_topics(self):
        self.refresh_whole_view()

    def refresh_sidebar(self):
        child = self.sidebar_list.get_first_child()
        while child:
            self.sidebar_list.remove(child)
            child = self.sidebar_list.get_first_child()
            
        all_row = Adw.ActionRow(title="Todos os Tópicos")
        all_row.area_name = None
        all_row.add_prefix(Gtk.Image.new_from_icon_name("view-list-bullet-symbolic"))
        all_row.set_activatable(True)
        self.sidebar_list.append(all_row)
        
        if self.current_area_filter is None:
            self.sidebar_list.select_row(all_row)
        
        areas = self.logic.db.get_areas()
        for area in areas:
            row = Adw.ActionRow(title=area[1])
            row.area_name = area[1]
            row.set_activatable(True)
            
            if len(area) > 2 and area[2]:
                dot = Gtk.Box()
                dot.set_size_request(8, 8)
                dot.set_valign(Gtk.Align.CENTER)
                provider = Gtk.CssProvider()
                css = f"* {{ background-color: {area[2]}; border-radius: 50%; }}"
                provider.load_from_data(css.encode())
                dot.get_style_context().add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
                row.add_prefix(dot)
            
            gesture = Gtk.GestureClick()
            gesture.set_button(3)
            gesture.connect("pressed", self.on_area_row_right_click, area)
            row.add_controller(gesture)
            
            self.sidebar_list.append(row)
            if self.current_area_filter == area[1]:
                self.sidebar_list.select_row(row)

    def refresh_topic_list(self):
        child = self.list_box.get_first_child()
        while child:
            self.list_box.remove(child)
            child = self.list_box.get_first_child()
            
        search_text = normalize_str(self.search_entry.get_text())
        topics = self.logic.db.get_topics()
        
        sort_idx = self.sort_dropdown.get_selected()
        if sort_idx == 0: topics.sort(key=lambda x: x[1].lower())
        elif sort_idx == 1: topics.sort(key=lambda x: (x[2].lower(), x[1].lower()))
        elif sort_idx == 2: topics.sort(key=lambda x: (x[3], x[1].lower()), reverse=True)

        filtered_count = 0
        for topic in topics:
            if self.current_area_filter and topic[2] != self.current_area_filter: continue
            if search_text and search_text not in normalize_str(topic[1]): continue
            row = TopicRow(topic, self.logic, self.refresh_all_external if self.refresh_all_external else self.refresh_whole_view)
            self.list_box.append(row)
            filtered_count += 1
        self.scrolled.set_visible(filtered_count > 0)
        self.empty_page.set_visible(filtered_count == 0)

    def on_sort_changed(self, dropdown, pspec):
        self.refresh_topic_list()

    def on_area_selected(self, listbox, row):
        if row: self.current_area_filter = getattr(row, 'area_name', None)
        self.refresh_topic_list()

    def on_search_changed(self, entry):
        self.refresh_topic_list()

    def on_row_activated(self, listbox, row):
        if hasattr(row, 'topic_id'):
            topics = self.logic.db.get_topics()
            for t in topics:
                if t[0] == row.topic_id:
                    win = TopicDetailsWindow(topic=t, logic=self.logic, refresh_callback=self.refresh_all_external if self.refresh_all_external else self.refresh_whole_view, transient_for=self.get_native())
                    win.present()
                    break

    def on_add_topic_clicked(self, btn):
        dlg = NewTopicWindow(logic=self.logic, refresh_callback=self.refresh_all_external if self.refresh_all_external else self.refresh_whole_view, transient_for=self.get_native())
        dlg.present()

    def on_sidebar_right_click(self, gesture, n_press, x, y):
        targeted_row = self.sidebar_list.get_row_at_y(y)
        if targeted_row and getattr(targeted_row, 'area_name', None) is not None:
            return 
            
        menu = Gio.Menu()
        menu.append("Adicionar nova área", "sidebar.add_area")
        popover = Gtk.PopoverMenu.new_from_model(menu)
        popover.set_parent(gesture.get_widget()) 
        popover.set_has_arrow(False)
        popover.set_pointing_to(Gdk.Rectangle(x=int(x), y=int(y), width=1, height=1))
        
        action_group = Gio.SimpleActionGroup()
        add_action = Gio.SimpleAction.new("add_area", None)
        add_action.connect("activate", lambda a, p: self.show_area_dialog())
        action_group.add_action(add_action)
        popover.insert_action_group("sidebar", action_group)
        popover.popup()

    def on_area_row_right_click(self, gesture, n_press, x, y, area):
        menu = Gio.Menu()
        menu.append("Editar área", "area.edit")
        menu.append("Apagar área", "area.delete")
        popover = Gtk.PopoverMenu.new_from_model(menu)
        popover.set_parent(gesture.get_widget()) 
        popover.set_has_arrow(False)
        popover.set_pointing_to(Gdk.Rectangle(x=int(x), y=int(y), width=1, height=1))
        
        action_group = Gio.SimpleActionGroup()
        edit_action = Gio.SimpleAction.new("edit", None)
        edit_action.connect("activate", lambda a, p: self.show_area_dialog(area))
        action_group.add_action(edit_action)
        delete_action = Gio.SimpleAction.new("delete", None)
        delete_action.connect("activate", lambda a, p: self.confirm_delete_area(area))
        action_group.add_action(delete_action)
        popover.insert_action_group("area", action_group)
        popover.popup()

    def show_area_dialog(self, area=None):
        title = "Editar Área" if area else "Nova Área"
        dialog = Adw.MessageDialog(transient_for=self.get_native(), heading=title)
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        entry = Gtk.Entry()
        entry.set_placeholder_text("Nome da área")
        if area: entry.set_text(area[1])
        content.append(entry)
        color_btn = Gtk.ColorButton()
        if area and len(area) > 2 and area[2]:
            rgba = Gdk.RGBA()
            if rgba.parse(area[2]): color_btn.set_rgba(rgba)
        content.append(color_btn)
        dialog.set_extra_child(content)
        dialog.add_response("cancel", "Cancelar")
        dialog.add_response("save", "Salvar")
        dialog.set_default_response("save")
        dialog.connect("response", self.on_area_dialog_response, area, entry, color_btn)
        dialog.present()

    def on_area_dialog_response(self, dialog, response, area, entry, color_btn):
        if response == "save":
            name = entry.get_text()
            color = color_btn.get_rgba().to_string()
            if name:
                if area: self.logic.db.update_area(area[0], name, color)
                else: self.logic.db.add_area(name, color)
                self.refresh_whole_view()
        dialog.destroy()

    def confirm_delete_area(self, area):
        title = "Apagar Área?"
        body = f"Deseja realmente apagar a área '{area[1]}'? Os tópicos desta área não serão apagados, mas ficarão sem área associada."
        dialog = Adw.MessageDialog(transient_for=self.get_native(), heading=title, body=body)
        dialog.add_response("cancel", "Cancelar")
        dialog.add_response("delete", "Apagar")
        dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", self.on_delete_area_response, area)
        dialog.present()

    def on_delete_area_response(self, dialog, response, area):
        if response == "delete":
            self.logic.db.delete_area(area[0])
            if self.current_area_filter == area[1]: self.current_area_filter = None
            self.refresh_whole_view()
        dialog.destroy()
