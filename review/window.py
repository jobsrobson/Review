from .views.month_view import MonthView
from .views.week_view import WeekView
from .views.topics_view import TopicsView
from .views.timer_widget import TimerWidget
from gi.repository import Gtk, Adw, Gio, GObject, GLib, Gdk
import re

HEX_COLOR_REGEX = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")

class ReviewWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_title("Review")
        self.set_default_size(900, 700)


        # Main Layout: Vertical Box
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(self.main_box)
        
        # Navigation Split View (Root)
        self.split_view = Adw.NavigationSplitView()
        self.split_view.set_vexpand(True)
        self.main_box.append(self.split_view)

        # Primary Menu
        menu = Gio.Menu.new()
        menu.append("Gerenciar Áreas e Tags", "win.manage")
        menu.append("Bulk Import", "win.bulk-import")
        menu.append("Configurações", "win.preferences")
        menu.append("Sobre", "win.about")

        # 1. Sidebar Page
        sidebar_toolbar = Adw.ToolbarView()
        
        # Sidebar HeaderBar
        self.sidebar_header = Adw.HeaderBar()
        self.sidebar_header.set_show_end_title_buttons(False)
        self.sidebar_header.set_show_start_title_buttons(False)
        
        # Sidebar Title
        self.sidebar_title = Gtk.Label(label="Review")
        self.sidebar_title.add_css_class("heading")
        self.sidebar_header.set_title_widget(self.sidebar_title)
        
        # Actions in Sidebar
        self.add_btn = Gtk.Button(icon_name="list-add-symbolic")
        self.add_btn.set_tooltip_text("Novo Tópico")
        self.add_btn.set_action_name("win.add-topic")
        self.sidebar_header.pack_start(self.add_btn)
        
        self.menu_btn = Gtk.MenuButton()
        self.menu_btn.set_icon_name("open-menu-symbolic")
        self.menu_btn.set_tooltip_text("Menu")
        self.menu_btn.set_menu_model(menu)
        self.sidebar_header.pack_end(self.menu_btn)
        
        sidebar_toolbar.add_top_bar(self.sidebar_header)

        # Sidebar Content
        sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.nav_list = Gtk.ListBox()
        self.nav_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.nav_list.add_css_class("navigation-sidebar") # Native list style
        self.nav_list.connect("row-activated", self.on_nav_row_activated)
        sidebar_box.append(self.nav_list)

        self.add_nav_item("Hoje", "user-home-symbolic", "today")
        self.add_nav_item("Calendário", "calendar-month-symbolic", "overview")
        self.add_nav_item("Tópicos", "view-list-bullet-symbolic", "topics")
        
        # Separator for Areas
        self.area_separator = Gtk.ListBoxRow()
        self.area_separator.set_activatable(False)
        self.area_separator.set_selectable(False)
        self.area_separator.set_margin_top(16)
        
        sep_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        sep_label = Gtk.Label(label="Áreas")
        sep_label.add_css_class("dim-label")
        sep_label.add_css_class("caption")
        sep_label.set_halign(Gtk.Align.START)
        sep_label.set_margin_start(12)
        sep_label.set_margin_bottom(6)
        sep_box.append(sep_label)
        sep_line = Gtk.Separator()
        sep_line.set_margin_start(0) # Margem linha separador
        sep_line.set_margin_end(0)
        sep_box.append(sep_line)
        self.area_separator.set_child(sep_box)
        self.nav_list.append(self.area_separator)
        
        
        sidebar_toolbar.set_content(sidebar_box)
        sidebar_page = Adw.NavigationPage(child=sidebar_toolbar, title="Menu")
        self.split_view.set_sidebar(sidebar_page)

        # 2. Content Page
        content_toolbar = Adw.ToolbarView()
        self.header = Adw.HeaderBar()
        self.header.set_show_back_button(False) # Prevent automatic back button
        
        self.content_title = Adw.WindowTitle(title="Hoje")
        self.header.set_title_widget(self.content_title)
        
        # Sidebar Toggle Button (Custom)
        self.sidebar_toggle = Gtk.ToggleButton(icon_name="sidebar-show-symbolic")
        self.sidebar_toggle.set_tooltip_text("Alternar Menu")
        self.header.pack_start(self.sidebar_toggle)
        
        self.refresh_btn = Gtk.Button(icon_name="view-refresh-symbolic")
        self.refresh_btn.set_tooltip_text("Atualizar")
        self.refresh_btn.connect("clicked", self.on_refresh_clicked)
        self.header.pack_start(self.refresh_btn)

        content_toolbar.add_top_bar(self.header)

        # Content Main Stack
        self.stack = Adw.ViewStack()
        self.stack.connect("notify::visible-child-name", self.on_view_changed)
        content_toolbar.set_content(self.stack)
        
        content_page = Adw.NavigationPage(child=content_toolbar, title="Review")
        self.split_view.set_content(content_page)

        # Views
        from .views.today_view import TodayView
        self.today_view = TodayView(refresh_callback=self.refresh_all_views)
        self.stack.add_named(self.today_view, "today")

        self.month_view = MonthView(refresh_callback=self.refresh_all_views)
        self.stack.add_named(self.month_view, "overview")

        self.topics_view = TopicsView(refresh_callback=self.refresh_all_views)
        self.stack.add_named(self.topics_view, "topics")

        # Breakpoint
        breakpoint = Adw.Breakpoint.new(Adw.BreakpointCondition.parse("max-width: 600px"))
        breakpoint.add_setter(self.split_view, "collapsed", True)
        self.add_breakpoint(breakpoint)

        # Bind toggle button active state to collapsed state
        self.split_view.bind_property("collapsed", self.sidebar_toggle, "active", 
                                      GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.BIDIRECTIONAL)
        self.split_view.connect("notify::collapsed", self.on_collapsed_changed)

        # Initial Refresh
        self.split_view.set_show_content(True)
        self.on_view_changed(self.stack, None)
        self.refresh_sidebar_areas()
        self._setup_actions()
        
        # Timer Widget (Floating)
        self.timer_widget = TimerWidget()
        self.timer_widget.connect("session-finished", self.on_session_finished)
        self.timer_widget.connect("fullscreen-toggled", self.on_timer_fullscreen_toggled)
        self.main_box.append(self.timer_widget)

        # Show Welcome Dialog if DB is empty (first run or reset)
        # Check logic or db directly. Assuming logic is passed or created in window,
        # but window creates TopicsView which creates logic. 
        # Accessing logic via self.topics_view.logic is easiest.
        if self.topics_view.logic.db.is_empty():
            GLib.idle_add(self.show_welcome_dialog)

    def show_welcome_dialog(self):
        from .views.welcome_dialog import WelcomeDialog
        dlg = WelcomeDialog(logic=self.topics_view.logic, refresh_callback=self.refresh_all_views, transient_for=self)
        dlg.present()

    def _setup_actions(self):
        action_group = Gio.SimpleActionGroup()
        self.insert_action_group("win", action_group)

        add_topic_action = Gio.SimpleAction.new("add-topic", None)
        add_topic_action.connect("activate", self.on_add_topic_activated)
        action_group.add_action(add_topic_action)

        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.on_about_activated)
        action_group.add_action(about_action)

        # Bulk Import Action
        bulk_import_action = Gio.SimpleAction.new("bulk-import", None)
        bulk_import_action.connect("activate", self.on_bulk_import_activated)
        action_group.add_action(bulk_import_action)
        
        manage_action = Gio.SimpleAction.new("manage", None)
        manage_action.connect("activate", self.on_manage_activated)
        action_group.add_action(manage_action)
        
        pref_action = Gio.SimpleAction.new("preferences", None)
        pref_action.connect("activate", self.on_preferences_activated)
        action_group.add_action(pref_action)

    def on_add_topic_activated(self, action, param):
        self.topics_view.on_add_topic_clicked(None)

    def on_manage_activated(self, action, param):
        from .views.management_dialog import ManagementDialog
        dlg = ManagementDialog(logic=self.topics_view.logic, refresh_callback=self.refresh_all_views, transient_for=self)
        dlg.present()

    def on_preferences_activated(self, action, param):
        from .views.settings_dialog import SettingsDialog
        # We pass self.application intentionally
        dlg = SettingsDialog(app=self.get_application(), logic=self.topics_view.logic, transient_for=self)
        dlg.present()

    def on_bulk_import_activated(self, action, param):
        from .views.bulk_import_dialog import BulkImportDialog
        # Use existing logic for database consistency
        logic = self.topics_view.logic
        dlg = BulkImportDialog(logic=logic, refresh_callback=self.refresh_all_views, transient_for=self)
        dlg.connect("destroy", lambda w: self._on_import_closed())
        dlg.present()

    def _on_import_closed(self):
        def check_and_reshow():
            if hasattr(self, 'topics_view') and self.topics_view.logic.db.is_empty():
                self.show_welcome_dialog()
            return False
        GLib.idle_add(check_and_reshow)

    def on_about_activated(self, action, param):
        about = Adw.AboutWindow(
            transient_for=self,
            application_name="Review",
            application_icon="review-app",
            developer_name="Robson Ricardo",
            version="2.0.0",
            copyright="© 2026",
            website="https://github.com/jobsr/Review"
        )
        about.present()

    def on_collapsed_changed(self, split_view, param):
        if split_view.get_collapsed():
            split_view.set_show_content(True)

    def refresh_sidebar_areas(self):
        # Remove old area rows (everything after the separator)
        child = self.area_separator.get_next_sibling()
        while child:
            next_child = child.get_next_sibling()
            self.nav_list.remove(child)
            child = next_child
        
        # Add current areas
        areas = self.topics_view.logic.db.get_areas()
        for area in areas:
            self.add_nav_item(area[1], "tag-symbolic", f"area:{area[1]}", color=area[2])

    def add_nav_item(self, title, icon_name, view_name, color=None):
        row = Gtk.ListBoxRow()
        row.view_name = view_name
        
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box.set_margin_top(6)
        box.set_margin_bottom(6)
        box.set_margin_start(12)
        box.set_margin_end(12)
        
        valid_color = False
        if color and isinstance(color, str):
            if HEX_COLOR_REGEX.match(color.strip()):
                valid_color = True

        if valid_color:
            dot = Gtk.Box()
            dot.set_size_request(8, 8)
            dot.set_valign(Gtk.Align.CENTER)
            dot.add_css_class("color-dot")
            try:
                provider = Gtk.CssProvider()
                css = f".color-dot {{ background-color: {color}; border-radius: 50%; }}"
                provider.load_from_data(css.encode())
                dot.get_style_context().add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
                box.append(dot)
            except Exception:
                pass
        else:
            icon = Gtk.Image.new_from_icon_name(icon_name)
            icon.set_pixel_size(16)
            box.append(icon)
        
        label = Gtk.Label(label=title)
        label.set_halign(Gtk.Align.START)
        box.append(label)
        
        row.set_child(box)
        self.nav_list.append(row)
        if view_name == "today":
            self.nav_list.select_row(row)

    def on_nav_row_activated(self, listbox, row):
        if row and hasattr(row, 'view_name'):
            view_name = row.view_name
            if view_name.startswith("area:"):
                if not hasattr(self, 'topics_view'): return
                area_name = view_name.split(":", 1)[1]
                self.topics_view.current_area_filter = area_name
                self.topics_view.refresh_topic_list()
                self.stack.set_visible_child_name("topics")
            else:
                if view_name == "topics" and hasattr(self, 'topics_view'):
                    self.topics_view.current_area_filter = None
                    self.topics_view.refresh_topic_list()
                self.stack.set_visible_child_name(view_name)
            
            # On narrow windows, hide sidebar after selection
            if self.split_view.get_collapsed():
                self.split_view.set_show_content(True)

    def refresh_all_views(self):
        """Refreshes data across all main views."""
        if hasattr(self, 'today_view') and hasattr(self.today_view, 'refresh_view'):
            self.today_view.refresh_view()
        if hasattr(self, 'month_view') and hasattr(self.month_view, 'refresh_calendar'):
            self.month_view.refresh_calendar()
        if hasattr(self, 'week_view') and hasattr(self.week_view, 'refresh_calendar'):
            self.week_view.refresh_calendar()
        if hasattr(self, 'topics_view') and hasattr(self.topics_view, 'refresh_topics'):
            self.topics_view.refresh_topics()
            self.refresh_sidebar_areas()

    
    def on_refresh_clicked(self, btn):
        """Refresh the current calendar view"""
        current_view = self.stack.get_visible_child_name()
        if current_view == "today" and hasattr(self.today_view, 'refresh_view'):
            self.today_view.refresh_view()
        elif current_view == "overview" and hasattr(self.month_view, 'refresh_calendar'):
            self.month_view.refresh_calendar()
        elif current_view == "week" and hasattr(self.week_view, 'refresh_calendar'):
            self.week_view.refresh_calendar()

    def on_view_changed(self, stack, param):
        name = stack.get_visible_child_name()
        
        # Update Header Title
        titles = {
            "today": "Hoje",
            "overview": "Calendário",
            "topics": "Tópicos"
        }
        self.content_title.set_title(titles.get(name, "Review"))
        
        # Show/Hide Refresh Button
        if name == "topics":
            self.refresh_btn.set_visible(False)
        else:
            self.refresh_btn.set_visible(True)

    def start_timer(self, topic_id, topic_title):
        self.timer_widget.start_session(topic_id, topic_title)

    def on_session_finished(self, widget, topic_id, duration):
        # Determine current active logic (e.g. from topics_view usually)
        logic = self.topics_view.logic 
        logic.register_study_session(topic_id, duration)
        self.refresh_all_views()

    def on_timer_fullscreen_toggled(self, widget, is_fullscreen):
        self.split_view.set_visible(not is_fullscreen)
