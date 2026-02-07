from gi.repository import Gtk, Adw, Gio, GLib, Gdk
from ..models import RevisionLogic
from datetime import datetime, timedelta
from ..utils import db_to_ui_date
import re

HEX_COLOR_REGEX = re.compile(r"^(?:#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})|rgba?\([0-9\s,.]+\))$")

def format_time(seconds):
    """Format time intelligently: minutes until 59, then hours"""
    if seconds < 3600:  # Less than 1 hour
        minutes = seconds // 60
        return f"{minutes}min"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if minutes > 0:
            return f"{hours}h {minutes}min"
        return f"{hours}h"

class StatCard(Gtk.Box):
    """Stat card widget"""
    def __init__(self, title, icon_name, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8, **kwargs)
        self.add_css_class("card")
        self.set_hexpand(True)  # Expand horizontally
        
        inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        inner.set_margin_top(16)
        inner.set_margin_bottom(16)
        inner.set_margin_start(16)
        inner.set_margin_end(16)
        self.append(inner)
        
        icon = Gtk.Image.new_from_icon_name(icon_name)
        icon.set_pixel_size(24)
        icon.add_css_class("dim-label")
        inner.append(icon)
        
        self.value_label = Gtk.Label(label="0")
        self.value_label.add_css_class("title-1")
        inner.append(self.value_label)
        
        title_lbl = Gtk.Label(label=title)
        title_lbl.add_css_class("caption")
        title_lbl.add_css_class("dim-label")
        title_lbl.set_wrap(True)
        title_lbl.set_justify(Gtk.Justification.CENTER)
        inner.append(title_lbl)
    
    def set_value(self, value):
        self.value_label.set_label(str(value))

