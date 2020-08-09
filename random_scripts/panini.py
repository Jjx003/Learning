panini_bible = "The quick brown fox jumps over the lazy dog"
panini_bet = list(set(panini_bible.strip()))
panini_strength = 6

def check_panini(panini_test):
    return panini_test != None and panini_test == "panini"

def panini_panini(panini_depth, panini_test):
    if panini_depth == panini_strength:
        return panini_test if check_panini(panini_test) else None

    for panini_piece in panini_bet:
        panini_craft = panini_panini(panini_depth+1,panini_test+panini_piece)
        if check_panini(panini_craft):
            return panini_craft

    return None

if __name__ == "__main__":
    print(panini_panini(0,""))
