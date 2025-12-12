import itertools
import random


class AI:
    def __init__(self, name, difficulty):
        self.name = name
        self.difficulty = difficulty

    def play_turn(self, hand, energy, locations):
        """
        Sceglie 3 carte dalla mano che rispettino il limite di energia.
        Restituisce un dizionario: {nome_location: indice_carta_nella_mano}
        """
        # 1. Trova tutte le combinazioni di 3 carte possibili
        # Restituisce una lista di tuple: (indice, carta)
        indexed_hand = list(enumerate(hand))
        possible_combinations = list(itertools.combinations(indexed_hand, 3))

        valid_moves = []

        # 2. Filtra quelle che costano troppo (PI > Energia)
        for combo in possible_combinations:
            # combo è una tupla di 3 elementi: ((idx1, card1), (idx2, card2), (idx3, card3))
            total_pi = sum(c[1].pi for c in combo)
            if total_pi <= energy:
                valid_moves.append(combo)

        # 3. Scegli la mossa in base alla difficoltà
        chosen_combo = None

        if self.difficulty == "AVERAGE":
            # Sceglie a caso una combinazione valida
            chosen_combo = random.choice(valid_moves)
            # Mischia l'assegnazione alle location
            # (non ottimizza quale carta va su quale location)
            random.shuffle(list(chosen_combo))

        elif self.difficulty == "PRO":  # medium
            # Cerca la combinazione che massimizza il punteggio sulle location attuali
            best_score = -1

            for combo in valid_moves:
                # combo contiene 3 carte. Proviamo tutte le permutazioni di queste 3 carte 
                # sulle 3 location per trovare l'incastro migliore
                # permutations genera le varianti di assegnazione (carta A su loc 1 vs carta A su loc 2...)
                for perm in itertools.permutations(combo):
                    current_score = 0
                    # perm[0] va su locations[0], perm[1] su locations[1], ecc.
                    for i in range(3):
                        card = perm[i][1]  # Oggetto carta
                        loc = locations[i]  # Oggetto location

                        # Calcola valore senza bonus
                        stat_val = card.get_stat(loc.stat)

                        current_score += stat_val

                    if current_score > best_score:
                        best_score = current_score
                        chosen_combo = perm
        elif self.difficulty == "UNBEATABLE":  # hard
            # Cerca la combinazione che massimizza il punteggio sulle location attuali considerando bonus
            best_score = -1

            for combo in valid_moves:
                # combo contiene 3 carte. Proviamo tutte le permutazioni di queste 3 carte
                # sulle 3 location per trovare l'incastro migliore
                # permutations genera le varianti di assegnazione (carta A su loc 1 vs carta A su loc 2...)
                for perm in itertools.permutations(combo):
                    current_score = 0
                    # perm[0] va su locations[0], perm[1] su locations[1], ecc.
                    for i in range(3):
                        card = perm[i][1]  # Oggetto carta
                        loc = locations[i]  # Oggetto location

                        # Calcola valore con bonus
                        base_val = card.get_stat(loc.stat)
                        bonuses_card = loc.check_criteria(card)
                        stat_val = card.calc_real_val(bonuses_card, base_val)

                        current_score += stat_val

                    if current_score > best_score:
                        best_score = current_score
                        chosen_combo = perm

        # 4. Formatta l'output per il Server
        # Il server si aspetta: { "LocationName": indice_carta }
        result = {}
        for i in range(3):
            # chosen_combo[i] è una tupla (indice_originale, oggetto_carta)
            loc_name = locations[i].name
            card_index = chosen_combo[i][0]
            result[loc_name] = card_index

        return result