class TodayTopicRow(Adw.ActionRow):
    """Row for a topic in today's revision list"""
    def __init__(self, revision, topic, logic, refresh_callback, parent_view, **kwargs):
        super().__init__(**kwargs)
        self.revision = revision
        self.topic = topic
        self.logic = logic
        self.refresh_callback = refresh_callback
        self.parent_view = parent_view
        
        self.add_css_class("card")
        self.set_margin_bottom(8)
        
        # Increase row height for better spacing
        self.set_size_request(-1, 72)
        
        # Title and subtitle - with ellipsization
        self.set_title(topic[1])  # Topic title
        self.set_subtitle(topic[2])  # Area
        
        # Enable ellipsization to prevent multi-line titles
        title_widget = self.get_first_child()
        if title_widget:
            # Find the title label
            def find_title_label(widget):
                if isinstance(widget, Gtk.Label):
                    return widget
                if hasattr(widget, 'get_first_child'):
                    child = widget.get_first_child()
                    while child:
                        result = find_title_label(child)
                        if result:
                            return result
                        child = child.get_next_sibling()
                return None
            
            title_label = find_title_label(title_widget)
            if title_label:
                title_label.set_ellipsize(3)  # ELLIPSIZE_END
                title_label.set_max_width_chars(50)
        
        # Color indicator
        color_dot = Gtk.Box()
        color_dot.set_size_request(10, 10)
        color_dot.set_valign(Gtk.Align.CENTER)
        color_dot.add_css_class("indicator-dot")
        
        display_color = topic[5] if len(topic) > 5 and topic[5] else None
        if len(topic) > 7 and topic[7] and str(topic[7]).strip():
            display_color = topic[7]
            
        if display_color and isinstance(display_color, str) and HEX_COLOR_REGEX.match(display_color.strip()):
            try:
                provider = Gtk.CssProvider()
                css = f".indicator-dot {{ background-color: {display_color}; border-radius: 50%; }}"
                provider.load_from_data(css.encode())
                color_dot.get_style_context().add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            except:
                pass
            
        self.add_prefix(color_dot)
        
        # Action buttons
        self.update_buttons()
    
    def update_buttons(self):
        """Update buttons based on revision status"""
        # Clear existing suffixes
        child = self.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            if hasattr(child, 'is_suffix_box'):
                self.remove(child)
            child = next_child
        
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        button_box.set_valign(Gtk.Align.CENTER)
        button_box.is_suffix_box = True
        
        # Details button (always visible)
        details_btn = Gtk.Button(icon_name="document-properties-symbolic")
        details_btn.set_tooltip_text("Ver Detalhes")
        details_btn.add_css_class("flat")
        details_btn.connect("clicked", self.on_details_clicked)
        button_box.append(details_btn)
        
        if self.revision[3] == 'studied':  # Completed
            # Show "Concluído" label and undo button
            completed_label = Gtk.Label(label="Concluído")
            completed_label.add_css_class("success")
            completed_label.add_css_class("dim-label")
            button_box.append(completed_label)
            
            undo_btn = Gtk.Button(icon_name="edit-undo-symbolic")
            undo_btn.set_tooltip_text("Desfazer Conclusão")
            undo_btn.add_css_class("flat")
            undo_btn.connect("clicked", self.on_undo_clicked)
            button_box.append(undo_btn)
        else:  # Pending
            # Play button - circular and prominent
            play_btn = Gtk.Button(icon_name="media-playback-start-symbolic")
            play_btn.set_tooltip_text("Iniciar Estudo")
            play_btn.add_css_class("circular")
            play_btn.add_css_class("suggested-action")
            play_btn.connect("clicked", self.on_play_clicked)
            button_box.append(play_btn)
            
            # Skip button - circular
            skip_btn = Gtk.Button(icon_name="media-skip-forward-symbolic")
            skip_btn.set_tooltip_text("Pular para Amanhã")
            skip_btn.add_css_class("circular")
            skip_btn.connect("clicked", self.on_skip_clicked)
            button_box.append(skip_btn)
            
            # Complete button - circular
            complete_btn = Gtk.Button(icon_name="object-select-symbolic")
            complete_btn.set_tooltip_text("Marcar como Concluído")
            complete_btn.add_css_class("circular")
            complete_btn.connect("clicked", self.on_complete_clicked)
            button_box.append(complete_btn)
        
        self.add_suffix(button_box)
    
    def on_details_clicked(self, btn):
        """Open topic details"""
        from .topic_details import TopicDetailsWindow
        win = TopicDetailsWindow(
            topic=self.topic, 
            logic=self.logic, 
            refresh_callback=self.refresh_callback,
            transient_for=self.get_native()
        )
        win.present()
    
    def on_play_clicked(self, btn):
        """Start study session"""
        window = self.get_native()
        if hasattr(window, 'start_timer'):
            window.start_timer(self.topic[0], self.topic[1])
    
    def on_skip_clicked(self, btn):
        """Skip to tomorrow"""
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        cursor = self.logic.db.conn.cursor()
        cursor.execute('UPDATE revisions SET scheduled_date = ? WHERE id = ?', 
                      (tomorrow, self.revision[0]))
        self.logic.db.conn.commit()
        
        if self.refresh_callback:
            self.refresh_callback()
    
    def on_complete_clicked(self, btn):
        """Mark as completed"""
        cursor = self.logic.db.conn.cursor()
        cursor.execute('UPDATE revisions SET status = ? WHERE id = ?', 
                      ('studied', self.revision[0]))
        self.logic.db.conn.commit()
        
        self.revision = list(self.revision)
        self.revision[3] = 'studied'
        self.revision = tuple(self.revision)
        
        self.update_buttons()
        
        if self.refresh_callback:
            self.refresh_callback()
    
    def on_undo_clicked(self, btn):
        """Undo completion"""
        cursor = self.logic.db.conn.cursor()
        cursor.execute('UPDATE revisions SET status = ? WHERE id = ?', 
                      ('pending', self.revision[0]))
        self.logic.db.conn.commit()
        
        self.revision = list(self.revision)
        self.revision[3] = 'pending'
        self.revision = tuple(self.revision)
        
        self.update_buttons()
        
        if self.refresh_callback:
            self.refresh_callback()

