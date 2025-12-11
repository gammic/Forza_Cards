import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# --- SETUP CARTELLA ---
OUTPUT_DIR = "images/graphs"
os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"I grafici verranno salvati in: {os.path.abspath(OUTPUT_DIR)}")

DB_CSV = "db_cleaned.csv"
try:
    cards = pd.read_csv(DB_CSV)
except FileNotFoundError:
    # Fallback se il file si chiama diversamente dopo l'aggiornamento
    cards = pd.read_csv("db_completo_con_trazione.csv")

# 1. ANALISI COSTI (PI)
plt.figure(figsize=(10, 6))
plt.hist(cards["PI"], bins=18, color='skyblue', edgecolor='black')
plt.xlabel("Costo (PI)")
plt.ylabel("Frequenza")
plt.title("Distribuzione dei costi delle carte")
plt.savefig(os.path.join(OUTPUT_DIR, "distribuzione_costi_pi.png"))
plt.close()

plt.figure(figsize=(10, 6))
sns.kdeplot(cards["PI"], fill=True, color='orange')
plt.title("Distribuzione lisciata del costo (KDE)")
plt.savefig(os.path.join(OUTPUT_DIR, "distribuzione_costi_kde.png"))
plt.close()

# 2. ANALISI STATISTICHE DI GIOCO
plt.figure(figsize=(12, 8))
cards[["speed", "acceleration", "handling", "launch", "braking", "offroad"]].hist(bins=20, figsize=(12, 8))
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "distribuzione_stats_gioco.png"))
plt.close()

# ---------------------------------------------------------
# NUOVE ANALISI RICHIESTE (Type, Year, Rarity, Country, Drivetrain)
# ---------------------------------------------------------

# A. CAR TYPE (Grafico a barre orizzontale per leggibilità)
plt.figure(figsize=(12, 10))
type_counts = cards['type'].value_counts().sort_values()
type_counts.plot(kind='barh', color='teal')
plt.title("Distribuzione per Tipo Auto (Car Type)")
plt.xlabel("Numero di Auto")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "analisi_car_type.png"))
plt.close()

# B. YEAR (Istogramma)
plt.figure(figsize=(10, 6))
sns.histplot(cards['year'], bins=30, kde=True, color='purple')
plt.title("Distribuzione per Anno di Produzione")
plt.xlabel("Anno")
plt.savefig(os.path.join(OUTPUT_DIR, "analisi_year.png"))
plt.close()

# C. RARITY (Bar Chart)
plt.figure(figsize=(8, 6))
rarity_order = ['Common', 'Rare', 'Epic', 'Legendary', 'Forza Edition']  # Ordine logico se presente
# Filtriamo l'ordine solo con le label presenti nel dataset
present_rarity = [r for r in rarity_order if r in cards['rarity'].unique()]
# Se le etichette sono numeri (es. 1,2,3...), usa value_counts normale
sns.countplot(data=cards, x='rarity', palette='viridis', order=present_rarity)
plt.title("Distribuzione per Rarità")
plt.savefig(os.path.join(OUTPUT_DIR, "analisi_rarity.png"))
plt.close()

# D. COUNTRY (Bar Chart)
plt.figure(figsize=(12, 6))
country_counts = cards['country'].value_counts()
sns.barplot(x=country_counts.index, y=country_counts.values, palette='coolwarm')
plt.title("Distribuzione per Nazione")
plt.xticks(rotation=45)
plt.ylabel("Numero di Auto")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "analisi_country.png"))
plt.close()

# E. DRIVETRAIN (Se esiste la colonna)
if 'drivetrain' in cards.columns:
    plt.figure(figsize=(8, 6))
    sns.countplot(data=cards, x='drivetrain', palette='magma')
    plt.title("Distribuzione per Trazione (Drivetrain)")
    plt.savefig(os.path.join(OUTPUT_DIR, "analisi_drivetrain.png"))
    plt.close()
else:
    print("ATTENZIONE: Colonna 'drivetrain' non trovata nel CSV. Salto il grafico relativo.")

# ---------------------------------------------------------
# SIMULAZIONE PARTITE (Codice Originale Adattato)
# ---------------------------------------------------------

# --- CONFIG ---
TRIALS = 10000
RNG_SEED = 12345

