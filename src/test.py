import app
p = app.get_pronounciations()
d = app.get_phoneme_distances()

test_words = {}
test_words['putter'] = app.word_to_phonemes("PUTTER") 
test_words['potter'] = app.word_to_phonemes("POTTER") 
test_words['punter'] = app.word_to_phonemes("PUNTER") 
test_words['water'] = app.word_to_phonemes("WATER") 
test_words['painter'] = app.word_to_phonemes("PAINTER") 
test_words['mutter'] = app.word_to_phonemes("MUTTER") 
test_words['butter'] = app.word_to_phonemes("BUTTER") 
test_words['butterscotch'] = app.word_to_phonemes("BUTTERSCOTCH")
test_words['rutabaga'] = app.word_to_phonemes("RUTABAGA")

for k in test_words.keys():
    print(k + ": " + str(test_words[k]) + "\n")

print("DISTANCES:\n")

#Yes, I know this is doing each distance twice. I'm testing to make sure
#   the distances are symmetrical. I'm about 80% they're supposed to be.
for k in test_words.keys():
    print(k + ":")
    for w in test_words.keys():
        print("\t" + w + ": " + str(app.alignment_score(test_words[k], test_words[w], d)) + "\n")
