import itertools
from collections import Counter
import pandas as pd
from carcard import CarCard
import random

energies = [1330, 1875, 2150, 2440, 2680]


class Deck:
    def __init__(self, csv_path):
        self.cards = []
        self.load_deck(csv_path)

    def load_deck(self, csv_path):
        df = pd.read_csv(csv_path)

        for _, row in df.iterrows():
            card = CarCard(
                name=row["name"],
                manufacturer=row["man"],
                year=row["year"],
                model=row["model"],
                car_type=row["type"],
                rarity=row["rarity"],
                country=row["country"],
                car_class=row["class"],
                pi=row["PI"],
                speed=row["speed"],
                handling=row["handling"],
                acceleration=row["acceleration"],
                launch=row["launch"],
                braking=row["braking"],
                offroad=row["offroad"],
                drivetrain=row["drivetrain"],
                avg_stat=row["avg"]
            )
            self.cards.append(card)

    def shuffle(self):
        random.shuffle(self.cards)

    def get_card(self, name):
        for card in self.cards:
            if card.name == name:
                return card

    def draw_cards(self, turn, current_hand=None):
        # Definizione pesi per ogni turno
        if turn == 1:
            available_classes = ['D', 'C']
            available_pi = [100, 600]
            weights = [0.70, 0.30]
        elif turn == 2:
            available_classes = ['D', 'C', 'B', 'A']
            available_pi = [300, 750]
            weights = [0.20, 0.25, 0.40, 0.15]
        elif turn == 3:
            available_classes = ['D', 'C', 'B', 'A', 'S1']
            available_pi = [450, 850]
            weights = [0.05, 0.10, 0.40, 0.30, 0.15]
        elif turn == 4:
            available_classes = ['C', 'B', 'A', 'S1', 'S2']
            available_pi = [550, 950]
            weights = [0.05, 0.15, 0.35, 0.30, 0.15]
        else:  # turno 5 e oltre
            available_classes = ['B', 'A', 'S1', 'S2']
            available_pi = [650, 998]
            weights = [0.05, 0.10, 0.45, 0.40]

        weights = [w / sum(weights) for w in weights]
        max_attempts = 200
        attempt = 0
        # Filtra le carte effettivamente disponibili
        av_cards = [c for c in self.cards if
                    c.car_class in available_classes and available_pi[0] <= c.pi <= available_pi[1]]
        if current_hand:
            keep_cards = [c for c in current_hand if
                     c.car_class in available_classes and available_pi[0] <= c.pi <= available_pi[1]]
        else:
            keep_cards = []
        n = 5 - len(keep_cards)
        if not av_cards:
            raise ValueError(f"Nessuna carta disponibile per classi {available_classes} nel range PI {available_pi}")

        # Distribuzione categorie per bonus
        cats = {}
        # Car Type
        category_car_types_counts = Counter([c.car_type for c in av_cards])
        total = sum(category_car_types_counts.values())
        categories_car_types = list(category_car_types_counts.keys())
        car_types_weights = [category_car_types_counts[cat] / total for cat in categories_car_types]
        cats["car_types"] = [categories_car_types, car_types_weights]
        # Rarity
        category_rarity_counts = Counter([c.rarity for c in av_cards])
        total = sum(category_rarity_counts.values())
        categories_rarities = list(category_rarity_counts.keys())
        rarities_weights = [category_rarity_counts[cat] / total for cat in categories_rarities]
        cats["rarities"] = [categories_rarities, rarities_weights]
        # Nation
        category_nations_counts = Counter([c.country for c in av_cards])
        total = sum(category_nations_counts.values())
        categories_nations = list(category_nations_counts.keys())
        nations_weights = [category_nations_counts[cat] / total for cat in categories_nations]
        cats["nations"] = [categories_nations, nations_weights]
        # Drivetrain
        category_drive_counts = Counter([c.drivetrain for c in av_cards])
        total = sum(category_drive_counts.values())
        categories_drive = list(category_drive_counts.keys())
        drive_weights = [category_drive_counts[cat] / total for cat in categories_drive]
        cats["drives"] = [categories_drive, drive_weights]
        attempts_schedule = [
            (100, 5),  # Primi 100 tentativi: cerchiamo l'eccellenza (5 combo)
            (50, 3),  # Altri 50 tentativi: ci accontentiamo di 3 combo
            (50, 1)  # Ultimi 50 tentativi: basta che sia giocabile (1 combo)
        ]
        for max_iter, min_required_combos in attempts_schedule:
            for _ in range(max_iter):
                attempt += 1
                temp_cards = self.cards.copy()
                drawn = []

                for _ in range(n):
                    chosen_class = random.choices(available_classes, weights=weights, k=1)[0]
                    cards_in_class = [c for c in temp_cards if
                                      c.car_class == chosen_class and available_pi[0] <= c.pi <= available_pi[1]]
                    if not cards_in_class:
                        continue
                    card = random.choice(cards_in_class)
                    drawn.append(card)
                    temp_cards.remove(card)

                new_hand = keep_cards + drawn
                # Controllo combinazioni giocabili
                turn_energy = energies[min(turn - 1, 4)]
                valid_combinations = sum(
                    1 for comb in itertools.combinations(new_hand, 3)
                    if sum(c.pi for c in comb) <= turn_energy
                )
                combinable = valid_combinations >= min_required_combos

                if combinable:
                    for card in drawn:
                        self.cards.remove(card)
                    return new_hand, cats

        raise ValueError("Impossibile pescare carte giocabili con l'energia disponibile.")
