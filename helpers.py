def heure_en_minute(temps):
    # Décomposer l'heure en heures, minutes et secondes
    
    h, m, s = temps.split(":")
    
    # Convertir chaque composante en secondes et calculer le total
    total_secondes = int(h) * 60 + int(m) + round(int(s)/60)
    
    return total_secondes