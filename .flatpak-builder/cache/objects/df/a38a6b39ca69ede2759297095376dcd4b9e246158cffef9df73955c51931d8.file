from gi.repository import Gtk, Adw, Pango

class WelcomeDialog(Adw.Window):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Bem-vindo")
        self.set_default_size(500, 400)
        self.set_modal(True)
        
        # Main Layout (Box)
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(main_box)
        
        # Carousel
        self.carousel = Adw.Carousel()
        self.carousel.set_vexpand(True)
        self.carousel.set_hexpand(True)
        self.carousel.set_spacing(24)
        main_box.append(self.carousel)
        
        # Slide 1: Welcome
        self.add_slide(
            "Bem-vindo ao Review", 
            "Seu assistente pessoal de estudos e revisão espaçada.",
            "review-app" 
        )
        
        # Slide 2: Organize
        self.add_slide(
            "Organize-se", 
            "Crie tópicos, categorize por áreas e use tags para manter tudo em ordem. Personalize com cores.",
            "document-open-recent-symbolic"
        )
        
        # Slide 3: Revise
        self.add_slide(
            "Revisão Espaçada", 
            "O método científico para não esquecer. O Review agenda automaticamente suas revisões para 7, 15 e 30 dias.",
            "document-revert-symbolic" # custom icon
        )

        # Slide 4: Track
        self.add_slide(
            "Acompanhe", 
            "Use o calendário para ver o que estudar a cada dia e receba notificações para não perder o ritmo.",
            "edit-find-symbolic"
        )
        
        # Indicators
        indicators = Adw.CarouselIndicatorDots()
        indicators.set_carousel(self.carousel)
        indicators.set_margin_bottom(24)
        main_box.append(indicators)
        
        # Footer Button
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        btn_box.set_halign(Gtk.Align.CENTER)
        btn_box.set_margin_bottom(24)
        main_box.append(btn_box)
        
        self.btn_start = Gtk.Button(label="Vamos lá")
        self.btn_start.add_css_class("pill")
        self.btn_start.add_css_class("suggested-action")
        self.btn_start.set_size_request(200, 50)
        self.btn_start.connect("clicked", lambda x: self.close())
        btn_box.append(self.btn_start)

    def add_slide(self, title_text, desc_text, icon_name):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_valign(Gtk.Align.CENTER)
        box.set_halign(Gtk.Align.CENTER)
        box.set_margin_start(48)
        box.set_margin_end(48)
        
        img = Gtk.Image.new_from_icon_name(icon_name)
        img.set_pixel_size(96)
        img.add_css_class("accent") 
        box.append(img)
        
        title = Gtk.Label(label=title_text)
        title.add_css_class("title-1")
        box.append(title)
        
        desc = Gtk.Label(label=desc_text)
        desc.set_wrap(True)
        desc.set_justify(Gtk.Justification.CENTER)
        desc.set_max_width_chars(40)
        desc.add_css_class("body")
        box.append(desc)
        
        self.carousel.append(box)

