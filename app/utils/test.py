import random
import string

def generate_distinct_variations(risposta, num_options=4, max_attempts=200):
    
    variations = []
    seen = {risposta}
    attempts = 0

    while len(variations) < num_options and attempts < max_attempts:
        modified = list(risposta)
        num_to_change = min((len(risposta) + 1) // 2, len(risposta))

        if num_to_change > 0:
            indices_to_change = random.sample(range(len(risposta)), num_to_change)

            for i in indices_to_change:
                char = modified[i]
                if char.isdigit():
                    pool = [d for d in string.digits if d != char]
                else:
                    pool = [l for l in string.ascii_letters if l != char]
                
                if pool: 
                  modified[i] = random.choice(pool)

        modified_str = "".join(modified)

        if modified_str not in seen:
            variations.append(modified_str)
            seen.add(modified_str)
        attempts += 1

    if risposta not in variations:
        variations.append(risposta)

    random.shuffle(variations)
    return variations[:num_options+1] 