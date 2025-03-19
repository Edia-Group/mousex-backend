import random
from app.models.domanda import Domanda

def generate_distinct_variations(risposta, num_options = random.randint(5,11)):

  opzioni = []
  seen = {risposta}

  while len(opzioni) < num_options:
    modified_risposta = list(risposta)
    if len(risposta) > 0: #prevent error with empty string
      index_to_change = random.randint(0, len(risposta) - 1)
      modified_risposta[index_to_change] = random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")

    modified_str = "".join(modified_risposta)

    if modified_str not in seen:
      opzioni.append(modified_str)
      seen.add(modified_str)

  # Insert risposta at a random position in opzioni
  random_position = random.randint(0, len(opzioni))
  opzioni.insert(random_position, risposta)

  return opzioni