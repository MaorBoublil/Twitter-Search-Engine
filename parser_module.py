import re
from nltk.corpus import stopwords
from document import Document
from stemmer import Stemmer
from configuration import ConfigClass
from utils import save_obj,load_obj

BILLION_PATTERN = r'(?<=\d|.) *Billion|(?<=\d|.) *billion'
MILLION_PATTERN = r'(?<=\d|.) *Million|(?<=\d|.) *million'
THOUSAND_PATTERN = r'(?<=\d|.) *Thousand|(?<=\d|.) *thousand'
BILLION_PATTERN_NUM = r'([0-9]+)(,{0,1})([0-9]{3})(,{0,1})([0-9]{3})(,{0,1})([0-9]{3})'
MILLION_PATTERN_NUM = r'([0-9]+)(,{0,1})([0-9]{3})(,{0,1})([0-9]{3})'
THOUSAND_PATTERN_NUM = r'([0-9]+)(,{0,1})([0-9]{3})'
GENERAL_PATTERN = r'([0-9]+).([0]*)([1-9]{0,3})([0]*)(K|M|B)'
DECIMAL_PATTERN = r'([0-9]{1,3}).([0]{3})(K|M|B)'
PERCENT_PATTERN = r'(?<=\d) *((p|P)(e|E)(r|R)(c|C)(e|E)(n|N)(t|T)|(p|P)(e|E)(r|R)(c|C)(e|E)(n|N)(t|T)(a|A)(g|G)(e|E)|%)'
DOLLAR_PATTERN = r'(?<=\d) *((d|D)(o|O)(l|L)(l|L)(a|A)(r|R)(s|S)*|$)'
SPLIT_URL_PATTERN = "://|\?|/|=|-|(?<=www)."
REMOVE_URL_PATTERN = r"http\S+"
HASHTAG_PATTERN = r'_|(?<=[^A-Z])(?=[A-Z])'
TWITTER_STATUS_PATTERN = r'(twitter.com\/)(\S*)(\/status\/)(\d)*'
TOKENIZER_PATTERN = r'''(?x)\d+\ +\d+\/\d+|\d+\/\d+|\d+\.*\d*(?:[MKB])*(?:[$%])|(?:[A-Z]\.)+| \w+(?:-\w+)*| \$?\d+(?:\.\d+)?%?'''


# TODO: entities detector
# TODO: add removement of ' (chukus)
# TODO: CHECK IF NEEDED TO REMOVE the at - at hashtags example THE DOLLAR
# TODO: 35 3/4 term

