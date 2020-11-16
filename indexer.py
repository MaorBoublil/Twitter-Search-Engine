class Indexer:

    def __init__(self, config):
        self.inverted_idx = {}
        self.document_dict = {}
        self.postingDict = {}
        self.config = config

    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """
        self.document_dict[document.tweet_id] = (document.doc_length, document.max_tf, document.unique_words_count)
        document_dictionary = document.term_doc_dictionary
        # Go over each term in the doc
        for term in document_dictionary.keys():
            try:
                # Updating term dictionary
                if term not in self.inverted_idx.keys():
                    self.inverted_idx[term] = [[document.tweet_id], 1, len(document_dictionary[term]), "b1"]
                    # self.postingDict[term] = []
                else:
                    term_rec = self.inverted_idx[term]
                    term_rec[0].append(document.tweet_id)
                    term_rec[1] += 1
                    term_rec[2] += len(document_dictionary[term])
                    self.inverted_idx[term] = term_rec

                self.postingDict[term].append((document.tweet_id, len(document_dictionary[term])))

            except:
                print('problem with the following key {}'.format(term[0]))
