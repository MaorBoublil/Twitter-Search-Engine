import re
from nltk.corpus import stopwords
from document import Document

# TODO: stemmer
# TODO: capital letters
# TODO: entities detector
# TODO: unicode 126

class Parse:

    def __init__(self):
        self.stop_words = stopwords.words(
            'english')  # TODO:remove RT, http, https, www etc. (we will see after inv-index
        self.nonstopwords = 0
        self.max_tf = 0

    def parse_sentence(self, text):
        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        :param text:
        :return:
        """
        term_dict = {}
        # text_tokens = word_tokenize(text) #TODO: is RE Faster? add to doh
        text_tokens = re.findall("[A-Z]{2,}(?![a-z])|[A-Z][a-z]+(?=[A-Z])|@[\'\w\-]+|#[\'\w\-]+|[\'\w\-]+", text)  #TODO: add digits and etc. - currently missing from doc
        indices_counter = 0
        for term in text_tokens:
            indices_counter += 1
            if term[0] == "#":
                hashtag_list = self.hashtag_parser(term)
                for mini_term in hashtag_list:
                    self.dictAppender(term_dict, indices_counter, mini_term)
            elif term[0] == "@" or term.lower() not in self.stop_words:
                self.dictAppender(term_dict, indices_counter, term)

        return term_dict, indices_counter

    def split_url(self, url):
        url_list = list(filter(None, re.split("://|\?|/|=|(?<=www).", url)))
        return url_list

    def remove_percent(self, text):
        return re.sub('(?<=\d) *percentage|(?<=\d) *percent', "%", text)

    def num_manipulation(self, num):
        # TODO: Add to DOH 2020(year example), 1000M to 1B?!
        num = re.sub(r'(?<=\d|.) *Billion|(?<=\d|.) *billion', "B", num)
        num = re.sub(r'(?<=\d|.) *Million|(?<=\d|.) *million', "M", num)
        num = re.sub(r'(?<=\d|.) *Thousand|(?<=\d|.) *thousand', "K", num)
        num = re.sub(r'([0-9]+)(,{0,1})([0-9]{3})(,{0,1})([0-9]{3})(,{0,1})([0-9]{3})', r'\1.\3B', num)
        num = re.sub(r'([0-9]+)(,{0,1})([0-9]{3})(,{0,1})([0-9]{3}).*([0-9]*)', r'\1.\3M', num)
        num = re.sub(r'([0-9]+)(,{0,1})([0-9]{3})($|(.[0-9]*)$)', r'\1.\3K', num)
        num = re.sub(r'([0-9]+).([0]*)([1-9]{0,3})([0]*)(K|M|B)', r'\1.\2\3\5', num)
        return re.sub(r'([0-9]{1,3}).([0]{3})(K|M|B)', r'\1\3', num)

    def url_parser(self, url):
        """
        :param url: recieves a string based dictionary of all urls
        :return: dictionary with parsed urls
        """
        try: url_dict = eval(url)  # convert string to dictionary
        except: url_dict = eval(re.sub(r'null', '""', url))

        finalList = []
        for val in url_dict.values():
            # TODO: key url is not needed - add to doh
            finalList += self.split_url(val)
        return finalList

    def hashtag_parser(self, hashtag):
        splitted_hashtag = map(lambda x: x.lower(),
                               filter(lambda x: len(x) > 0, re.split(r'_|(?<=[^A-Z])(?=[A-Z])', hashtag)))
        return list(splitted_hashtag)[1:] + [hashtag.lower()]

    def dictAppender(self, d, counter, term):
        self.nonstopwords += 1
        tmp_lst = d.get(term, [])
        tmp_lst.append(counter)
        d[term] = tmp_lst
        if self.max_tf < len(tmp_lst):
            self.max_tf = len(tmp_lst)

    def parse_doc(self, doc_as_list):
        """doc_as_list[3]
        This function takes a tweet document as list and break it into different fields
        :param doc_as_list: list re-preseting the tweet.
        :return: Document object with corresponding fields.
        """
        tweet_id = doc_as_list[0]
        tweet_date = doc_as_list[1]
        full_text = doc_as_list[2]
        url = doc_as_list[3]
        # indices = doc_as_list[4]
        retweet_text = doc_as_list[5]
        retweet_url = doc_as_list[6]
        # retweet_indices = doc_as_list[7]
        quote_text = doc_as_list[8]
        quote_url = doc_as_list[9]
        # quote_indices = doc_as_list[10]
        # retweet_quote_text = doc_as_list[11]
        # retweet_quote_url = doc_as_list[12]
        # retweet_quote_indices = doc_as_list[13]

        self.nonstopwords = 0
        self.max_tf =0
        docText = full_text
        if quote_text:
            docText += quote_text
        docText = self.num_manipulation(docText)  # TODO: CHECK IF OK
        docText = self.remove_percent(docText)

        tokenized_dict, indices_counter = self.parse_sentence(docText)

        urlTermList = self.url_parser(url)  # TODO maybe add another url
        for term in urlTermList:
            indices_counter += 1
            self.dictAppender(tokenized_dict, indices_counter, term)

        doc_length = self.nonstopwords  # after text operations.

        document = Document(tweet_id, tweet_date, full_text, url, retweet_text, retweet_url, quote_text,
                            quote_url, tokenized_dict, doc_length, self.max_tf)
        return document
