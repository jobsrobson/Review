from gi.repository import Gtk, Adw, Gio, GObject
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
        
        self.set_title(topic[1])
        # subtitle with area and localized date
        self.set_subtitle(f"{topic[2]} • Início: {db_to_ui_date(topic[3])}")
        self.set_activatable(True)
        
        # Color indicator
        color_dot = Gtk.Box()
        color_dot.set_size_request(8, 8)
        color_dot.set_valign(Gtk.Align.CENTER)
        color_dot.add_css_class("indicator-dot")
        
        # Use Area color (index 7) if available, else Topic color (index 5)
        # topic tuple: (id, title, area, start_date, tags, color, description, area_color)
        display_color = topic[5]
        if len(topic) > 7 and topic[7]:
            display_color = topic[7]
            
        if display_color:
            provider = Gtk.CssProvider()
            css = f"* {{ background-color: {display_color}; border-radius: 50%; }}"
            provider.load_from_data(css.encode())
            context = color_dot.get_style_context()
            context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            
        self.add_prefix(color_dot)
        
        # Total Study Time
        time_spent = 0
        if len(topic) > 7 and topic[7] is not None:
             time_spent = topic[7]
             
        hours, remainder = divmod(time_spent, 3600)
        minutes, _ = divmod(remainder, 60)
        
        time_label = Gtk.Label(label=f"{hours}h {minutes}m")
        time_label.add_css_class("caption")
        time_label.add_css_class("dim-label")
        time_label.set_valign(Gtk.Align.CENTER)
        self.add_suffix(time_label)


class TopicsView(Gtk.Box):
    def __init__(self, refresh_callback=None, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0, **kwargs)
        self.logic = RevisionLogic()
        self.refresh_all_external = refresh_callback
        self.current_area_filter = None
        
        self.split_view = Adw.NavigationSplitView()
        self.split_view.set_vexpand(True)
        self.append(self.split_view)
        
        # Sidebar
        sidebar_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        sidebar_page = Adw.NavigationPage(child=sidebar_content, title="Áreas")
        self.split_view.set_sidebar(sidebar_page)
        
        self.sidebar_list = Gtk.ListBox()
        self.sidebar_list.add_css_class("navigation-sidebar")
        self.sidebar_list.connect("row-activated", self.on_area_selected)
        
        scrolled_sidebar = Gtk.ScrolledWindow()
        scrolled_sidebar.set_vexpand(True)
        scrolled_sidebar.set_child(self.sidebar_list)
        sidebar_content.append(scrolled_sidebar)
        
        # Content
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content_page = Adw.NavigationPage(child=content_box, title="Tópicos")
        self.split_view.set_content(content_page)
        
        # Search Bar
        self.search_bar = Gtk.SearchBar()
        self.search_bar.set_key_capture_widget(content_box)
        content_box.append(self.search_bar)
        
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_hexpand(True)
        self.search_entry.connect("search-changed", self.on_search_changed)
        self.search_bar.set_child(self.search_entry)
        self.search_bar.connect_entry(self.search_entry)
        
        # List Container
        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.set_vexpand(True)
        content_box.append(self.scrolled)
        
        clamp = Adw.Clamp()
        clamp.set_maximum_size(700)
        self.scrolled.set_child(clamp)
        
        self.list_box = Gtk.ListBox()
        self.list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        self.list_box.add_css_class("boxed-list")
        self.list_box.set_margin_top(24)
        self.list_box.set_margin_bottom(24)
        self.list_box.set_margin_start(24)
        self.list_box.set_margin_end(24)
        self.list_box.connect("row-activated", self.on_row_activated)
        clamp.set_child(self.list_box)

        # Empty State
        self.empty_page = Adw.StatusPage()
        self.empty_page.set_title("Nenhum Tópico")
        self.empty_page.set_description("Adicione um novo tópico ou mude o filtro.")
        self.empty_page.set_icon_name("view-list-bullet-symbolic")
        content_box.append(self.empty_page)
        
        self.refresh_whole_view()

    def refresh_whole_view(self):
        """Called when data changes externally"""
        self.refresh_sidebar()
        self.refresh_topic_list()

    def refresh_sidebar(self):
        # Determine currently selected area to restore it if possible
        # For now, just rebuild
        child = self.sidebar_list.get_first_child()
        while child:
            self.sidebar_list.remove(child)
            child = self.sidebar_list.get_first_child()
            
        all_row = Adw.ActionRow(title="Todos os Tópicos")
        all_row.area_name = None
        all_row.set_activatable(True)
        self.sidebar_list.append(all_row)
        
        if self.current_area_filter is None:
            self.sidebar_list.select_row(all_row)
        
        areas = self.logic.db.get_areas()
        for area in areas:
            row = Adw.ActionRow(title=area[1])
            row.area_name = area[1]
            
            if len(area) > 2 and area[2]:
                dot = Gtk.Box()
                dot.set_size_request(8, 8)
                dot.set_valign(Gtk.Align.CENTER)
                provider = Gtk.CssProvider()
                css = f"* {{ background-color: {area[2]}; border-radius: 50%; }}"
                provider.load_from_data(css.encode())
                context = dot.get_style_context()
                context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
                row.add_prefix(dot)
            
            row.set_activatable(True)
            self.sidebar_list.append(row)
            
            if self.current_area_filter == area[1]:
                self.sidebar_list.select_row(row)

    def refresh_topic_list(self):
        # Refresh Main List based on current filter
        child = self.list_box.get_first_child()
        while child:
            self.list_box.remove(child)
            child = self.list_box.get_first_child()
            
        search_text = normalize_str(self.search_entry.get_text())
        topics = self.logic.db.get_topics()
        
        filtered_count = 0
        for topic in topics:
            # topic: (id, title, area, start_date, tags, color, description, area_color)
            if self.current_area_filter and topic[2] != self.current_area_filter:
                continue
            
            # Normalize topic title for comparison
            normalized_title = normalize_str(topic[1])
            if search_text and search_text not in normalized_title:
                continue
                
            row = TopicRow(topic, self.logic, self.refresh_all_external if self.refresh_all_external else self.refresh_whole_view)
            self.list_box.append(row)
            filtered_count += 1
            
        self.scrolled.set_visible(filtered_count > 0)
        self.empty_page.set_visible(filtered_count == 0)

    # Legacy method name for compatibility if called externally by window.py or others
    def refresh_topics(self):
        self.refresh_whole_view()

    def on_area_selected(self, listbox, row):
        if row:
            self.current_area_filter = getattr(row, 'area_name', None)
        else:
            self.current_area_filter = None
        self.refresh_topic_list() # ONLY refresh list, do not rebuild sidebar
        

    def on_search_changed(self, entry):
        self.refresh_topic_list()

    def on_add_topic_clicked(self, button):
        win = NewTopicWindow(
            logic=self.logic, 
            refresh_callback=self.refresh_all_external if self.refresh_all_external else self.refresh_whole_view,
            transient_for=self.get_native()
        )
        win.present()

    def on_row_activated(self, listbox, row):
        topics = self.logic.db.get_topics()
        for t in topics:
            if t[0] == row.topic_id:
                win = TopicDetailsWindow(
                    topic=t, 
                    logic=self.logic, 
                    refresh_callback=self.refresh_all_external if self.refresh_all_external else self.refresh_whole_view,
                    transient_for=self.get_native()
                )
                win.present()
                break
