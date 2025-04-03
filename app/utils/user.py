from sqlalchemy.orm import Session
from sqlalchemy import func as sqlfunc
import random
from app.models.domanda import Domanda

def get_random_domande_variante(db: Session):
    domande = (
        db.query(Domanda)
        .order_by(sqlfunc.random())
        .all()
    )
    random.shuffle(domande)
    return get_unique_domande(domande[:55])

def get_unique_domande(domande : list[Domanda]):
    rand_limit_domande = random.randint(12,15)
    domande_body = []
    domande_unique = []
    for domanda in domande:
        if domanda.corpo not in domande_body:
            domande_body.append(domanda.corpo)
            domande_unique.append(domanda)
    return assign_page(domande_unique[:rand_limit_domande])

def assign_page(domande : list[Domanda]):
    total_page = random.randint(1, 2)
    for index, domanda in enumerate(domande):
        domanda.numero_pagina = index % (total_page + 1)
    
    return sorted(domande, key=lambda x: x.numero_pagina)