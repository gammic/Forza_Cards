import sys
import time

import Pyro5.api
import Pyro5.errors

import pygame
import ctypes
import platform

from location import Location
from carcard import CarCard

# Inizializza PyGame
pygame.init()
clock = pygame.time.Clock()

# Costanti
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (35, 195, 24)
YELLOW = (255, 255, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (240, 240, 240)
BLUE = (100, 149, 237)
LIGHT_BLUE = (173, 216, 230)
FORZA_COLOR = (248, 76, 100)
LIGHT_FORZA_COLOR = (255, 112, 82)
TEXT_POS = (300, 200)

LOCATIONS_POS = (300, 200, 320)
CARD_SIZE = (200, 300)
CARDS_OFFSET = (100, 300)

# Finestra

pygame.display.set_caption("ForzaCards")
info = pygame.display.Info()
SCREEN_SIZE = (1536, 793)
WIDTH, HEIGHT = info.current_w, info.current_h
system = platform.system()

if system == "Windows":
    # --- Metodo nativo Windows ---
    screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
    hwnd = pygame.display.get_wm_info()['window']
    ctypes.windll.user32.ShowWindow(hwnd, 3)  # SW_MAXIMIZE = 3
else:
    # --- Metodo cross-platform ---
    screen = pygame.display.set_mode((WIDTH, HEIGHT - 80), pygame.RESIZABLE)
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h

# Font
FONT_SMALL = pygame.font.Font("fonts/font.ttf", 14)
FONT_MEDIUM = pygame.font.Font("fonts/font.ttf", 17)
FONT_BONUS = pygame.font.Font("fonts/font.ttf", 16)
FONT_LARGE = pygame.font.Font("fonts/font.ttf", 24)
FONT_HUGE = pygame.font.Font("fonts/font.ttf", 30)
FONT_TITLE = pygame.font.Font("fonts/font.ttf", 40)
FONT_BUTTONS = pygame.font.Font("fonts/font.ttf", 48)

# Locations

locations = [
    Location("quarter_mile", "launch"),
    Location("half_mile", "acceleration"),
    Location("circuit_track", "handling"),
    Location("highway", "speed"),
    Location("offroad_trail", "offroad"),
    Location("brake_test", "braking")
]

# Inizializzazioni
BONUS_TEXT_Y = 210

# Energia
energies = [1330, 1875, 2150, 2440, 2680]
partial_energy = energies[0]

# Template carte
frame_d_img = pygame.image.load("images/cards/d_card.png").convert_alpha()
frame_c_img = pygame.image.load("images/cards/c_card.png").convert_alpha()
frame_b_img = pygame.image.load("images/cards/b_card.png").convert_alpha()
frame_a_img = pygame.image.load("images/cards/a_card.png").convert_alpha()
frame_s1_img = pygame.image.load("images/cards/s1_card.png").convert_alpha()
frame_s2_img = pygame.image.load("images/cards/s2_card.png").convert_alpha()
frame_d_img_small = pygame.image.load("images/cards/d_card_small.png").convert_alpha()
frame_c_img_small = pygame.image.load("images/cards/c_card_small.png").convert_alpha()
frame_b_img_small = pygame.image.load("images/cards/b_card_small.png").convert_alpha()
frame_a_img_small = pygame.image.load("images/cards/a_card_small.png").convert_alpha()
frame_s1_img_small = pygame.image.load("images/cards/s1_card_small.png").convert_alpha()
frame_s2_img_small = pygame.image.load("images/cards/s2_card_small.png").convert_alpha()
frame_d_img_ext = pygame.image.load("images/cards/d_card_e.png").convert_alpha()
frame_c_img_ext = pygame.image.load("images/cards/c_card_e.png").convert_alpha()
frame_b_img_ext = pygame.image.load("images/cards/b_card_e.png").convert_alpha()
frame_a_img_ext = pygame.image.load("images/cards/a_card_e.png").convert_alpha()
frame_s1_img_ext = pygame.image.load("images/cards/s1_card_e.png").convert_alpha()
frame_s2_img_ext = pygame.image.load("images/cards/s2_card_e.png").convert_alpha()

# Immagini varie
bg_image = pygame.image.load("images/board.png").convert()
bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
res_image = pygame.image.load("images/res.png").convert_alpha()
win_image = pygame.image.load("images/win_mess.png").convert_alpha()
lose_image = pygame.image.load("images/lose_mess.png").convert_alpha()
logo_image = pygame.image.load("images/logo.png").convert_alpha()
main_menu_image = pygame.image.load("images/main_menu_bg.jpg").convert_alpha()
main_menu_image = pygame.transform.scale(main_menu_image, (WIDTH, HEIGHT))
endgame_image = pygame.image.load("images/endgame_bg.png").convert_alpha()
endgame_image = pygame.transform.scale(endgame_image, (WIDTH, HEIGHT))

# Posizioni
RES_IMAGE_POS = ((WIDTH - res_image.get_width()) // 2, (HEIGHT - res_image.get_height()) // 2)
RESULTS_STARTING_POS = (RES_IMAGE_POS[0] + 95, RES_IMAGE_POS[1] + 5)

# Template HP
ai_hp_image = pygame.image.load("images/hp/hp_template.png").convert_alpha()
player_hp_image = pygame.image.load("images/hp/hp_rot_template.png").convert_alpha()
p2_lancetta = pygame.image.load("images/hp/lancetta.png").convert_alpha()
player_lancetta = pygame.image.load("images/hp/lancetta_rot.png").convert_alpha()
MAX_HP = 10
MIN_ANGLE = 0
MAX_ANGLE = 241
CENTRO_REV = (102, 198)

# Immagini carte
frame_images = {
    'D': frame_d_img,
    'C': frame_c_img,
    'B': frame_b_img,
    'A': frame_a_img,
    'S1': frame_s1_img,
    'S2': frame_s2_img,
    'D_S': frame_d_img_small,
    'C_S': frame_c_img_small,
    'B_S': frame_b_img_small,
    'A_S': frame_a_img_small,
    'S1_S': frame_s1_img_small,
    'S2_S': frame_s2_img_small,
    'D_E': frame_d_img_ext,
    'C_E': frame_c_img_ext,
    'B_E': frame_b_img_ext,
    'A_E': frame_a_img_ext,
    'S1_E': frame_s1_img_ext,
    'S2_E': frame_s2_img_ext,
}


def draw_locations(turn, current_locations, cat, phase, selected_location=None):
    if phase == "card_sel" or phase == "end_turn":
        for i, location in enumerate(current_locations):
            if location.name == selected_location:
                location.selected_location()
            location.draw_location(screen, LOCATIONS_POS[0] + i * LOCATIONS_POS[2], LOCATIONS_POS[1])


def draw_hand(hand, loc=None):
    x_offset = CARDS_OFFSET[0]
    for card in hand:
        card.draw_card(screen, x_offset, HEIGHT - 300, frame_images, FONT_SMALL, FONT_MEDIUM, FONT_LARGE, FONT_TITLE,
                       scaled=False, selected_loc=loc)
        x_offset += CARDS_OFFSET[1]


def draw_info(turn, player1, player2, phase, not_play_msg=None, results=None):
    """
    results = {"location": location_name, "played_cards": {"pl_name": card}, "winner" : winner_name, "damage" : damage_value}
    """
    global partial_energy, player_name, opponent_name
    p1_energy = player1["energy"]
    p1_hp = player1["hp"]
    p2_hp = player2["hp"]
    # Disegna energia, HP e turno oppure schermata finale
    if phase == "card_sel":
        screen.blit(bg_image, (0, 0))
        logo_image_main_game = pygame.transform.scale(logo_image, (250, 83))
        screen.blit(logo_image_main_game, (300, 0))
    if phase == "end_turn":
        screen.blit(bg_image, (0, 0))
        logo_image_main_game = pygame.transform.scale(logo_image, (250, 83))
        screen.blit(logo_image_main_game, (300, 0))
        awaiting_turn_text = FONT_HUGE.render("Waiting for other player", True, FORZA_COLOR)
        screen.blit(awaiting_turn_text, ((WIDTH - awaiting_turn_text.get_width()) // 2, 100))
    if phase == "dmg_eval" and results is not None:
        screen.blit(bg_image, (0, 0))
        logo_image_main_game = pygame.transform.scale(logo_image, (250, 83))
        screen.blit(logo_image_main_game, (300, 0))
        # Mostra sfondo risultati
        screen.blit(res_image, RES_IMAGE_POS)
        # Mostra risultati a schermo
        for i, res in enumerate(results):
            y_offset = i * 30
            loc_name, attr = res["location"]
            winner = res["winner"]
            dmg = res["damage"]
            vals = res["vals"]
            if winner == player_name:
                dmg_pos = (RESULTS_STARTING_POS[0] + 750, RESULTS_STARTING_POS[1] + 100 + y_offset)
            elif winner == opponent_name:
                dmg_pos = (RESULTS_STARTING_POS[0] - 150, RESULTS_STARTING_POS[1] + 100 + y_offset)
            else:
                dmg_pos = (RESULTS_STARTING_POS[0] + 300, RESULTS_STARTING_POS[1] + 100 + y_offset)
            dmg_text = FONT_HUGE.render(f"- {dmg}", True, RED)
            screen.blit(dmg_text, dmg_pos)
            p1_card = rebuild_hand(res["played_cards"][player_name])[0]
            p2_card = rebuild_hand(res["played_cards"][opponent_name])[0]
            p1_card.draw_card(screen, RESULTS_STARTING_POS[0], RESULTS_STARTING_POS[1], frame_images,
                              FONT_SMALL, FONT_MEDIUM, FONT_LARGE, FONT_TITLE, scaled=True,
                              val=vals[player_name], attr=attr)
            p1_text = FONT_HUGE.render(str(player_name), True, WHITE)
            screen.blit(p1_text,
                        (RESULTS_STARTING_POS[0] + 100 - (p1_text.get_width() // 2), RESULTS_STARTING_POS[1] + 300))
            p2_card.draw_card(screen, RESULTS_STARTING_POS[0] + 485, RESULTS_STARTING_POS[1],
                              frame_images, FONT_SMALL, FONT_MEDIUM, FONT_LARGE, FONT_TITLE, scaled=True,
                              attr=attr, val=vals[opponent_name])
            p2_text = FONT_HUGE.render(str(opponent_name), True, WHITE)
            screen.blit(p2_text, (
                RESULTS_STARTING_POS[0] + 485 + 100 - (p2_text.get_width() // 2),
                RESULTS_STARTING_POS[1] + 300))
            pygame.display.flip()
            wait_time = pygame.time.get_ticks() + 2000
            pygame.display.update()
            while pygame.time.get_ticks() < wait_time:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()
    # Energia
    p1_energy_text = FONT_LARGE.render(f"PLAYER ENERGY: {int(partial_energy)}", True, WHITE)
    screen.blit(p1_energy_text, ((WIDTH - p1_energy_text.get_width()) // 2, 20))
    # HP
    # PLAYER A SX
    screen.blit(ai_hp_image, (0, 0))
    player_hp_angle = hp_to_angle(p1_hp)
    player_lanc_rot = pygame.transform.rotate(p2_lancetta, player_hp_angle)
    player_lanc_rect = player_lanc_rot.get_rect(
        center=CENTRO_REV)
    screen.blit(player_lanc_rot, player_lanc_rect)
    p1_hp_text = FONT_LARGE.render(f"{p1_hp} HP", True, RED)
    screen.blit(p1_hp_text, (60, 120))
    # OPPONENT A DX
    screen.blit(player_hp_image, (WIDTH - player_hp_image.get_width(), 0))
    p2_hp_angle = hp_to_angle(p2_hp)
    p2_lanc_rot = pygame.transform.rotate(player_lancetta, p2_hp_angle)
    p2_lanc_rect = p2_lanc_rot.get_rect(center=(WIDTH - CENTRO_REV[0], CENTRO_REV[1]))
    screen.blit(p2_lanc_rot, p2_lanc_rect)
    p2_hp_text = FONT_LARGE.render(f"{p2_hp} HP", True, RED)
    screen.blit(p2_hp_text, ((WIDTH - player_hp_image.get_width()) + 150, 120))
    # Turno
    turn_text = FONT_HUGE.render(f"TURN {turn}", True, WHITE)
    screen.blit(turn_text, ((WIDTH - turn_text.get_width()) // 2, 60))
    # Nomi
    player2_text = FONT_HUGE.render(f"{str(opponent_name).upper()}", True, WHITE)
    screen.blit(player2_text, (WIDTH - player2_text.get_width() - 20, ai_hp_image.get_height() + 20))
    player1_text = FONT_HUGE.render(f"{str(player_name).upper()}", True, WHITE)
    screen.blit(player1_text, (20, player_hp_image.get_height() + 20))
    # Avviso unplayable card
    unpl_pos = (950, 20)
    if not_play_msg is not None:
        if any(not_play_msg):
            for p, msg in enumerate(not_play_msg):
                if msg:
                    card = p + 1
                    unplayable_text = FONT_LARGE.render(f"CARD {card} TOO EXPENSIVE!", True, RED)
                    screen.blit(unplayable_text, unpl_pos)


def main_menu(server):
    global player_name

    input_box = pygame.Rect(50, HEIGHT // 2 + 20, 300, 50)
    color_inactive = FORZA_COLOR
    color_active = LIGHT_FORZA_COLOR
    color_insert_player = color_inactive
    active_insert_player = False
    active_top_player = False
    actived_player = False
    searching = False
    text = ''
    start_text = FONT_HUGE.render("PLAY ONLINE GAME", True, WHITE)
    start_button = pygame.Rect(50, HEIGHT // 2 + 90, start_text.get_width(),
                               start_text.get_height())
    start_ai_text = FONT_HUGE.render("OR SELECT AI LEVEL :", True, WHITE)
    diff_avg_text = FONT_HUGE.render("AVERAGE", True, BLACK)
    diff_pro_text = FONT_HUGE.render("PRO", True, BLACK)
    diff_unb_text = FONT_HUGE.render("UNBEATABLE", True, BLACK)
    diff_avg_button = pygame.Rect(50, HEIGHT // 2 + 190, diff_avg_text.get_width(),
                                  diff_avg_text.get_height())
    diff_pro_button = pygame.Rect(50 + diff_avg_text.get_width() + 25, HEIGHT // 2 + 190, diff_pro_text.get_width(),
                                  diff_pro_text.get_height())
    diff_unb_button = pygame.Rect(50, HEIGHT // 2 + 240, diff_unb_text.get_width(),
                                  diff_unb_text.get_height())
    get_card_text = FONT_HUGE.render("SHOW RANDOM CARD", True, WHITE)
    get_card_button = pygame.Rect(WIDTH - get_card_text.get_width() - 50, HEIGHT - 400, get_card_text.get_width(),
                                  get_card_text.get_height())
    get_new_random_card = False
    new_card = rebuild_hand([server.get_random_card()])[0]

    PLAYERS_LIST = "players_list.csv"
    selected_player = None
    running = True
    logo_image_main_menu = logo_image
    best_players = server.list_best_players()
    while running:
        try:
            pygame.display.update()
            screen.blit(main_menu_image, (0, 0))
            screen.blit(logo_image_main_menu, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    actived_player = False
                    # Se clicco dentro il box, attivo l'input
                    if input_box.collidepoint(event.pos):
                        active_insert_player = not active_insert_player
                    else:
                        active_insert_player = False

                    for p in best_players:
                        if p.get("rect") and p["rect"].collidepoint(event.pos):
                            selected_player = p["name"]
                            text = selected_player
                            active_top_player = True
                            actived_player = True
                    if not actived_player:
                        active_top_player = False

                    # Se clicco sui pulsanti Start
                    if text.strip() or selected_player:
                        if text.strip():
                            player_name = text.strip()
                        elif selected_player:
                            player_name = selected_player

                        if start_button.collidepoint(event.pos):
                            bot_game = False
                            running = False
                            searching = True
                        elif diff_pro_button.collidepoint(event.pos):
                            bot_game = True
                            diff_bot = "PRO"
                            running = False
                            searching = True
                        elif diff_unb_button.collidepoint(event.pos):
                            bot_game = True
                            diff_bot = "UNBEATABLE"
                            running = False
                            searching = True
                        elif diff_avg_button.collidepoint(event.pos):
                            bot_game = True
                            diff_bot = "AVERAGE"
                            running = False
                            searching = True

                    color_insert_player = color_active if active_insert_player else color_inactive

                    # Se clicco su show random card
                    if get_card_button.collidepoint(event.pos):
                        get_new_random_card = True

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif active_insert_player:
                        if event.key == pygame.K_BACKSPACE:
                            text = text[:-1]

                        else:
                            text += event.unicode

            # Classifica a destra
            widest_pl_text = 0
            y_offset = 150
            for i, p in enumerate(best_players):
                color_pl_text = LIGHT_FORZA_COLOR if active_top_player and selected_player == p[
                    'name'] else FORZA_COLOR
                pl_text = FONT_LARGE.render(
                    f"{i + 1}. {p['name'].upper()} ({p['points']} points, {p['wins']} W / {p['games']})", True,
                    BLACK)
                player_rect = pygame.Rect(WIDTH - pl_text.get_width() - 50, y_offset + i * 50,
                                          pl_text.get_width(), 40)
                if pl_text.get_width() > widest_pl_text:
                    widest_pl_text = pl_text.get_width()
                p["rect"] = player_rect
                p["text"] = pl_text
                p["color"] = color_pl_text

            top_panel = pygame.Surface((widest_pl_text + 50, y_offset + i * 50), pygame.SRCALPHA)
            top_panel.fill((0, 0, 0, 150))
            screen.blit(top_panel, (WIDTH - widest_pl_text - 75, 50))
            pygame.draw.rect(screen, FORZA_COLOR, (WIDTH - widest_pl_text - 75, 50, 5, y_offset + i * 50))

            top_label = FONT_BUTTONS.render("Top 5 Players", True, WHITE)
            screen.blit(top_label, (WIDTH - top_label.get_width() - 50, 50))
            for i, p in enumerate(best_players):
                color_pl_text = p["color"]
                pl_text = p["text"]
                player_rect = p["rect"]
                pygame.draw.rect(screen, color_pl_text, player_rect)
                screen.blit(pl_text, (player_rect.x, player_rect.y))

            # Carta random a destra
            if get_new_random_card:
                new_card = rebuild_hand([server.get_random_card()])[0]
                get_new_random_card = False
            new_card.draw_card(screen, WIDTH - 550, HEIGHT - 350, frame_images, FONT_SMALL, FONT_MEDIUM, FONT_LARGE,
                               FONT_TITLE, scaled=False, extended=True)
            pygame.draw.rect(screen, BLACK, get_card_button)
            screen.blit(get_card_text, (get_card_button.centerx - get_card_text.get_width() // 2,
                                        get_card_button.centery - get_card_text.get_height() // 2))

            # Inserimento nome a sinistra
            # Campo di testo
            txt_surface = FONT_HUGE.render(text, True, (255, 255, 255))
            width = max(300, txt_surface.get_width() + 10)
            input_box.w = width
            # Etichetta
            label = FONT_HUGE.render("INSERT NAME HERE:", True, WHITE)
            box_width = max(width, label.get_width(), start_ai_text.get_width())
            box_height = (
                    txt_surface.get_height() + label.get_height() + start_text.get_height() + start_ai_text.get_height() +
                    diff_pro_text.get_height() + diff_avg_text.get_height() + diff_unb_text.get_height())
            insert_name_panel = pygame.Surface((box_width + 50, box_height + 60), pygame.SRCALPHA)
            insert_name_panel.fill((0, 0, 0, 150))
            screen.blit(insert_name_panel, (25, HEIGHT // 2 - 35))
            pygame.draw.rect(screen, FORZA_COLOR, (25, HEIGHT // 2 - 35, 5, box_height + 60))

            pygame.draw.rect(screen, color_insert_player, input_box)
            pygame.draw.rect(screen, BLACK, input_box, 2)
            screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))

            screen.blit(label, (50, HEIGHT // 2 - 30))
            screen.blit(start_ai_text, (50, HEIGHT // 2 + 140))

            # Pulsanti Start
            pygame.draw.rect(screen, BLACK, start_button)
            screen.blit(start_text, (start_button.centerx - start_text.get_width() // 2,
                                     start_button.centery - start_text.get_height() // 2))
            pygame.draw.rect(screen, GREEN, diff_avg_button)
            screen.blit(diff_avg_text, (diff_avg_button.centerx - diff_avg_text.get_width() // 2,
                                        diff_avg_button.centery - diff_avg_text.get_height() // 2))
            pygame.draw.rect(screen, YELLOW, diff_pro_button)
            screen.blit(diff_pro_text, (diff_pro_button.centerx - diff_pro_text.get_width() // 2,
                                        diff_pro_button.centery - diff_pro_text.get_height() // 2))
            pygame.draw.rect(screen, RED, diff_unb_button)
            screen.blit(diff_unb_text, (diff_unb_button.centerx - diff_unb_text.get_width() // 2,
                                        diff_unb_button.centery - diff_unb_text.get_height() // 2))

            pygame.display.flip()
            clock.tick(60)
        except Exception:
            print("\n--- Traceback remoto dal server ---")
            print("".join(Pyro5.errors.get_pyro_traceback()))

    try:
        if bot_game:
            registered_log = server.register_ai_game(player_name, diff_bot)
        else:
            registered_log = server.register_player(player_name)
    except Exception:
        print("\n--- Traceback remoto dal server ---")
        print("".join(Pyro5.errors.get_pyro_traceback()))
    while searching:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.blit(main_menu_image, (0, 0))  # ridisegno sfondo
        # Messaggi di registrazione
        if registered_log['status']:
            mess = FONT_BUTTONS.render("Player registered, searching game", True, (255, 255, 255))
        else:
            mess = FONT_BUTTONS.render(str(registered_log["message"]), True, (255, 255, 255))
        screen.blit(mess, (WIDTH // 2 - mess.get_width() // 2, HEIGHT // 2 + 120))
        # Polling ogni mezzo secondo
        pygame.time.wait(500)

        if server.game_start():
            game_found = FONT_BUTTONS.render("Match found!", True, WHITE)
            screen.blit(game_found, (WIDTH // 2 - game_found.get_width() // 2, HEIGHT // 2 + 160))
            pygame.display.flip()
            pygame.time.wait(2000)
            searching = False
            break
        pygame.display.flip()
        clock.tick(60)


def end_game(results, server):
    global player_name
    while True:
        try:
            screen.blit(endgame_image, (0, 0))
            logo_image_end_game = logo_image
            screen.blit(logo_image_end_game, (WIDTH - logo_image_end_game.get_width() - 20, 0))
            tot_winner = results["total_winner"]
            tot_loser = results["total_loser"]
            hp_winner = results["hp_winner"]
            if tot_winner == player_name:
                screen.blit(win_image, (50, HEIGHT - win_image.get_height() - 50))
                points_gained = hp_winner
            elif tot_loser == player_name:
                screen.blit(lose_image, (50, HEIGHT - win_image.get_height() - 50))
                points_gained = 0
            points_text = FONT_HUGE.render(f"Points gained : {points_gained}", True, FORZA_COLOR)
            box_width = points_text.get_width() + 50
            goto_menu_text = FONT_HUGE.render("GO TO MAIN MENU", True, WHITE)
            box_height = points_text.get_height() + goto_menu_text.get_height()
            insert_name_panel = pygame.Surface((box_width + 50, box_height + 50), pygame.SRCALPHA)
            insert_name_panel.fill((0, 0, 0, 150))
            screen.blit(insert_name_panel, (WIDTH - box_width - 50, logo_image.get_height() + 75))
            pygame.draw.rect(screen, FORZA_COLOR,
                             (WIDTH - box_width - 40, logo_image.get_height() + 75, 5, box_height + 50))

            screen.blit(points_text, (WIDTH - points_text.get_width() - 25, logo_image.get_height() + 100))
            goto_menu_button = pygame.Rect(WIDTH - goto_menu_text.get_width() - 25, logo_image.get_height() + 150,
                                           goto_menu_text.get_width(),
                                           goto_menu_text.get_height())
            pygame.draw.rect(screen, BLACK, goto_menu_button)
            screen.blit(goto_menu_text, (goto_menu_button.centerx - goto_menu_text.get_width() // 2,
                                         goto_menu_button.centery - goto_menu_text.get_height() // 2))

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Se clicco dentro il box, attivo l'input
                    if goto_menu_button.collidepoint(event.pos):
                        server.unregister_player(player_name)
                        main_loop()
        except Exception:
            print("\n--- Traceback remoto dal server ---")
            print("".join(Pyro5.errors.get_pyro_traceback()))

        pygame.display.flip()
        clock.tick(60)


def rebuild_hand(light_hand, selected_cards=None):
    hand = []
    for i, light_card in enumerate(light_hand):
        card = CarCard(
            name=light_card["name"],
            manufacturer=light_card["manufacturer"],
            year=light_card["year"],
            model=light_card["model"],
            car_type=light_card["car_type"],
            rarity=light_card["rarity"],
            country=light_card["country"],
            car_class=light_card["car_class"],
            pi=light_card["pi"],
            speed=light_card["speed"],
            handling=light_card["handling"],
            acceleration=light_card["acceleration"],
            launch=light_card["launch"],
            braking=light_card["braking"],
            offroad=light_card["offroad"],
            avg_stat=light_card["avg_stat"],
            drivetrain=light_card["drivetrain"],
            load_image=True
        )
        if selected_cards:
            if selected_cards[i]:
                card.played_card()
        hand.append(card)
    return hand


def rebuild_loc(loc, sel):
    new_loc = []
    for i, l in enumerate(loc):
        new_l = Location(
            name=l["name"],
            stat=l["stat"],
            load_image=True
        )
        if sel[i]:
            new_l.chosen_location(sel[i])
        new_l.bonus_val = l["bonus_val"]
        new_l.bonus_cat = l["bonus_cat"]
        new_l.bonus_ass = l["bonus_ass"]
        new_loc.append(new_l)
    return new_loc


def main_loop():
    global player_name, partial_energy, opponent_name
    # Connessione server
    ns = Pyro5.api.locate_ns(host="192.168.178.83")
    uri = ns.lookup("game.server")
    server = Pyro5.api.Proxy(uri)
    game_ended = False
    main_menu(server)
    # Stato iniziale
    selected_location = None
    sel = None
    selected_locations = [False, False, False]
    selected_cards = [False, False, False, False, False]
    not_playable = [False, False, False, False, False]
    start_time_not_playable = [None, None, None, None, None]
    not_playable_adv = [False, False, False, False, False]
    set_new_energy = False
    player_choices = {}
    card_to_show = None
    phase = "card_sel"  # fase selezione carte
    clock = pygame.time.Clock()
    last_poll = 0
    last_upd_time = 0
    UPD_INTERVAL = 100
    while not game_ended:
        try:
            current_time = pygame.time.get_ticks()
            if current_time - last_upd_time > UPD_INTERVAL:
                state = server.get_state()
                current_player = state["players"][player_name]
                opponent_name = [p for p in state["players"].keys() if p != player_name][0]
                other_player = state["players"][opponent_name]
                turn = state["turn"]
                locs = rebuild_loc(state["locations"], selected_locations)
                hand = rebuild_hand(current_player["hand"], selected_cards)
            if not set_new_energy:
                partial_energy = energies[min(state["turn"] - 1, 4)]
                set_new_energy = True
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if card_to_show:
                            card_to_show = None
                        else:
                            pygame.quit()
                            sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN and phase == "card_sel":
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    # Popup carta estesa

                    if card_to_show:
                        card_to_show = None
                        continue

                    if event.button == 3:
                        x_offset = CARDS_OFFSET[0]
                        for c in hand:
                            # Calcola rect della carta nella mano
                            card_rect = pygame.Rect(x_offset, HEIGHT - 300, CARD_SIZE[0], CARD_SIZE[1])
                            if card_rect.collidepoint(mouse_x, mouse_y):
                                card_to_show = c  # Imposta la carta da mostrare
                                break  # Trovata, esci dal ciclo
                            x_offset += CARDS_OFFSET[1]
                    elif event.button == 1:
                        # selezione location
                        for i, loc in enumerate(locs):
                            loc_rect = pygame.Rect(LOCATIONS_POS[0] + i * LOCATIONS_POS[2], LOCATIONS_POS[1], 250, 250)
                            if loc_rect.collidepoint(mouse_x, mouse_y) and not selected_locations[i]:
                                selected_location = loc.name
                                sel = i

                        # selezione carta
                        x_offset = CARDS_OFFSET[0]

                        for idx, c in enumerate(hand):
                            card_rect = pygame.Rect(x_offset, HEIGHT - 300, CARD_SIZE[0], CARD_SIZE[1])
                            if card_rect.collidepoint(mouse_x,
                                                      mouse_y) and selected_location is not None and selected_location not in player_choices.keys():
                                if partial_energy >= c.pi:
                                    remaining_energy = partial_energy - c.pi
                                    costs_in_hand = sorted([cc.pi for cc in hand if cc != c])
                                    lowest_costs = sum(costs_in_hand[:(2 - len(player_choices))])
                                    if remaining_energy >= lowest_costs:
                                        player_choices[selected_location] = idx
                                        selected_cards[idx] = True
                                        bonuses = locs[sel].check_criteria(c)
                                        real_value = c.calc_real_val(bonuses, c.get_stat(locs[sel].stat))
                                        selected_locations[sel] = real_value
                                        selected_location = None
                                        partial_energy = remaining_energy
                                    else:
                                        not_playable[idx] = True
                                else:
                                    not_playable[idx] = True
                            x_offset += CARDS_OFFSET[1]
                        if len(player_choices.keys()) >= 3:
                            turn_info = server.submit_turn(player_name, player_choices)
                            if turn_info["resolved"]:
                                phase = "dmg_eval"
                            else:
                                phase = "end_turn"
                                last_poll = pygame.time.get_ticks()
            # Fase di selezione
            if phase == "card_sel":
                active_loc_obj = None
                if selected_location:
                    for l in locs:
                        if l.name == selected_location:
                            active_loc_obj = l
                            break
                if any(not_playable):
                    for pos, i in enumerate(not_playable):
                        if i:
                            start_time_not_playable[pos] = pygame.time.get_ticks()
                            not_playable[pos] = False
                for pos, t in enumerate(start_time_not_playable):
                    if t is not None:
                        if current_time - t <= 1000:
                            not_playable_adv[pos] = True
                        else:
                            not_playable_adv[pos] = False
                            start_time_not_playable[pos] = None
                draw_info(turn, current_player, other_player, phase, not_playable_adv, None)
                draw_locations(turn, locs, current_player["cat"], phase,
                               selected_location)
                draw_hand(hand, active_loc_obj)
                # Disegno popup
                if card_to_show is not None:
                    card_to_show.draw_card(screen, 0, 0, frame_images, FONT_SMALL, FONT_MEDIUM, FONT_LARGE, FONT_SMALL,
                                           extended=True, in_game=True, selected_loc=active_loc_obj)
            # Fase di fine turno
            elif phase == "end_turn":
                draw_info(turn, current_player, other_player, phase, None, None)
                draw_locations(turn, locs, current_player["cat"], phase)
                draw_hand(hand)
                now = pygame.time.get_ticks()
                if now - last_poll > 500:
                    turn_info = server.get_end_turn_info()
                    last_poll = now
                    if turn_info["resolved"]:
                        phase = "dmg_eval"
            # Fase di risoluzione
            elif phase == "dmg_eval":
                results = turn_info["results"]
                draw_info(turn, current_player, other_player, phase, None, results)
                if turn_info["total_results"]:
                    tot_results = turn_info["total_results"]
                    phase = "game_over"
                else:
                    pygame.time.wait(3000)
                    player_choices = {}
                    selected_locations = [False, False, False]
                    selected_cards = [False, False, False, False, False]
                    set_new_energy = False
                    phase = "card_sel"
            # Fase di game over
            elif phase == "game_over":
                game_ended = True
            pygame.display.flip()
            clock.tick(60)
        except Exception:
            print("\n--- Traceback remoto dal server ---")
            print("".join(Pyro5.errors.get_pyro_traceback()))
    if game_ended:
        end_game(tot_results, server)
    pygame.quit()
    sys.exit()


def hp_to_angle(current_hp):
    hp_ratio = current_hp / MAX_HP
    angle = MIN_ANGLE + (MAX_ANGLE - MIN_ANGLE) * (1 - hp_ratio)
    return angle


if __name__ == "__main__":
    player_name = None
    opponent_name = None
    Pyro5.errors.config.DETAILED_TRACEBACK = True
    main_loop()
