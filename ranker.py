import numpy as np

class Ranker:

    def __init__(self, searcher):
        self.searcher = searcher


    def rank_relevant_docs(self,relevant_docs):
        """
        This function provides rank for each relevant document and sorts them by their scores.
        The current score considers solely the number of terms shared by the tweet (full_text) and query.
        :param relevant_doc: dictionary of documents that contains at least one term from the query.
        :return: sorted list of documents by score
        """
        posting_files, doc_set, query_terms, term_dict = relevant_docs

        # Creating Matrix
        doc_map = {tweet_id: inx for inx, tweet_id in enumerate(doc_set)}
        term_map = {term: inx for inx, term in enumerate(query_terms)}
        query_len = len(query_terms)
        number_of_docs = len(doc_set)
        matrix = np.zeros((number_of_docs, query_len))
        query_vector = np.zeros((query_len, 1))
        query_weight = 0

        for term in query_terms:
            docs = term_dict[term][0]
            j = term_map[term]
            w_iq = term_dict[term][4] * query_terms[term]
            query_weight += w_iq ** 2
            query_vector[j, 0] = w_iq
            for tweet_id in docs:
                w_ij = posting_files[(term, tweet_id)][2]
                i = doc_map[tweet_id]
                matrix[i, j] = w_ij

        query_weight = query_weight ** 0.5
        document_vector = np.dot(matrix, query_vector)
        doc_size_vector = np.zeros((number_of_docs, 1))
        for tweet_id, indx in doc_map.items():
            doc_size_vector[indx, 0] = (self.searcher.get_doc_length(tweet_id) ** 0.5) * query_weight
        ranking = np.transpose(np.divide(document_vector, doc_size_vector)).tolist()[0]

        ranked_tweets = [(x,y) for x,y in zip (doc_map,ranking)]

        return sorted(ranked_tweets,key= lambda x: x[1],reverse=True)


    def retrieve_top_k(self, sorted_relevant_doc, k=1):
        """
        return a list of top K tweets based on their ranking from highest to lowest
        :param sorted_relevant_doc: list of all candidates docs.
        :param k: Number of top document to return
        :return: list of relevant document
        """
        return sorted_relevant_doc[:k]
