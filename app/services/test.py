from app.utils.test import generate_distinct_variations
from app.models.testgroup import TestsGroup
from app.models.user import User
from app.models.test import Test    
from app.schemas.domande import DomandaRisposta, DomandaOptions
from app.utils.user import get_random_domande_variante
from sqlalchemy.orm import Session

def generate_test(test_group: TestsGroup, user: User, db: Session): 

    new_test = Test.create(
        id=user.id, 
        secondi_ritardo=test_group.secondi_ritardo,
        tipo=test_group.tipo,
        db=db
    )

    domande_with_options = []
    domande = get_random_domande_variante(db)
    for domanda in domande:
        opzioni = generate_distinct_variations(domanda.risposta_esatta)
        domande_with_options.append(
            DomandaOptions(
                domanda=domanda,
                varianti=opzioni
            )
        )
        
    return DomandaRisposta(
        domande=domande_with_options, test_id=new_test.id_test, data_ora_inizio=new_test.data_ora_inizio
    ) 