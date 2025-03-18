from sqlalchemy.orm import Session
from sqlalchemy import func as sqlfunc
from app.models.variante import Variante
import random
from app.models.domanda import Domanda

def get_random_domande_variante(db: Session):

    rand_limit_domande = random.randint(13,18)
    domande = (
        db.query(Domanda)
        .order_by(sqlfunc.random())
        .limit(rand_limit_domande)
        .all()
    )

    domanda_ids = [domanda.idDomanda for domanda in domande]
    varianti = db.query(Variante).filter(Variante.domanda_id.in_(domanda_ids)).all()
    varianti_grouped = {}
    for variante in varianti:
        if variante.domanda_id not in varianti_grouped:
            varianti_grouped[variante.domanda_id] = []
        varianti_grouped[variante.domanda_id].append(variante)
    result_dict = {}
    for domanda in domande:
        if domanda.idDomanda in varianti_grouped.keys():
            result_dict[domanda.corpo] = {
                "variante": random.choice(varianti_grouped[domanda.idDomanda]),
                "tipo": domanda.tipo
            }
    return result_dict