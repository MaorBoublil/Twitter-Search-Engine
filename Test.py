from nltk.corpus import wordnet
from parser_module import Parse
p = Parse(False)
query = 'Wearing a mask to prevent the spread of COVID-19 is unnecessary because the disease can also be spread via farts'
x = p.remove_stopwords(query)
query_list = [term for term in x.split(" ")]
print(query_list)
query_sysnets = []
lower_set = set()
for term in query_list:
    lower_term = term.lower()
    lower_set.add(lower_term)
    syns = wordnet.synsets(lower_term)
    if len(syns) == 0 : continue
    for synset in syns:
        if synset._name.partition('.')[0] == lower_term:
            query_sysnets.append(synset)
            break
lemmas = []
l = []
for synset in query_sysnets:
    for lemma in synset._lemmas:
        if lemma._name.lower() in lower_set or "_" in lemma._name: continue
        counter = 0
        lemmas.append(lemma._name)
        for compare_synset in query_sysnets:
            similarity = lemma._synset.wup_similarity(compare_synset)
            if similarity is not None and similarity > 0.3:
                l.append((lemma._name,compare_synset._name,similarity))
                counter+=1
                if counter == 2:
                    query_list.append(lemma._name)
                   # break

print(lemmas)
print(l)
print(query_list)