from .views.month_view import MonthView
from .views.week_view import WeekView
from .views.topics_view import TopicsView
from .views.timer_widget import TimerWidget
from gi.repository import Gtk, Adw, Gio, GObject, GLib

class ReviewWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_title("Review")
        self.set_default_size(900, 700)

        # Main Layout: Overlay for Floating Timer
        self.overlay = Gtk.Overlay()
        self.set_content(self.overlay)
        
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.overlay.set_child(self.main_box)

        # Header Bar
        self.header = Adw.HeaderBar()
        self.main_box.append(self.header)

        # Timer Widget (Floating at Bottom)
        self.timer_widget = TimerWidget()
        self.timer_widget.set_valign(Gtk.Align.END)
        self.timer_widget.set_halign(Gtk.Align.FILL)
        self.timer_widget.connect("session-finished", self.on_session_finished)
        self.overlay.add_overlay(self.timer_widget)

        # View Switcher Title (shows in the center of HeaderBar)
        self.view_switcher_title = Adw.ViewSwitcherTitle()
        self.header.set_title_widget(self.view_switcher_title)

        # Stack for holding the views
        self.stack = Adw.ViewStack()
        self.main_box.append(self.stack)

        # Connect Switcher to Stack
        self.view_switcher_title.set_stack(self.stack)
        self.stack.connect("notify::visible-child", self.on_view_changed)

        # Actions
        self._setup_actions()

        # HeaderBar Buttons
        self.search_btn = Gtk.ToggleButton(icon_name="system-search-symbolic")
        self.search_btn.set_tooltip_text("Buscar Tópicos")
        self.search_btn.connect("toggled", self.on_search_toggled)
        self.search_btn.set_visible(False) # Hidden by default until Topics view is active
        self.header.pack_start(self.search_btn)

        self.add_btn = Gtk.Button(icon_name="list-add-symbolic")
        self.add_btn.set_tooltip_text("Novo Tópico")
        self.add_btn.set_action_name("win.add-topic")
        self.header.pack_start(self.add_btn)
        
        # Refresh Button
        self.refresh_btn = Gtk.Button(icon_name="view-refresh-symbolic")
        self.refresh_btn.set_tooltip_text("Atualizar Calendário")
        self.refresh_btn.connect("clicked", self.on_refresh_clicked)
        self.header.pack_start(self.refresh_btn)

        # Primary Menu
        menu = Gio.Menu.new()
        menu.append("Gerenciar Áreas e Tags", "win.manage")
        menu.append("Bulk Import", "win.bulk-import")
        menu.append("Configurações", "win.preferences")
        menu.append("Sobre", "win.about")
        
        self.menu_btn = Gtk.MenuButton()
        self.menu_btn.set_icon_name("open-menu-symbolic")
        self.menu_btn.set_menu_model(menu)
        self.header.pack_end(self.menu_btn)

        # Add Views to Stack
        self.month_view = MonthView(refresh_callback=self.refresh_all_views)
        self.stack.add_titled_with_icon(
            self.month_view, 
            "overview", 
            "Visão Geral", 
            "user-home-symbolic" 
        )

        self.week_view = WeekView(refresh_callback=self.refresh_all_views)
        self.stack.add_titled_with_icon(
            self.week_view, 
            "week", 
            "Semana", 
            "view-grid-symbolic" 
        )

        self.topics_view = TopicsView(refresh_callback=self.refresh_all_views)
        self.stack.add_titled_with_icon(
            self.topics_view, 
            "topics", 
            "Tópicos", 
            "view-list-bullet-symbolic" 
        )

        # Add a ViewSwitcher Bar for narrow windows (responsive)
        self.view_switcher_bar = Adw.ViewSwitcherBar()
        self.view_switcher_bar.set_stack(self.stack)
        self.main_box.append(self.view_switcher_bar)

        # Bind the switcher bar visibility to the switcher title visibility
        self.view_switcher_title.bind_property(
            "title-visible",
            self.view_switcher_bar,
            "reveal",
            GObject.BindingFlags.DEFAULT
        )

        # Show Welcome Dialog if DB is empty (first run or reset)
        # Check logic or db directly. Assuming logic is passed or created in window,
        # but window creates TopicsView which creates logic. 
        # Accessing logic via self.topics_view.logic is easiest.
        if self.topics_view.logic.db.is_empty():
            GLib.idle_add(self.show_welcome_dialog)

    def show_welcome_dialog(self):
        from .views.welcome_dialog import WelcomeDialog
        dlg = WelcomeDialog(transient_for=self)
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
        from .models import RevisionLogic
        dlg = ManagementDialog(logic=RevisionLogic(), refresh_callback=self.refresh_all_views, transient_for=self)
        dlg.present()

    def on_preferences_activated(self, action, param):
        from .views.settings_dialog import SettingsDialog
        from .models import RevisionLogic
        # We pass self.application intentionally
        dlg = SettingsDialog(app=self.get_application(), logic=RevisionLogic(), transient_for=self)
        dlg.present()

    def on_bulk_import_activated(self, action, param):
        from .views.bulk_import_dialog import BulkImportDialog
        from .models import RevisionLogic
        dlg = BulkImportDialog(logic=RevisionLogic(), refresh_callback=self.refresh_all_views, transient_for=self)
        dlg.present()

    def on_about_activated(self, action, param):
        about = Adw.AboutWindow(
            transient_for=self,
            application_name="Review",
            application_icon="review-app",
            developer_name="Robson Ricardo",
            version="1.0.1",
            copyright="© 2026",
            website="https://github.com/jobsr/Review"
        )
        about.present()

    def refresh_all_views(self):
        """Refreshes data across all main views."""
        if hasattr(self, 'month_view') and hasattr(self.month_view, 'refresh_calendar'):
            self.month_view.refresh_calendar()
        if hasattr(self, 'week_view') and hasattr(self.week_view, 'refresh_calendar'):
            self.week_view.refresh_calendar()
        if hasattr(self, 'topics_view') and hasattr(self.topics_view, 'refresh_topics'):
            self.topics_view.refresh_topics()

    def on_search_toggled(self, btn):
        is_active = btn.get_active()
        if self.stack.get_visible_child_name() == "topics":
            self.topics_view.search_bar.set_search_mode(is_active)
            if is_active:
                self.topics_view.search_entry.grab_focus()
    
    def on_refresh_clicked(self, btn):
        """Refresh the current calendar view"""
        current_view = self.stack.get_visible_child_name()
        if current_view == "overview" and hasattr(self.month_view, 'refresh_calendar'):
            self.month_view.refresh_calendar()
        elif current_view == "week" and hasattr(self.week_view, 'refresh_calendar'):
            self.week_view.refresh_calendar()

    def on_view_changed(self, stack, param):
        name = stack.get_visible_child_name()
        if name == "topics":
            self.search_btn.set_visible(True)
            self.refresh_btn.set_visible(False)
            # Sync button state with search bar state
            self.search_btn.set_active(self.topics_view.search_bar.get_search_mode())
        else:
            # Calendar views (overview, week)
            self.search_btn.set_visible(False)
            self.search_btn.set_active(False)
            self.refresh_btn.set_visible(True)

    def start_timer(self, topic_id, topic_title):
        self.timer_widget.start_session(topic_id, topic_title)

    def on_session_finished(self, widget, topic_id, duration):
        # Determine current active logic (e.g. from topics_view usually)
        logic = self.topics_view.logic 
        logic.register_study_session(topic_id, duration)
        self.refresh_all_views()
