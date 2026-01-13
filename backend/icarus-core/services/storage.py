# En backend/icarus-core/services/storage.py
import pandas as pd

def cargar_configuracion_negociacion():
    # Lee tu archivo de estrategias y anchor points
    df = pd.read_excel('data/raw/datos_ia.ods', engine='odf')
    return df.to_dict()
