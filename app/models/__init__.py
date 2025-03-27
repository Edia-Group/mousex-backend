from .user import User
from .domanda import Domanda
from .variante import Variante
from .test import Test
from .testgroup import TestsGroup
from .statistiche import Statistiche
from .testAdmin import TestAdmin
from .testPrefattGroup import TestPrefattiGroup
__all__ = [
    "User", "Statistiche",
    "TestsGroup", "Domanda",
    "Variante",
    "Test","TestAdmin", "TestPrefattiGroup"
]