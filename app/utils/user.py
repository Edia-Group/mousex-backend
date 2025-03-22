from sqlalchemy.orm import Session
from sqlalchemy import func as sqlfunc
import random
from app.models.domanda import Domanda

def get_random_domande_variante(db: Session):

    domande = (
        db.query(Domanda)
        .order_by(sqlfunc.random())
        .limit(100)
        .all()
    )

    return get_unique_domande(domande)

def get_unique_domande(domande : list[Domanda]):
    rand_limit_domande = random.randint(12,15)
    domande_body = []
    domande_unique = []
    for domanda in domande:
        if domanda.corpo not in domande_body:
            domande_body.append(domanda.corpo)
            domande_unique.append(domanda)
    return domande_unique[:rand_limit_domande]