turn_defs = {
    1: {'classes': ['D', 'C'], 'pi_range': (100, 600), 'weights': [0.70, 0.30], 'energy': 1330},
    2: {'classes': ['D', 'C', 'B', 'A'], 'pi_range': (300, 750), 'weights': [0.20, 0.25, 0.40, 0.15], 'energy': 1875},
    3: {'classes': ['D', 'C', 'B', 'A', 'S1'], 'pi_range': (450, 850), 'weights': [0.05, 0.10, 0.40, 0.30, 0.15],
        'energy': 2150},
    4: {'classes': ['C', 'B', 'A', 'S1', 'S2'], 'pi_range': (550, 950), 'weights': [0.05, 0.15, 0.35, 0.30, 0.15],
        'energy': 2440},
    5: {'classes': ['B', 'A', 'S1', 'S2'], 'pi_range': (650, 998), 'weights': [0.05, 0.10, 0.45, 0.40], 'energy': 2680},
}

# Normalizzazione Colonne per simulazione
df = cards.copy()
if 'class' not in df.columns:
    # Fallback se la colonna class non esiste
    if 'car_class' in df.columns:
        df['class'] = df['car_class']
    else:
        print("Warning: colonna 'class' non trovata per la simulazione.")

if 'PI' not in df.columns and 'pi' in df.columns:
    df['PI'] = df['pi']

df['class'] = df['class'].astype(str)
df['PI'] = pd.to_numeric(df['PI'], errors='coerce')

# Precompute pools
pools_pi = {}
fallback_pi = {}
for t, info in turn_defs.items():
    lo, hi = info['pi_range']
    pools_pi[t] = {}
    for cls in info['classes']:
        pools_pi[t][cls] = df[(df['class'] == cls) & (df['PI'] >= lo) & (df['PI'] <= hi)]['PI'].values
    fallback_pi[t] = df[(df['PI'] >= lo) & (df['PI'] <= hi)]['PI'].values

rng = np.random.default_rng(RNG_SEED)
summary = []

for t, info in turn_defs.items():
    classes = info['classes']
    weights = np.array(info['weights'], dtype=float)
    weights = weights / weights.sum()
    energy = info['energy']
    lo, hi = info['pi_range']

    available_classes = [c for c in classes if pools_pi[t][c].size > 0]
    if len(available_classes) == 0:
        available_classes = classes.copy()

    avail_weights = np.array([weights[classes.index(c)] for c in available_classes], dtype=float)
    avail_weights = avail_weights / avail_weights.sum()
    class_arrays = [pools_pi[t][c] for c in available_classes]

    sums = np.empty(TRIALS)
    chosen_class_counts = {c: 0 for c in classes}
    over_count = 0

    for i in range(TRIALS):
        total = 0.0
        for k in range(3):
            cls_idx = rng.choice(len(available_classes), p=avail_weights)
            chosen_class = available_classes[cls_idx]
            chosen_class_counts[chosen_class] += 1
            arr = class_arrays[cls_idx]
            if arr.size > 0:
                total += float(arr[rng.integers(0, arr.size)])
            else:
                fb = fallback_pi[t]
                if fb.size > 0:
                    total += float(fb[rng.integers(0, fb.size)])
                else:
                    if df.shape[0] > 0:
                        total += float(df['PI'].values[rng.integers(0, df.shape[0])])
        sums[i] = total
        if total > energy:
            over_count += 1

    mean_sum = sums.mean()
    std_sum = sums.std()
    p_over = over_count / TRIALS * 100.0
    summary.append((t, energy, mean_sum, std_sum, p_over, chosen_class_counts))

    # Plot histogram simulazione
    plt.figure(figsize=(8, 5))
    plt.hist(sums, bins=40, color='green', alpha=0.7)
    plt.axvline(energy, color='red', linestyle='dashed', linewidth=2, label=f'Limite Energia ({energy})')
    plt.title(f"Turn {t} - Somma 3 carte (Energy cap={energy})")
    plt.xlabel("Somma PI")
    plt.ylabel("Frequenza")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, f"simulazione_turno_{t}.png"))
    plt.close()

summary_df = pd.DataFrame([{
    'turn': s[0],
    'energy': s[1],
    'mean_sum': s[2],
    'std_sum': s[3],
    'p_overflow_percent': s[4],
    'suggested_energy': s[2] + (0.5*s[3])
} for s in summary]).set_index('turn')

print("\n--- RISULTATI SIMULAZIONE ---")
print(summary_df)
print("\nGenerazione grafici completata nella cartella 'graphs'.")