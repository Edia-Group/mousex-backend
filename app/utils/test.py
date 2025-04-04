import random
import string

def generate_distinct_variations(risposta, num_options=4):
    variations = []
    seen = {risposta}
    
    while len(variations) < num_options:
        modified = list(risposta)

        if len(risposta) < 6:
            indices_to_change = range(len(risposta))
        else:
            num_to_change = (len(risposta) + 1) // 2  # At least half, rounded up
            indices_to_change = random.sample(range(len(risposta)), num_to_change)
        
        for i in indices_to_change:
            char = modified[i]
            if char.isdigit():
                pool = [d for d in string.digits if d != char]
            elif char.isalpha():
                pool = [l for l in string.ascii_letters if l != char]
            else:
                continue
            
            modified[i] = random.choice(pool)
        
        modified_str = "".join(modified)
        if modified_str not in seen:
            variations.append(modified_str)
            seen.add(modified_str)
    
    random_position = random.randint(0, len(variations))
    variations.insert(random_position, risposta)
    
    return variations