class TodayView(Gtk.Box):
    def __init__(self, refresh_callback=None, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0, **kwargs)
        self.logic = RevisionLogic()
        self.refresh_all = refresh_callback
        
        # Main scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.append(scrolled)
        
        # Main content box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        main_box.set_margin_top(24)
        main_box.set_margin_bottom(24)
        scrolled.set_child(main_box)
        
        # Stats Cards
        stats_clamp = Adw.Clamp()
        stats_clamp.set_maximum_size(800)
        main_box.append(stats_clamp)
        
        stats_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        stats_box.set_homogeneous(True)  # Equal width for all cards
        stats_box.set_margin_start(12)
        stats_box.set_margin_end(12)
        stats_clamp.set_child(stats_box)
        
        # Stat: Topics Today
        self.topics_stat = StatCard("Tópicos para Hoje", "view-list-bullet-symbolic")
        stats_box.append(self.topics_stat)
        
        # Stat: Time Today
        self.time_today_stat = StatCard("Tempo de Estudo Hoje", "preferences-system-time-symbolic")
        stats_box.append(self.time_today_stat)
        
        # Stat: Total Time
        self.time_total_stat = StatCard("Tempo de Estudo Total", "document-properties-symbolic")
        stats_box.append(self.time_total_stat)
        
        # Topics List
        list_clamp = Adw.Clamp()
        list_clamp.set_maximum_size(800)
        main_box.append(list_clamp)
        
        list_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        list_container.set_margin_start(12)
        list_container.set_margin_end(12)
        list_clamp.set_child(list_container)
        
        list_title = Gtk.Label(label="Revisões de Hoje")
        list_title.add_css_class("title-3")
        list_title.set_halign(Gtk.Align.START)
        list_container.append(list_title)
        
        self.list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        list_container.append(self.list_box)
        
        # Empty State
        self.empty_page = Adw.StatusPage()
        self.empty_page.set_title("Tudo em dia!")
        self.empty_page.set_description("Você não tem revisões pendentes para hoje.")
        self.empty_page.set_icon_name("emblem-ok-symbolic")
        list_container.append(self.empty_page)
        
        # Defer initial refresh to avoid initialization issues
        GLib.idle_add(self.safe_refresh_view)
    
    def safe_refresh_view(self):
        """Safely refresh view with error handling"""
        try:
            self.refresh_view()
        except Exception as e:
            print(f"Error refreshing TodayView: {e}")
            import traceback
            traceback.print_exc()
        return False

    def refresh_view(self):
        """Refresh all view components"""
        try:
            today_str = datetime.now().strftime('%Y-%m-%d')
            
            # Get today's study time
            today_seconds = self.logic.db.get_study_time_for_date(today_str)
            self.time_today_stat.set_value(format_time(today_seconds))
            
            # Get total study time (all time)
            cursor = self.logic.db.conn.cursor()
            cursor.execute('SELECT SUM(duration_seconds) FROM study_sessions')
            total_result = cursor.fetchone()[0]
            total_seconds = total_result if total_result else 0
            self.time_total_stat.set_value(format_time(total_seconds))
            
        except Exception as e:
            print(f"Error updating stats: {e}")
            self.time_today_stat.set_value("0min")
            self.time_total_stat.set_value("0min")
        
        # Update List - clear old items
        child = self.list_box.get_first_child()
        while child:
            self.list_box.remove(child)
            child = self.list_box.get_first_child()
        
        try:
            today_str = datetime.now().strftime('%Y-%m-%d')
            
            # Get all revisions for today (both pending and studied)
            cursor = self.logic.db.conn.cursor()
            cursor.execute('''
                SELECT r.*, t.title, t.area, t.color 
                FROM revisions r
                JOIN topics t ON r.topic_id = t.id
                WHERE r.scheduled_date = ?
                ORDER BY r.status ASC, t.title ASC
            ''', (today_str,))
            revisions = cursor.fetchall()
            
            # Update topics count
            self.topics_stat.set_value(str(len(revisions)))
            
            # Get full topic data for each revision
            for revision in revisions:
                topic_id = revision[1]
                topics = self.logic.db.get_topics()
                topic = next((t for t in topics if t[0] == topic_id), None)
                
                if topic:
                    row = TodayTopicRow(revision, topic, self.logic, self.refresh_all if self.refresh_all else self.refresh_view, self)
                    self.list_box.append(row)
            
            self.list_box.set_visible(len(revisions) > 0)
            self.empty_page.set_visible(len(revisions) == 0)
        except Exception as e:
            print(f"Error updating topics list: {e}")
            import traceback
            traceback.print_exc()
            self.list_box.set_visible(False)
            self.empty_page.set_visible(True)
            self.topics_stat.set_value("0")
