from parser_module import Parse
from ranker import Ranker
from utils import load_obj
import os

class Searcher:

    def __init__(self, docs, path):
        """
        :param inverted_index: dictionary of inverted index
        """
        self.ranker = Ranker(self)
        self.term_dict,self.document_dict = docs
        self.POSTING_PATH = path

    def get_doc_length(self, tweet_id):
        return self.document_dict[tweet_id][3]

    def relevant_docs_from_posting(self, parsed_query, parsed_entities):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query: {term:[indices]}
        :return: dictionary of relevant documents.
        """
        query_terms = {term:len(parsed_query[term]) for term in parsed_query}  # query terms is {term:tf}

        # preparing query terms as appear in dictionary
        terms = list(query_terms)
        for term in terms:
            if term not in self.term_dict:
                if term.isupper() and term.lower() in self.term_dict:
                    query_terms[term.lower()] = query_terms[term]
                    query_terms.pop(term)
                elif term.islower() and term.upper() in self.term_dict:
                    query_terms[term.upper()] = query_terms[term]
                    query_terms.pop(term)
                else:
                    query_terms.pop(term)

        # adding entities to query terms
        for entity in parsed_entities:
            if entity in self.term_dict:
                query_terms[entity] = parsed_entities[entity]

        doc_set = set()
        buckets = {}  # {BUCKET_ID : [TERMS AS TUPLES (TERM,[TWEETS])]}
        for term in query_terms:
            # Add to bucket search list
            bucket_id = self.term_dict[term][3]
            tmp_list = buckets.get(bucket_id, [])
            tmp_list.append((term, self.term_dict[term][0]))
            buckets[bucket_id] = tmp_list
            doc_set.update(self.term_dict[term][0])

        # Create doc and terms to return
        return_term_dict = {}
        return_postings = {}
        for bucket_id in buckets:
            posting_file = load_obj(self.POSTING_PATH + '/' + bucket_id)
            for term, all_tweets in buckets[bucket_id]:
                for tweet_id in all_tweets:
                    return_postings[(term, tweet_id)] = posting_file[(term, tweet_id)]
                return_term_dict[term] = self.term_dict[term]

        return return_postings, doc_set, query_terms, return_term_dict
