# 🏎️ ForzaCards - Distributed Multiplayer Card Game

**ForzaCards** è un gioco di carte strategico multiplayer basato sui dati reali delle auto di *Forza Horizon 5*.
Il progetto è un'implementazione pratica di un **Sistema Distribuito Client-Server**, sviluppato in Python utilizzando il middleware **Pyro5** per la comunicazione remota e **Pygame** per l'interfaccia grafica.

![Gameplay Screenshot](screenshots/gameplay.png)
*(Inserisci qui uno screenshot della board di gioco)*

## 📋 Funzionalità Principali

* **Architettura Client-Server:** Gestione centralizzata dello stato di gioco con sincronizzazione in tempo reale tra client concorrenti.
* **Modalità PvP & PvE:** Gioca contro un altro giocatore umano in LAN o sfida l'Intelligenza Artificiale (CPU).
* **Logica di Gioco Strategica:**
    * Mazzo generato dinamicamente con rarità ponderata (Common, Rare, Legendary, etc.).
    * Sistema di **Bonus Location**: Le carte ottengono potenziamenti in base a Nazione, Trazione o Classe.
    * Gestione dell'Energia (PI - Performance Index) limitata per turno.
* **Interfaccia "Juicy":** Feedback visivi avanzati, ispezione carte con click destro, effetti grafici per i bonus.
* **Robustezza:** Algoritmi di fallback per la pesca delle carte e gestione thread-safe delle risorse (RLock).

## 🛠️ Tecnologie Utilizzate

* **Linguaggio:** Python 3.9+
* **Networking/RMI:** [Pyro5](https://pypi.org/project/Pyro5/) (Python Remote Objects)
* **GUI:** [Pygame](https://www.pygame.org/)
* **Data Analysis:** [Pandas](https://pandas.pydata.org/) (Gestione dataset CSV)

## ⚙️ Installazione

1.  **Clona il repository:**
    ```bash
    git clone [https://github.com/tuo-username/ForzaCards.git](https://github.com/tuo-username/ForzaCards.git)
    cd ForzaCards
    ```

2.  **Crea un ambiente virtuale (Opzionale ma consigliato):**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Installa le dipendenze:**
    ```bash
    pip install -r requirements.txt
    ```

## 🚀 Come Avviare il Gioco

Poiché si tratta di un sistema distribuito, è necessario avviare i componenti nell'ordine corretto.

### 1. Avvia il Name Server (Pyro)
Il Name Server permette ai componenti di trovarsi sulla rete.
Apri un terminale e lancia:
```bash
python -m Pyro5.nameserver
