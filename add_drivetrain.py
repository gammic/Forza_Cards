import pandas as pd

# 1. CARICAMENTO DATI
# ---------------------------------------------------------
df_mio = pd.read_csv('db_cleaned.csv')
df_kaggle = pd.read_csv('Forza_Horizon_Cars.csv')  # Inserisci qui il nome del file Kaggle


# 2. PREPARAZIONE LOOKUP (Dizionario di ricerca)
# ---------------------------------------------------------
# Funzione per pulire le stringhe e facilitare il match
def normalizza_chiave(testo):
    return str(testo).lower().replace(" ", "").replace("'", "").replace("-", "")


kaggle_lookup = {}

# Mappa per convertire i valori di Kaggle nei tuoi standard (se necessario)
# Esempio: se Kaggle usa "Rear" e tu vuoi "RWD"

if not df_kaggle.empty:
    # ATTENZIONE: Cambia 'Car Name' e 'Drive' con i nomi reali delle colonne nel file Kaggle
    colonna_nome_kaggle = 'Name_and_model'
    colonna_trazione_kaggle = 'Drive_Type'

    for index, row in df_kaggle.iterrows():
        # Creo una chiave unica unendo nome o costruttore+modello
        # Se Kaggle ha costruttore e modello separati:
        # chiave = normalizza_chiave(str(row['Make']) + str(row['Model']))

        # Se Kaggle ha tutto nel nome:
        chiave = normalizza_chiave(row[colonna_nome_kaggle])

        drive = row[colonna_trazione_kaggle]
        kaggle_lookup[chiave] = drive

# 3. DEFINIZIONE REGOLE EURISTICHE (Il "Piano B")
# ---------------------------------------------------------
type_to_drivetrain = {
    'Classic Muscle': 'RWD', 'Retro Muscle': 'RWD', 'Modern Muscle': 'RWD',
    'Rods & Customs': 'RWD', 'Drift Cars': 'RWD', 'Classic Racers': 'RWD',
    'Vintage Racers': 'RWD', 'Classic Sports Cars': 'RWD', 'Retro Sports Cars': 'RWD',
    'Track Toys': 'RWD', 'GT Cars': 'RWD', 'Super GT': 'RWD', 'Hypercars': 'RWD',
    'Hot Hatch': 'FWD', 'Retro Hot Hatch': 'FWD',
    'Rally Monsters': 'AWD', 'Modern Rally': 'AWD', 'Retro Rally': 'AWD',
    'Unlimited Offroad': 'AWD', 'Pickups & 4x4s': 'AWD', 'Offroad': 'AWD',
    'Sports Utility Heroes': 'AWD', 'UTVs': 'AWD', 'Trucks': 'AWD', 'Buggies': 'RWD'
}


def get_drivetrain_smart(row):
    # A. TENTATIVO MATCH CON KAGGLE
    # Costruisco la chiave usando i tuoi dati: 'man' + 'model'
    chiave_mia = normalizza_chiave(str(row['year']) + str(row['man']) + str(row['model']))

    if chiave_mia in kaggle_lookup:
        drive = kaggle_lookup[chiave_mia]
        if drive != "info_not_found":
            print(f"auto {chiave_mia} trovata nel dataset")
            return drive  # Trovato nel dataset affidabile!

    # B. ANALISI DEL NOME (Se Kaggle fallisce)
    name_upper = (str(row['name']) + " " + str(row['model'])).upper()
    if any(x in name_upper for x in ['QUATTRO', '4WD', '4X4', 'AWD', 'EVO', 'WRX', 'INTEGRALE']):
        return 'AWD'

    # C. ANALISI CATEGORIA
    if row['type'] in type_to_drivetrain:
        print(f"auto {chiave_mia} dedotta trazione")
        return type_to_drivetrain[row['type']]

    # D. CASO DISPERATO
    print(f"auto {chiave_mia} boh")
    drive = input()
    return drive  # Da guardare a mano


# 4. ESECUZIONE
# ---------------------------------------------------------
df_mio['drivetrain'] = df_mio.apply(get_drivetrain_smart, axis=1)

# Statistiche finali
print(f"Totale auto: {len(df_mio)}")
print(f"Trazione assegnata: {df_mio['drivetrain'].value_counts()}")
print("\nPrime 5 righe:")
print(df_mio[['name', 'type', 'drivetrain']].head())

# Salvataggio
df_mio.to_csv('db_completo_con_trazione.csv', index=False)
