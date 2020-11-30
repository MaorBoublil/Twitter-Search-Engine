class Document:

    def __init__(self, tweet_id, full_text=None,term_doc_dictionary=None, doc_length=0, max_tf=1, entities_dict=None):
        """
        :param tweet_id: tweet id
        :param tweet_date: tweet date
        :param full_text: full text as string from tweet
        :param url: url
        :param retweet_text: retweet text
        :param retweet_url: retweet url
        :param quote_text: quote text
        :param quote_url: quote url
        :param term_doc_dictionary: dictionary of term and documents.
        :param doc_length: doc length
        """

        self.tweet_id = tweet_id
        self.full_text = full_text
        self.term_doc_dictionary = term_doc_dictionary
        self.doc_length = doc_length
        self.unique_words_count = len(term_doc_dictionary)
        self.max_tf = max_tf
        self.entities = entities_dict