class Parse:

    def __init__(self):
        self.stop_words = stopwords.words('english')
        self.stop_words+= ["rt", "http", "https", "www","twitter.com"]# TODO:remove domain stop words. we will see after inv-index
        self.terms = set()
        self.nonstopwords = 0
        self.max_tf = 0
        self.toStem = ConfigClass().toStem
        if self.toStem:
            self.stemmer = Stemmer()

    def parse_sentence(self, text):
        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        :param text:
        :return:
        """
        term_dict = {}
        text_tokens = re.findall(TOKENIZER_PATTERN, text)
        indices_counter = 0
        for term in text_tokens:
            indices_counter += 1
            if term[0] == "#":
                hashtag_list = self.hashtag_parser(term)
                for mini_term in hashtag_list:
                    self.dictAppender(term_dict, indices_counter, mini_term)
            elif term[0] == "@":
                no_tag = self.tags_parser(term)
                self.dictAppender(term_dict, indices_counter, no_tag)
            self.dictAppender(term_dict, indices_counter, term)

        return term_dict, indices_counter

    def split_url(self, url):
        url_list = list(filter(None, re.split(SPLIT_URL_PATTERN, url)))
        return url_list

    def remove_percent_dollar(self, text):
        no_dollar = re.sub(DOLLAR_PATTERN,"$", text)
        return re.sub(PERCENT_PATTERN, "%", no_dollar)

    def num_manipulation(self,num):
        # TODO: Add to DOH 2020(year example), 1000M to 1B?!
        num = re.sub(BILLION_PATTERN, "B", num)
        num = re.sub(MILLION_PATTERN, "M", num)
        num = re.sub(THOUSAND_PATTERN, "K", num)
        num = re.sub(BILLION_PATTERN_NUM, r'\1.\3B', num)
        num = re.sub(MILLION_PATTERN_NUM, r'\1.\3M', num)
        num = re.sub(THOUSAND_PATTERN_NUM, r'\1.\3K', num)
        num = re.sub(GENERAL_PATTERN, r'\1.\2\3\5', num)
        return re.sub(DECIMAL_PATTERN, r'\1\3', num)

    def url_parser(self, url): # TODO: split by -
        """
        :param url: recieves a string based dictionary of all urls
        :return: dictionary with parsed urls
        """
        try: url_dict = eval(url)  # convert string to dictionary
        except: url_dict = eval(re.sub(r'null', '""', url))

        finalList = []
        for val in url_dict.values():
            # TODO: key url is not needed - add to doh
            if 'twitter.com/i/web/status/' in val:
                continue
            val = re.sub(TWITTER_STATUS_PATTERN,r'\2',val)
            print(val)
            finalList = self.split_url(val)
        return finalList

    def hashtag_parser(self, hashtag):
        splitted_hashtag = map(lambda x: x.lower(),
                               filter(lambda x: len(x) > 0, re.split(HASHTAG_PATTERN, hashtag)))
        return list(splitted_hashtag)[1:] + [hashtag.lower()]

    def tags_parser(self, tag):
        return tag[1:]

    def dictAppender(self, d, counter, term):
        # Handling Stemming
        if self.toStem:
            stemmed_word = self.stemmer.stem_term(term)
            if not term.islower():
                term = stemmed_word.upper()
            else:
                term = stemmed_word

        # Handling upper & lower cases per document
        term_lower = term.lower()
        if not all(ord(c) < 128 for c in term): return
        if term_lower in self.stop_words: return
        term_upper = term.upper()

        if not term.islower():  # upper
            term = term_upper
            if term_lower in self.terms:
                term = term_lower
        elif term_upper in self.terms:  # lower
            self.terms.remove(term_upper)
            upper_list = d[term_upper]
            d.pop(term_upper)
            d[term_lower] = upper_list
        self.terms.add(term)

        # Creating indices list
        self.nonstopwords += 1
        tmp_lst = d.get(term, [])
        tmp_lst.append(counter)
        d[term] = tmp_lst
        if self.max_tf < len(tmp_lst):
            self.max_tf = len(tmp_lst)

    def parse_doc(self, doc_as_list):  # Do NOT change signature
        """doc_as_list[3]
        This function takes a tweet document as list and break it into different fields
        :param doc_as_list: list re-preseting the tweet.
        :return: Document object with corresponding fields.
        """
        tweet_id = doc_as_list[0]
        tweet_date = doc_as_list[1]
        full_text = doc_as_list[2]
        url = doc_as_list[3]
        retweet_text = doc_as_list[5]
        retweet_url = doc_as_list[6]
        quote_text = doc_as_list[8]
        quote_url = doc_as_list[9]

        self.nonstopwords = 0
        self.max_tf =0
        docText = full_text
        if quote_text:
            docText += quote_text

        docText = re.sub(REMOVE_URL_PATTERN, "", docText)  # link removal
        docText = self.remove_percent_dollar(docText)
        docText = self.num_manipulation(docText)

        tokenized_dict, indices_counter = self.parse_sentence(docText)

        urlTermList = self.url_parser(url)
        for term in urlTermList:
            indices_counter += 1
            self.dictAppender(tokenized_dict, indices_counter, term)

        doc_length = self.nonstopwords  # after text operations.

        document = Document(tweet_id, tweet_date, full_text, url, retweet_text, retweet_url, quote_text,
                            quote_url, tokenized_dict, doc_length, self.max_tf)
        return document


    def parse_query(self,query): # return {term: ([indices,tf])}
        self.nonstopwords = 0
        self.max_tf =0
        docText = self.num_manipulation(query)  # TODO: CHECK IF OK
        docText = self.remove_percent_dollar(docText)

        tokenized_dict, indices_counter = self.parse_sentence(docText)
        return tokenized_dict
