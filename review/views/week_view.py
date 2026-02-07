from gi.repository import Gtk, Adw, GObject
from datetime import datetime, timedelta
from ..models import RevisionLogic

class WeekDayCell(Gtk.Button):
    """Simplified day cell for week view - no popover, just selection"""
    def __init__(self, day, month, year, revisions, **kwargs):
        super().__init__(**kwargs)
        self.day = day
        self.month = month
        self.year = year
        self.revisions = revisions
        
        # Make cell responsive - no fixed size
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.add_css_class("flat")
        self.add_css_class("day-cell")
        
        # Content Box
        self.content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.content.set_margin_top(6)
        self.content.set_margin_bottom(6)
        self.content.set_margin_start(8)
        self.content.set_margin_end(8)
        self.set_child(self.content)
        
        # Day Number Header
        self.header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        self.header.append(spacer)
        
        day_label = Gtk.Label(label=str(day))
        day_label.add_css_class("title-4")
        if day == datetime.now().day and month == datetime.now().month and year == datetime.now().year:
            day_label.add_css_class("accent")
        
        self.header.append(day_label)
        self.content.append(self.header)
        
        # Revision Indicators Container
        self.indicators = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        self.indicators.set_valign(Gtk.Align.START)
        self.content.append(self.indicators)
        
        self.add_indicators()
    
    def add_indicators(self):
        # Show max 2 indicators to keep cells compact
        for rev in self.revisions[:2]:
            topic_title = rev[5]
            indicator = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
            indicator.add_css_class("revision-indicator")
            
            dot = Gtk.Box()
            dot.set_size_request(4, 4)
            dot.set_valign(Gtk.Align.CENTER)
            dot.add_css_class("indicator-dot")
            
            # Apply color if available (index 7 from query)
            if len(rev) > 7 and rev[7]:
                col = rev[7]
                if isinstance(col, str) and HEX_COLOR_REGEX.match(col.strip()):
                    try:
                        provider = Gtk.CssProvider()
                        css = f"* {{ background-color: {col}; border-radius: 50%; }}"
                        provider.load_from_data(css.encode())
                        context = dot.get_style_context()
                        context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
                    except: pass
                
            indicator.append(dot)
            
            label = Gtk.Label(label=topic_title)
            label.set_ellipsize(3)
            label.set_max_width_chars(15)
            label.set_halign(Gtk.Align.START)
            label.add_css_class("caption")
            if rev[3] == 'studied':
                label.add_css_class("studied-text")
            
            indicator.append(label)
            
            self.indicators.append(indicator)
            
        if len(self.revisions) > 2:
            more_label = Gtk.Label(label=f"+{len(self.revisions) - 2} mais")
            more_label.add_css_class("caption")
            more_label.add_css_class("dim-label")
            self.indicators.append(more_label)



