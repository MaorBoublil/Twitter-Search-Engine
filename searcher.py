from parser_module import Parse
from ranker import Ranker
from utils import load_obj

POSTING_PATH = "PostingFiles/" #TODO: configuration this


class Searcher:

    def __init__(self, docs):
        """
        :param inverted_index: dictionary of inverted index
        """
        self.parser = Parse()
        self.ranker = Ranker()
        self.term_dict,self.document_dict = docs


    def relevant_docs_from_posting(self, query):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query: query
        :return: dictionary of relevant documents.
        """
        query_terms = self.parser.parse_query(query)

        buckets = {}
        for term in query_terms:
            # Add to bucket search list
            bucket_id = self.term_dict[term][3]
            tmp_list = buckets.get(bucket_id, [])
            tmp_list.append((term, self.term_dict[term][0]))
            buckets[bucket_id] = tmp_list

        # Create doc and terms to return
        return_term_dict = {}
        return_doc_dict = {}
        for bucket_id in buckets:
            posting_file = load_obj(POSTING_PATH + bucket_id)
            for term, all_tweets in buckets[bucket_id]:
                term_postings = []
                for tweet_id in all_tweets:
                    term_postings.append(posting_file[(term, tweet_id)])
                    if tweet_id not in return_doc_dict:
                        return_doc_dict[tweet_id] = self.document_dict[tweet_id]
                return_term_dict[term] = (term_postings)  # TODO: check if need more parameters


        # posting = utils.load_obj("posting")
        # relevant_docs = {}
        # for term in query:
        #     try:  # an example of checks that you have to do
        #         posting_doc = posting[term]
        #         for doc_tuple in posting_doc:
        #             doc = doc_tuple[0]
        #             if doc not in relevant_docs.keys():
        #                 relevant_docs[doc] = 1
        #             else:
        #                 relevant_docs[doc] += 1
        #     except:
        #         print('term {} not found in posting'.format(term))
        # return relevant_docs
