import pygame
import sys
import re

GREEN = (35, 195, 24)
IMG_START_Y, IMG_END_Y = 22, 145
IMG_START_X, IMG_END_X = 9, 201
IMG_SIZE = (IMG_END_X - IMG_START_X, IMG_END_Y - IMG_START_Y)
PI_START = (45, 10)
CAR_NAME_START = 157
STATS_OFFSET_X = 20
STATS_OFFSET_Y = 30
STATS_START = 200
CAT_START = (92, 0)
CLASS_COLORS = {
    "D": (6, 146, 230),
    "C": (247, 203, 3),
    "B": (253, 118, 2),
    "A": (179, 5, 28),
    "S1": (171, 16, 227),
    "S2": (13, 48, 118)
}
RARITY_DETAILS = {
    "Common": ["CMMN", (122, 203, 73)],
    "Rare": ["RARE", (45, 205, 249)],
    "Epic": ["EPIC", (210, 71, 237)],
    "Legendary": ["LGND", (254, 167, 29)],
    "Forza Edition": ["FRZA", (137, 58, 196)]
}


class CarCard:
    def __init__(self, name, manufacturer, year, model, car_type, rarity, country, car_class, pi, speed, handling,
                 acceleration, launch, braking, offroad, avg_stat, drivetrain, load_image=False):
        self.name = name
        self.manufacturer = manufacturer
        self.year = year
        self.model = model
        self.car_type = car_type
        self.rarity = rarity
        self.country = country
        self.car_class = car_class
        self.pi = pi
        self.speed = speed
        self.handling = handling
        self.acceleration = acceleration
        self.launch = launch
        self.braking = braking
        self.offroad = offroad
        self.avg_stat = avg_stat
        self.drivetrain = drivetrain
        self.name_save = re.sub(r'[<>:"/\\|?*]', '', f"{name}.png")
        self.played = False
        # Creazione immagine solo se serve
        self.image = None
        self.font = None
        if load_image:
            self.image = pygame.image.load(f'images/cars/{self.name_save}').convert_alpha()
            self.font = pygame.font.Font("fonts/font.ttf", 24)

    def get_stat(self, stat):
        stats_dict = {
            "speed": self.speed,
            "acceleration": self.acceleration,
            "handling": self.handling,
            "braking": self.braking,
            "offroad": self.offroad,
            "launch": self.launch,
            "average stat": self.avg_stat,
            "pi": int(self.pi)
        }
        return stats_dict.get(stat.lower(), None)

    def played_card(self):
        self.played = True

    def calc_real_val(self, bonuses, val):
        final_val = val
        for bonus in bonuses:
            if bonus:
                final_val += val * (bonus / 100)
        return round(final_val, 1)

    def draw_card(self, screen, x, y, template, FONT_SMALL, FONT_MEDIUM, title_font, subtitle_font, scaled=False,
                  attr=None, val=None, extended=False, in_game=False, selected_loc=None):
        def wrap_text(text, font, max_width):
            words = text.split(' ')
            lines = []
            current_line = ''

            for word in words:
                test_line = current_line + ' ' + word if current_line else word
                if font.size(test_line)[0] <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word

            if current_line:
                lines.append(current_line)

            return lines

        text_color = (0, 0, 0)
        stat_color = (255, 255, 255)

        card_width, card_height = 200, 300

        # Immagine
        if scaled:
            card_bg = template[f"{self.car_class}_S"]
        elif extended:
            card_bg = template[f"{self.car_class}_E"]
        else:
            card_bg = template[self.car_class]
        if not extended:
            # Template
            screen.blit(card_bg, (x, y))

            # Immagine auto
            normal_image = pygame.transform.scale(self.image, IMG_SIZE)
            screen.blit(normal_image, (x + IMG_START_X, y + IMG_START_Y))

            # PI (in alto a sx)
            pi_text = FONT_SMALL.render(f"{int(self.pi)}", True, text_color)
            screen.blit(pi_text, (x + PI_START[0], y + PI_START[1]))

            # Nome auto (sotto immagine)
            name_text = FONT_MEDIUM.render(self.name, True, text_color)
            screen.blit(name_text, (x + (card_width - name_text.get_width()) // 2, y + CAR_NAME_START))

            # Categoria auto
            max_width = 100
            wrapped_cat_text = wrap_text(self.car_type, FONT_SMALL, max_width)
            for i, line in enumerate(wrapped_cat_text):
                line_surf = FONT_SMALL.render(line, True, stat_color)
                screen.blit(line_surf, (CAT_START[0] + x, CAT_START[1] + y + i * (FONT_SMALL.get_height())))

            # Stats (3 a sx e 3 a dx)
            stats_mapping = [
                ("SPD", self.speed, "speed"), ("ACC", self.acceleration, "acceleration"),
                ("HND", self.handling, "handling"), ("BRK", self.braking, "braking"),
                ("OFF", self.offroad, "offroad"), ("LAU", self.launch, "launch")
            ]
        if scaled:
            label = attr
            text = FONT_MEDIUM.render(f"{label}: {val}", True, stat_color)
            screen.blit(text, (x + (card_width - text.get_width()) // 2, y + STATS_START))
        elif extended:
            WIDTH, HEIGHT = screen.get_size()
            class_color = CLASS_COLORS[self.car_class]

            # 2. Pannello Carta Estesa
            CARD_W, CARD_H = 500, 300
            card_bg = pygame.transform.scale(card_bg, (CARD_W, CARD_H))
            if in_game:
                panel_x = (WIDTH - CARD_W) // 2
                panel_y = (HEIGHT - CARD_H)
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))  # Nero con opacità (180 su 255)
                screen.blit(overlay, (0, 0))
            else:
                panel_x = x
                panel_y = y
            # 2. Sfondo Pannello
            # Colore scuro metallico
            screen.blit(card_bg, (panel_x, panel_y))

            # 2. Immagine Auto (Nel riquadro bianco a sinistra)
            # Coordinate stimate per il box bianco nel template 500x300
            if hasattr(self, 'image'):
                img_w, img_h = 280, 155
                # Centriamo l'immagine mantenendo l'aspect ratio se possibile,
                # oppure scaliamo brutalmente:
                scaled_img = pygame.transform.scale(self.image, (img_w, img_h))
                screen.blit(scaled_img, (panel_x + 20, panel_y + 84))

            # 3. Classe (Lettera nel box in alto a sinistra)
            # Usiamo un font più grande per la lettera singola
            class_text = title_font.render(self.car_class, True, (255, 255, 255))
            # Centra nel quadratino colorato
            screen.blit(class_text, (panel_x + 24, panel_y + 25))

            # 4. Nome Auto (Intestazione in alto)
            # Combina Anno + Produttore + Modello
            upper_name = f"{self.year} {self.manufacturer}"
            lower_name = f"{self.model}"
            # Se è troppo lungo, va a capo
            upper_name_surf = FONT_MEDIUM.render(upper_name, True, class_color)
            screen.blit(upper_name_surf, (panel_x + 70, panel_y + 14))
            max_width = 250
            wrapped_cat_text = wrap_text(lower_name, FONT_MEDIUM, max_width)
            for i, line in enumerate(wrapped_cat_text):
                line_surf = FONT_MEDIUM.render(line, True, stat_color)
                screen.blit(line_surf, (
                    panel_x + 70, panel_y + 15 + upper_name_surf.get_height() + i * (FONT_MEDIUM.get_height())))

            # 5. Metadati (Colonna Destra in alto)
            # Il template ha già le scritte "RARITY", "COUNTRY", "DRIVE".
            # Noi scriviamo solo i valori sotto o a fianco.
            # Coordinate allineate alle etichette del template:
            RARITY_CX = panel_x + 343
            COUNTRY_CX = panel_x + 404
            DRIVE_CX = panel_x + 466

            META_Y = panel_y + 78

            def draw_centered(surf, center_x, y):
                rect = surf.get_rect(center=(center_x, y))
                return rect

            # Rarity
            rarity_val = FONT_SMALL.render(str(RARITY_DETAILS[self.rarity][0]), True, (255, 255, 255))
            rarity_bg = pygame.Surface((rarity_val.get_width() + 2, rarity_val.get_height() + 2), pygame.SRCALPHA)
            rarity_bg.fill(RARITY_DETAILS[self.rarity][1])
            screen.blit(rarity_bg, draw_centered(rarity_bg, RARITY_CX, META_Y))
            screen.blit(rarity_val, draw_centered(rarity_val, RARITY_CX, META_Y))

            # Country
            country_val = FONT_SMALL.render(str(self.country.upper()), True, (255, 255, 255))
            screen.blit(country_val, draw_centered(country_val, COUNTRY_CX, META_Y))

            # Drivetrain
            drive_val = FONT_SMALL.render(str(self.drivetrain.upper()), True, (255, 255, 255))
            screen.blit(drive_val, draw_centered(drive_val, DRIVE_CX, META_Y))

            # 6. Statistiche (Colonna Destra - Barre)
            # Le coordinate y devono scendere per allinearsi ai box del template
            stats_start_x = panel_x + 371  # Spostato a destra per lasciare spazio alle scritte "SPEED" ecc del template
            stats_start_y = panel_y + 98
            bar_w = 87  # Larghezza barra
            bar_h = 13.5  # Altezza barra
            gap = 23.2  # Spazio verticale tra una stat e l'altra

            stats_data_ext = [
                ("speed", self.speed), ("handling", self.handling),
                ("acceleration", self.acceleration), ("launch", self.launch),
                ("braking", self.braking), ("offroad", self.offroad)
            ]
            upg = False
            if selected_loc is not None:
                attribute = selected_loc.stat
                bonuses = selected_loc.check_criteria(self)
                if any(bonuses):
                    upg = True
            for i, (stat_name, val) in enumerate(stats_data_ext):
                stat_clr = (255, 255, 255)
                current_y = stats_start_y + (i * gap)
                if selected_loc is not None:
                    if attribute == stat_name and upg:
                        upgraded_val = self.calc_real_val(bonuses, val)
                        val = upgraded_val
                        stat_clr = GREEN
                # Disegno barra valore (Bianca)
                fill_width = (min(val, 10) / 10.0) * bar_w
                pygame.draw.rect(screen, class_color, (stats_start_x, current_y, fill_width, bar_h))
                # Valore numerico a destra della barra

                val_text = FONT_SMALL.render(str(val), True, stat_clr)
                screen.blit(val_text, (stats_start_x + bar_w + 5, current_y - 2))

            # 7. PI (Striscia in basso)
            type_text = title_font.render(str(int(self.pi)), True, (255, 255, 255))
            screen.blit(type_text, (panel_x + 20, panel_y + 252))

            # 8. Categoria Auto (Striscia in basso)
            type_text = title_font.render(self.car_type.upper(), True, (255, 255, 255))
            screen.blit(type_text, (panel_x + CARD_W - type_text.get_width() - 25, panel_y + 252))
        else:
            upg = False
            if selected_loc is not None:
                attribute = selected_loc.stat
                bonuses = selected_loc.check_criteria(self)
                if any(bonuses):
                    upg = True
            for i in range(6):
                label, value, stat_key = stats_mapping[i]

                # Colore default
                current_stat_color = stat_color

                # Se la location richiede questa stat -> VERDE
                if selected_loc:
                    if attribute == stat_key and upg:
                        upg_val = self.calc_real_val(bonuses, value)
                        value = upg_val
                        current_stat_color = GREEN

                text = FONT_SMALL.render(f"{label}: {value}", True, current_stat_color)

                # Coordinate (logica originale divisa in 2 colonne)
                if i < 3:
                    screen.blit(text, (x + STATS_OFFSET_X, y + STATS_START + i * STATS_OFFSET_Y))
                else:
                    screen.blit(text,
                                (x + card_width // 2 + STATS_OFFSET_X, y + STATS_START + (i - 3) * STATS_OFFSET_Y))
            if self.played:
                card_rect = pygame.Rect(x, y, card_width, card_height)
                overlay = pygame.Surface((card_width, card_height))
                overlay.set_alpha(150)  # trasparenza
                overlay.fill((128, 128, 128))  # colore grigio
                screen.blit(overlay, card_rect)
