from nltk.corpus import wordnet
x = [x.lemmas()[0].name() for x in wordnet.synsets("people")]
print(x.lemmas()[0].name() for x in wordnet.synsets("people"))