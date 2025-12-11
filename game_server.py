import Pyro5.api
import random
import threading
from collections import defaultdict
from deck import Deck
from location import Location
import copy
import pandas as pd
from AI import AI

# Configurazione
MAX_PLAYERS = 2
SERVER_IP = "192.168.178.83"
DB_CSV = "db_cleaned.csv"
LOCATIONS_LIST = [
    Location("quarter_mile", "launch", load_image=False),
    Location("half_mile", "acceleration", load_image=False),
    Location("circuit_track", "handling", load_image=False),
    Location("highway", "speed", load_image=False),
    Location("offroad_trail", "offroad", load_image=False),
    Location("brake_test", "braking", load_image=False),
]
# Font
ENERGIES = [1330, 1875, 2150, 2440, 2680]
MAX_HP = 10
PLAYERS_LIST = "players_list.csv"


@Pyro5.api.expose
class GameServer:
    def __init__(self):
        self.lock = threading.RLock()
        self.players = {}  # nome -> player state dict
        self.order = []
        self.ai_player = None
        self.turn = 1
        self.current_locations = self._draw_new_locations()
        self.player_choices = {}
        self.ready = set()
        self.game_ready = False
        self.last_results = None
        self.total_results = None
        self.turn_resolved = False
        self.players_list = self.load_players(PLAYERS_LIST)

    # ---------------- player & lobby management ----------------
    def load_players(self, players_list):
        players = pd.read_csv(players_list)
        return players

    def get_random_card(self):
        temp_deck = Deck(DB_CSV)
        card = random.choice(temp_deck.cards)
        return self._card_summary(card)

    def list_best_players(self):
        best_players = self.players_list.sort_values(by='points', ascending=False).head(5)
        return best_players.to_dict(orient='records')

    def register_player(self, player_name):
        with self.lock:
            if player_name not in self.order:
                self.order.append(player_name)
                player_deck = Deck(DB_CSV)
                player_deck.shuffle()
                hand, categories = player_deck.draw_cards(1)
                self.players[player_name] = {
                    "hp": 10,
                    "energy": ENERGIES[0],
                    "hand": hand,
                    "deck": player_deck,
                    "cat": categories,
                }
                self.player_choices[player_name] = {}

        if len(self.order) == 2:
            self.game_ready = True
        return {"status": True, "n_players": len(self.order)}

    def unregister_player(self, player_name):

        with self.lock:
            del self.players[str(player_name)]
            self.order.remove(str(player_name))
            if self.ai_player:
                del self.players[self.ai_player.name]
                self.order.remove(self.ai_player.name)
            self._clean_internals()
            return {"ok": True}

    def game_start(self):
        return self.game_ready

    def register_ai_game(self, player_name, difficulty):
        with self.lock:
            # 1. Registra il giocatore umano (come register_player normale)
            self.players = {}
            self.order = []

            # Registra Umano
            self.register_player(player_name)

            # 2. Crea e Registra l'AI
            ai_name = f"BOT_{difficulty[:3]}"
            self.ai_player = AI(ai_name, difficulty)  # Istanza della classe AI

            # Creiamo lo stato per l'AI come se fosse un giocatore normale
            ai_deck = Deck(DB_CSV)
            ai_deck.shuffle()
            hand, categories = ai_deck.draw_cards(1)

            self.order.append(ai_name)
            self.players[ai_name] = {
                "hp": 10,
                "energy": ENERGIES[0],
                "hand": hand,
                "deck": ai_deck,
                "cat": categories
            }
            self.player_choices[ai_name] = {}

            self.game_ready = True  # Il gioco parte subito
            return {"status": True, "n_players": 2}

    # ---------------- state retrieval ----------------
    def get_state(self):
        """Restituisce lo stato di gioco serializzabile (dizionari, tuple).
        Le carte sono ridotte a tuple: (name, car_type, pi, class)"""
        with self.lock:
            state = {
                "turn": self.turn,
                "locations": [self._loc_summary(loc) for loc in self.current_locations],
                "players": {}
            }
            for name, p in self.players.items():
                state["players"][name] = {
                    "hp": p["hp"],
                    "energy": p["energy"],
                    "hand": [self._card_summary(c) for c in p["hand"]],
                    "cat": p["cat"],
                }
            return state

    # ---------------- actions ----------------

    def submit_turn(self, player_name, played_cards):
        """
        played_cards = {location_name: card_name, ...}
        """
        with self.lock:
            if not self.player_choices[player_name]:
                self.player_choices[player_name] = dict(played_cards)
                self.ready.add(player_name)
            if self.ai_player:
                ai_name = self.ai_player.name

                # Recupera dati AI
                ai_state = self.players[ai_name]
                ai_hand = ai_state["hand"]
                ai_energy = ai_state["energy"]

                # L'AI calcola la mossa
                # Passiamo gli oggetti location attuali
                ai_moves = self.ai_player.play_turn(ai_hand, ai_energy, self.current_locations)

                # Salviamo la mossa nel server
                self.player_choices[ai_name] = ai_moves
                self.ready.add(ai_name)
            # Quando tutti hanno inviato le loro giocate
            if len(self.ready) == len(self.players):
                results = self._resolve_turn_locked()
                if self._advance_turn_locked():
                    tot_results = self._advance_turn_locked()
                    self.total_results = tot_results
                for p in list(self.player_choices.keys()):
                    self.player_choices[p] = {}
                self.ready.clear()
                self.last_results = results
                self.turn_resolved = True
                return {
                    "ok": True,
                    "resolved": True,
                    "results": results,
                    "total_results": self.total_results
                }
            return {
                "ok": True,
                "resolved": False,
            }

    def get_end_turn_info(self):
        with self.lock:
            if self.turn_resolved:  # Turno finito
                self.turn_resolved = False
                return {"resolved": True, "results": self.last_results, "total_results": self.total_results}
            else:
                return {"resolved": False}

    # ---------------- internal helpers ----------------
    def _card_summary(self, card):
        """Restituisce un dizionario serializzabile per Pyro."""
        if isinstance(card, dict):
            return card
        return {
            "name": card.name,
            "manufacturer": card.manufacturer,
            "year": card.year,
            "model": card.model,
            "car_type": card.car_type,
            "rarity": card.rarity,
            "country": card.country,
            "car_class": card.car_class,
            "pi": card.pi,
            "speed": card.speed,
            "handling": card.handling,
            "acceleration": card.acceleration,
            "launch": card.launch,
            "braking": card.braking,
            "offroad": card.offroad,
            "avg_stat": card.avg_stat,
            "drivetrain": card.drivetrain
        }

    def _loc_summary(self, l):
        return {
            "name": l.name,
            "stat": l.stat,
            "chosen": l.chosen,
            "bonus_val": l.bonus_val,
            "bonus_cat": l.bonus_cat,
            "bonus_ass": l.bonus_ass
        }

    def _update_players_stats(self, winner, loser, points):
        for player in [winner, loser]:
            if player not in self.players_list['name'].values and player != self.ai_player.name:
                # se il giocatore non esiste, aggiungilo
                # se è il bot no
                self.players_list.loc[len(self.players_list)] = [player, 0, 0, 0]

        # Incrementa i contatori
        if winner != self.ai_player.name:
            self.players_list.loc[self.players_list['name'] == winner, 'wins'] += 1
            self.players_list.loc[self.players_list['name'] == winner, 'points'] += round(points)
            self.players_list.loc[self.players_list['name'] == winner, 'games'] += 1
        if loser != self.ai_player.name:
            self.players_list.loc[self.players_list['name'] == loser, 'games'] += 1

        self.players_list.to_csv(PLAYERS_LIST, index=True, index_label=False)

    def _clean_internals(self):
        self.players = {}
        self.order = []
        self.ai_player = None
        self.turn = 1
        self.current_locations = self._draw_new_locations()
        self.player_choices = {}
        self.ready = set()
        self.game_ready = False
        self.last_results = None
        self.total_results = None
        self.turn_resolved = False
        self.players_list = self.load_players(PLAYERS_LIST)

    def _resolve_turn_locked(self):
        """
        Confronta le scelte dei giocatori per ogni location e calcola i danni.
        Questa funzione lavora con lock già acquisito.
        """
        results = []
        positions_p1 = []
        positions_p2 = []
        # get list of players in consistent order
        p1, p2 = self.order[0], self.order[1]
        # per ogni location (0..2)
        for loc in self.current_locations:
            # raccogli le carte giocate dai giocatori su questa location
            pos_c1 = self.player_choices[p1][loc.name]
            pos_c2 = self.player_choices[p2][loc.name]
            positions_p1.append(pos_c1)
            positions_p2.append(pos_c2)
            c1 = self.players[p1]["hand"][pos_c1]
            c2 = self.players[p2]["hand"][pos_c2]

            # supponiamo due giocatori: confronta i valori dell'attributo dominante

            winner, dmg, vals, attr = self._compare_cards(loc, c1, c2)

            results.append({
                "location": [loc.name, attr],
                "winner": winner,
                "damage": dmg,
                "played_cards": {p1: [self._card_summary(c1)],
                                 p2: [self._card_summary(c2)]},
                "vals": {p1: vals[0], p2: vals[1]}
            })
        hand_p1 = self.players[p1]["hand"]
        hand_p2 = self.players[p2]["hand"]
        self.players[p1]["hand"] = [card for i, card in enumerate(hand_p1) if i not in positions_p1]
        self.players[p2]["hand"] = [card for i, card in enumerate(hand_p2) if i not in positions_p2]

        return results

    def _advance_turn_locked(self):
        """Aggiorna turno, refill mani, location, energie, oppure gestione endgame"""
        p1, p2 = self.order[0], self.order[1]
        p1_hp = self.players[p1]["hp"]
        p2_hp = self.players[p2]["hp"]
        if p1_hp <= 0 or p2_hp <= 0:
            if p1_hp <= 0 and p2_hp <= 0:
                total_winner = p1 if p2_hp < p1_hp else p2
                total_loser = p2 if p1_hp < p2_hp else p1
                hp_winner = p1_hp if p2_hp < p1_hp else p2
            elif p1_hp <= 0:
                total_winner = p2
                hp_winner = p2_hp
                total_loser = p1
            elif p2_hp <= 0:
                total_winner = p1
                total_loser = p2
                hp_winner = p1_hp

            self._update_players_stats(total_winner, total_loser, hp_winner)
            return {
                "total_winner": total_winner,
                "total_loser": total_loser,
                "hp_winner": hp_winner

            }

        self.turn += 1
        # nuove location
        self.current_locations = self._draw_new_locations()

        # Ricarica energia, refill hand...
        for p in self.players.values():
            new_cards, p["cat"] = p["deck"].draw_cards(self.turn, p["hand"])
            p["hand"] = new_cards
            p["energy"] = ENERGIES[min(self.turn - 1, len(ENERGIES) - 1)]
        for loc in self.current_locations:
            loc.pick_bonus(self.turn, self.players[self.order[0]]["cat"])
        return None

    # ---------------- utility ----------------

    def _draw_new_locations(self):
        """Genera 3 location casuali per l'inizio del turno"""
        return [Location(l.name, l.stat, load_image=False) for l in random.sample(LOCATIONS_LIST, 3)]

    def _compare_cards(self, location, c1, c2):
        """Restituisce il nome del giocatore vincente o None"""
        attr = location.stat
        v1 = c1.get_stat(attr)
        v2 = c2.get_stat(attr)

        # applica bonus location se presenti
        if location.bonus_cat is not None:
            bonuses_c1 = location.check_criteria(c1)
            bonuses_c2 = location.check_criteria(c2)
            v1 = c1.calc_real_val(bonuses_c1, v1)
            v2 = c2.calc_real_val(bonuses_c2, v2)
        vals = [v1, v2]
        dmg = 0.0
        if v1 > v2:
            winner = self.order[0]
            dmg = round(v1 - v2, 1)
            self.players[self.order[1]]["hp"] = round(self.players[self.order[1]]["hp"] - dmg, 1)
        elif v2 > v1:
            winner = self.order[1]
            dmg = round(v2 - v1, 1)
            self.players[self.order[0]]["hp"] = round(self.players[self.order[0]]["hp"] - dmg, 1)
        else:
            winner = "Draw"

        return winner, dmg, vals, attr


def main():
    daemon = Pyro5.api.Daemon(host=SERVER_IP)
    ns = Pyro5.api.locate_ns(host=SERVER_IP)
    gameserver = GameServer()
    uri = daemon.register(gameserver)
    ns.register("game.server", uri)
    print("Server pronto. URI:", uri)
    daemon.requestLoop()


if __name__ == "__main__":
    main()
