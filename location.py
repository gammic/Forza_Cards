import random
import pygame

BLACK = (0, 0, 0)
BONUS_TEXT_Y = 225
GREEN = (35, 195, 24)
LOC_SIZE = [300, 274]


class Location:
    def __init__(self, name, stat, load_image=False):
        self.val = None
        self.name = name
        self.stat = stat
        if load_image:
            self.font = pygame.font.Font("fonts/font.ttf", 16)
            self.image = pygame.image.load(f"images/loc/{self.name}.png")
            self.font_stat = pygame.font.Font("fonts/font.ttf", 24)
        self.chosen = False
        self.bonus_cat = None  # Categoria bonus e percentuale
        self.bonus_val = 0
        self.bonus_ass = False
        self.selected = False

    def draw_location(self, screen, x, y):
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

        screen.blit(self.image, (x, y))
        bonus_cat, bonus_val = self.bonus_cat, self.bonus_val
        if bonus_cat is None:
            bonus_text = self.font.render(f"No active bonus", True, BLACK)
            screen.blit(bonus_text, (150 - bonus_text.get_width() // 2 + x, y + BONUS_TEXT_Y))
        else:
            bonus_text = ""
            for bonus in bonus_cat:
                bonus_text += f"{bonus}, "
            bonus_text = bonus_text[:-2]
            max_width = 272
            wrapped_cat_text = wrap_text(bonus_text, self.font, max_width)
            for i, line in enumerate(wrapped_cat_text):
                line_surf = self.font.render(line, True, BLACK)
                line_start_x = 150 - line_surf.get_width() // 2 + x
                screen.blit(line_surf, (line_start_x, BONUS_TEXT_Y + y + i * (self.font.get_height() + 2)))

        if self.chosen:
            loc_rect = pygame.Rect(x, y, LOC_SIZE[0], LOC_SIZE[1])
            overlay = pygame.Surface((LOC_SIZE[0], LOC_SIZE[1]))
            overlay.set_alpha(150)  # trasparenza
            overlay.fill((128, 128, 128))  # colore grigio
            screen.blit(overlay, loc_rect)
            val_text = self.font_stat.render(str(self.val), True, GREEN)
            screen.blit(val_text, (x + 10, y + 173))
        if self.bonus_val > 0:
            bonus_perc_text = self.font_stat.render(f"+{self.bonus_val}%", True, GREEN)
            screen.blit(bonus_perc_text, (x + LOC_SIZE[0] - bonus_perc_text.get_width() - 5, y + 173))

        if self.selected:
            loc_rect = pygame.Rect(x, y, LOC_SIZE[0], LOC_SIZE[1])
            pygame.draw.rect(screen, GREEN, loc_rect, 10)

    def chosen_location(self, val):
        self.chosen = True
        self.val = val

    def selected_location(self):
        self.selected = True

    def reset_location(self):
        self.chosen = False
        self.bonus_val = 0
        self.bonus_ass = False
        self.bonus_ass = False
        self.val = None
        self.selected = False

    def check_criteria(self, card):
        """Controlla se la carta soddisfa i criteri dei bonus della location."""

        val = self.bonus_val
        cats = self.bonus_cat
        bonus_list = [card.car_type, card.rarity, card.country, card.drivetrain]
        matches = [False for _ in bonus_list]
        if not self.bonus_val:
            return matches

        for p, bonus in enumerate(cats):
            if bonus == bonus_list[p]:
                matches[p] = val

        return matches

    def pick_bonus(self, turn, categories):
        if not self.bonus_ass:
            bonus_car_type = random.choices(categories["car_types"][0], weights=categories["car_types"][1], k=1)[0]
            bonus_rarity = random.choices(categories["rarities"][0], weights=categories["rarities"][1])[0]
            bonus_nation = random.choices(categories["nations"][0], weights=categories["nations"][1])[0]
            bonus_drive = random.choices(categories["drives"][0], weights=categories["drives"][1])[0]

            if turn == 2 or turn == 3:
                self.bonus_val = 10
                self.bonus_cat = [bonus_car_type, bonus_rarity, bonus_nation, bonus_drive]
            elif turn >= 4:
                self.bonus_val = 20
                self.bonus_cat = [bonus_car_type, bonus_rarity, bonus_nation, bonus_drive]
            self.bonus_ass = True
        return self.bonus_cat, self.bonus_val
