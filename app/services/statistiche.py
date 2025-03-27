from app.models.statistiche import Statistiche
from sqlalchemy.orm import Session

def create_statistiche(db: Session, user_id: int):

    new_stats = list()
    stats = ['c','s','r','t','m']
    for stat in stats:
        new_stat = Statistiche(tipo_domanda=stat, nr_errori=0, utente_id=user_id)
        new_stats.append(new_stat)
        db.add(new_stat)
        db.commit()
        db.refresh(new_stat)