class WeekView(Gtk.Box):
    def __init__(self, refresh_callback=None, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, **kwargs)
        self.refresh_all = refresh_callback
        self.logic = RevisionLogic()
        
        # Current week start (Monday)
        today = datetime.now()
        self.current_week_start = today - timedelta(days=today.weekday())
        self.selected_date = None
        
        # Header with navigation
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        header.set_margin_top(12)
        header.set_margin_bottom(8)
        header.set_margin_start(12)
        header.set_margin_end(12)
        self.append(header)
        
        # Previous week button
        prev_btn = Gtk.Button(icon_name="go-previous-symbolic")
        prev_btn.add_css_class("flat")
        prev_btn.connect("clicked", self.on_prev_week)
        header.append(prev_btn)
        
        # Week label
        self.week_label = Gtk.Label()
        self.week_label.add_css_class("title-3")
        self.week_label.set_hexpand(True)
        header.append(self.week_label)
        
        # Today button
        today_btn = Gtk.Button(label="Hoje")
        today_btn.add_css_class("suggested-action")
        today_btn.connect("clicked", self.on_today_clicked)
        header.append(today_btn)
        
        # Next week button
        next_btn = Gtk.Button(icon_name="go-next-symbolic")
        next_btn.add_css_class("flat")
        next_btn.connect("clicked", self.on_next_week)
        header.append(next_btn)
        
        # Main content area with paned
        paned = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL)
        paned.set_vexpand(True)
        paned.set_position(280)  # Set initial position for week grid
        paned.set_shrink_start_child(False)
        paned.set_resize_start_child(False)
        self.append(paned)
        
        # Top: Week grid (no scrolled window)
        top_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        top_box.set_vexpand(False)
        paned.set_start_child(top_box)
        
        clamp_top = Adw.Clamp()
        clamp_top.set_maximum_size(1200)
        top_box.append(clamp_top)
        
        self.week_grid = Gtk.Grid()
        self.week_grid.set_column_homogeneous(True)
        self.week_grid.set_row_spacing(8)
        self.week_grid.set_column_spacing(8)
        self.week_grid.set_margin_top(8)
        self.week_grid.set_margin_bottom(12)
        self.week_grid.set_margin_start(12)
        self.week_grid.set_margin_end(12)
        clamp_top.set_child(self.week_grid)
        
        # Bottom: Revisions list with scrolling
        scrolled_bottom = Gtk.ScrolledWindow()
        scrolled_bottom.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_bottom.set_vexpand(True)
        paned.set_end_child(scrolled_bottom)
        
        clamp_bottom = Adw.Clamp()
        clamp_bottom.set_maximum_size(900)
        scrolled_bottom.set_child(clamp_bottom)
        
        self.revisions_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.revisions_box.set_margin_top(12)
        self.revisions_box.set_margin_bottom(12)
        self.revisions_box.set_margin_start(12)
        self.revisions_box.set_margin_end(12)
        clamp_bottom.set_child(self.revisions_box)
        
        # Empty state
        self.empty_state = Adw.StatusPage()
        self.empty_state.set_title("Selecione um Dia")
        self.empty_state.set_description("Clique em um dia acima para ver as revisões agendadas")
        self.empty_state.set_icon_name("calendar-symbolic")
        self.revisions_box.append(self.empty_state)
        
        self.build_week()

    
    def build_week(self):
        # Clear existing grid
        while True:
            child = self.week_grid.get_first_child()
            if child is None:
                break
            self.week_grid.remove(child)
        
        # Update week label
        week_end = self.current_week_start + timedelta(days=6)
        if self.current_week_start.month == week_end.month:
            week_str = f"{self.current_week_start.day} - {week_end.day} de {self.current_week_start.strftime('%B %Y').capitalize()}"
        else:
            week_str = f"{self.current_week_start.strftime('%d %b')} - {week_end.strftime('%d %b %Y')}"
        self.week_label.set_text(week_str)
        
        # Day names header
        day_names = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
        for col, day_name in enumerate(day_names):
            label = Gtk.Label(label=day_name)
            label.add_css_class("caption-heading")
            label.add_css_class("dim-label")
            label.set_halign(Gtk.Align.CENTER)
            label.set_margin_bottom(4)
            self.week_grid.attach(label, col, 0, 1, 1)
        
        # Week days
        for col in range(7):
            day_date = self.current_week_start + timedelta(days=col)
            day = day_date.day
            month = day_date.month
            year = day_date.year
            
            # Get revisions for this day
            date_str = day_date.strftime('%Y-%m-%d')
            revisions = self.logic.get_upcoming_revisions(date_str)
            
            # Create day cell
            cell = WeekDayCell(day, month, year, revisions)
            cell.connect("clicked", self.on_day_selected, date_str, revisions)
            
            self.week_grid.attach(cell, col, 1, 1, 1)
    
    def on_day_selected(self, btn, date_str, revisions):
        """Show revisions for selected day in bottom panel"""
        self.selected_date = date_str
        
        # Clear revisions box
        while True:
            child = self.revisions_box.get_first_child()
            if child is None:
                break
            self.revisions_box.remove(child)
        
        if not revisions:
            # Show empty state
            empty = Adw.StatusPage()
            empty.set_title("Nenhuma Revisão")
            empty.set_description(f"Não há revisões agendadas para {self.format_date(date_str)}")
            empty.set_icon_name("calendar-symbolic")
            empty.set_vexpand(True)
            self.revisions_box.append(empty)
            return
        
        # Header
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        header_label = Gtk.Label(label=f"Revisões para {self.format_date(date_str)}")
        header_label.add_css_class("title-4")
        header_label.set_halign(Gtk.Align.START)
        header_label.set_margin_bottom(8)
        self.revisions_box.append(header_label)
        
        # List of revisions
        list_box = Gtk.ListBox()
        list_box.add_css_class("boxed-list")
        list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        self.revisions_box.append(list_box)

        
        for rev in revisions:
            rev_id, topic_id, scheduled_date, status, interval, topic_title, area, color = rev
            
            row = Adw.ActionRow()
            row.set_title(topic_title)
            row.set_subtitle(f"{area} • Intervalo: {interval} dias")
            
            # Color indicator
            if color:
                dot = Gtk.Box()
                dot.set_size_request(12, 12)
                dot.set_valign(Gtk.Align.CENTER)
                provider = Gtk.CssProvider()
                css = f"* {{ background-color: {color}; border-radius: 50%; }}"
                provider.load_from_data(css.encode())
                context = dot.get_style_context()
                context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
                row.add_prefix(dot)
            
            # Action buttons
            btn_box = Gtk.Box(spacing=6)
            
            if status == 'pending':
                # Study button
                study_btn = Gtk.Button(icon_name="media-playback-start-symbolic")
                study_btn.set_tooltip_text("Iniciar Estudo")
                study_btn.add_css_class("flat")
                study_btn.connect("clicked", self.on_start_study, topic_id, topic_title)
                btn_box.append(study_btn)
                
                # Skip button
                skip_btn = Gtk.Button(icon_name="media-skip-forward-symbolic")
                skip_btn.set_tooltip_text("Pular para amanhã")
                skip_btn.add_css_class("flat")
                skip_btn.add_css_class("error")
                skip_btn.connect("clicked", self.on_skip_topic, rev_id, topic_id)
                btn_box.append(skip_btn)

                # Mark as studied button
                check_btn = Gtk.Button(icon_name="object-select-symbolic")
                check_btn.set_tooltip_text("Marcar como Concluído")
                check_btn.add_css_class("flat")
                check_btn.connect("clicked", self.on_mark_studied, rev_id)
                btn_box.append(check_btn)
            else:
                # Status label
                status_label = Gtk.Label(label="✓ Concluído")
                status_label.add_css_class("success")
                status_label.add_css_class("dim-label")
                btn_box.append(status_label)

                # Undo button
                undo_btn = Gtk.Button(icon_name="edit-undo-symbolic")
                undo_btn.set_tooltip_text("Desfazer Conclusão")
                undo_btn.add_css_class("flat")
                undo_btn.connect("clicked", self.on_undo_completion, rev_id)
                btn_box.append(undo_btn)
            
            row.add_suffix(btn_box)
            list_box.append(row)
    
    def on_undo_completion(self, btn, rev_id):
        """Revert revision to pending status"""
        self.logic.mark_as_pending(rev_id)
        if self.refresh_all:
            self.refresh_all()
        else:
            self.refresh_calendar()
    
    def on_skip_topic(self, btn, rev_id, topic_id):
        """Skip revision and move to next day"""
        self.logic.mark_as_not_studied(rev_id, topic_id)
        if self.refresh_all:
            self.refresh_all()
        else:
            self.refresh_calendar()
    
    def format_date(self, date_str):

        """Format date string to readable format"""
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%d de %B de %Y').capitalize()
    
    def on_start_study(self, btn, topic_id, topic_title):
        """Start timer for topic"""
        window = self.get_native()
        if hasattr(window, 'start_timer'):
            window.start_timer(topic_id, topic_title)
    
    def on_mark_studied(self, btn, rev_id):
        """Mark revision as studied"""
        self.logic.mark_as_studied(rev_id)
        # Refresh current view and parent
        if self.refresh_all:
            self.refresh_all()
        else:
            self.refresh_calendar()
    
    def on_prev_week(self, btn):
        self.current_week_start -= timedelta(days=7)
        self.selected_date = None
        self.build_week()
        self.clear_revisions_panel()
    
    def on_next_week(self, btn):
        self.current_week_start += timedelta(days=7)
        self.selected_date = None
        self.build_week()
        self.clear_revisions_panel()
    
    def on_today_clicked(self, btn):
        today = datetime.now()
        self.current_week_start = today - timedelta(days=today.weekday())
        self.selected_date = None
        self.build_week()
        self.clear_revisions_panel()
    
    def clear_revisions_panel(self):
        """Clear and show empty state"""
        while True:
            child = self.revisions_box.get_first_child()
            if child is None:
                break
            self.revisions_box.remove(child)
        
        empty = Adw.StatusPage()
        empty.set_title("Selecione um Dia")
        empty.set_description("Clique em um dia acima para ver as revisões agendadas")
        empty.set_icon_name("calendar-symbolic")
        self.revisions_box.append(empty)
    
    def refresh_calendar(self):
        """Refresh the current week view"""
        self.build_week()
        # Refresh selected day if any
        if self.selected_date:
            revisions = self.logic.get_upcoming_revisions(self.selected_date)
            self.on_day_selected(None, self.selected_date, revisions)
