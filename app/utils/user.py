from sqlalchemy.orm import Session
from sqlalchemy import func as sqlfunc
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

    return domande