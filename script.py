from datetime import datetime
from haversine import haversine, Unit
import pandas as pd

from helpers import heure_en_minute

# Exemple de données de véhicules (doit être récupéré depuis une base de données ou une API)
vehicules = {
        'immatriculation' : 'IMMAT_5',
        'vehicle_status': 'not_parked', #[parked, move]
        'coordinate': (4.7128, 9.9360), #(LATITUDE, LONGITUDE)
        'vitesse_interval' : {'min':30, 'max':55} #km/h
}


# Fonction pour le calcule du temps estime pour parquer dans un de ces points habituels
def calculer_temps_estimee(vehicle, list_parkings, checking_time):
    temps_estimer_mn = dict()

    for latitude, longitude, pluscode in zip(list_parkings['lat'], list_parkings['lng'], list_parkings['lieu_x']):

        distance = haversine((vehicle['coordinate']), (latitude, longitude), unit=Unit.KILOMETERS)
        print(distance)
        temps_estimer_mn[pluscode] = {
            'min' : (distance / vehicle['vitesse_interval']['max'])  * 60 + checking_time,
            'max' : (distance / vehicle['vitesse_interval']['min'])  * 60 + checking_time
        }
    
    
    return temps_estimer_mn


def probabilite_estime_de_parquer_dans_le_temps(temps_estimer_mn, list_parkings):

    probabilite_de_parquer = dict()

    for pluscode, plage_min, plage_max in zip(temps_estimer_mn.keys(), list_parkings['plage_min'], list_parkings['plage_max']):

        if(temps_estimer_mn[pluscode]['min'] >= plage_max):
            probabilite_de_parquer[pluscode] = 0

        if(temps_estimer_mn[pluscode]['max']<= plage_min or (temps_estimer_mn[pluscode]['min'] >= plage_min and temps_estimer_mn[pluscode]['max'] <= plage_max)):
            probabilite_de_parquer[pluscode] = 1


        if(plage_min<= temps_estimer_mn[pluscode]['min'] <= plage_max and temps_estimer_mn[pluscode]['max'] >= plage_max):
            probabilite_de_parquer[pluscode] = (plage_max - temps_estimer_mn[pluscode]['min']) / (temps_estimer_mn[pluscode]['max'] - temps_estimer_mn[pluscode]['min'])

    return probabilite_de_parquer



def application_proba_parking (day , vehicule, checking_time):
    hebdo_data = pd.read_excel(f"model_save/{vehicule['immatriculation']}/stats/{day}.xlsx")

    detail_data = pd.read_excel(f"model_save/{vehicule['immatriculation']}/details.xlsx")

    data = pd.merge(hebdo_data, detail_data, left_on='lieu', right_on='pluscode')

    data["heure_moyenne_entre"] = data["heure_moyenne_entre"].apply(heure_en_minute)
    data["heure_moyenne_sortie"] = data["heure_moyenne_sortie"].apply(heure_en_minute)

    data['plage_min'] = data["heure_moyenne_entre"] - data['marge_heure_entre'].apply(int)
    data['plage_max'] = data["heure_moyenne_entre"] + data['marge_heure_entre'].apply(int)

    data['plage_min_s'] = data["heure_moyenne_sortie"] - data['marge_heure_sortie'].apply(int)
    data['plage_max_s'] = data["heure_moyenne_sortie"] + data['marge_heure_sortie'].apply(int)

    temps_estimer = calculer_temps_estimee(vehicule, data, checking_time)
    probabilite_estimer = probabilite_estime_de_parquer_dans_le_temps(temps_estimer, data)

    return probabilite_estimer


current_time = datetime.now().time()
current_time = current_time.hour * 60 + current_time.minute + int(current_time.second / 60)


probabilite_estimer = application_proba_parking('Lundi', vehicules, current_time)

print(probabilite_estimer)