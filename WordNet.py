from nltk.corpus import wordnet
class WordNet():

    @staticmethod
    def expand_query(query):
        query_list = [term for term in query.split(" ")]
        query_sysnets = []
        lower_set = set()
        # Get the first synset with the same name as term
        for term in query_list:
            lower_term = term.lower()
            lower_set.add(lower_term)
            syns = wordnet.synsets(lower_term)
            if len(syns) == 0: continue
            for synset in syns:
                if synset._name.partition('.')[0] == lower_term:
                    query_sysnets.append(synset)
                    break
        # Get all relevant lemmas - query expansion
        for synset in query_sysnets:
            for lemma in synset._lemmas:
                if lemma._name.lower() in lower_set or "_" in lemma._name: continue
                counter = 0
                for compare_synset in query_sysnets:
                    # expand the query only if lemma is similar to two or more terms in the query
                    similarity = lemma._synset.wup_similarity(compare_synset)
                    if similarity is not None and similarity > 0.3:
                        counter += 1
                        if counter == 2:
                            query_list.append(lemma._name)
                            break
        return ' '.join(query_list)