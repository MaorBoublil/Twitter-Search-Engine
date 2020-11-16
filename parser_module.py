import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from document import Document


class Parse:

    def __init__(self):
        self.stop_words = stopwords.words('english')

    def parse_sentence(self, text):
        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        :param text:
        :return:
        """
        # TODO: Percents, Numbers, Names and Entity's
        text = self.remove_percent(text)
        text = self.num_manipulation(text)
        text_tokens = word_tokenize(text)
        text_tokens_without_stopwords = [w.lower() for w in text_tokens if w not in self.stop_words]
        return text_tokens_without_stopwords

    def split_url(self, url):
        url_list = list(filter(None, re.split("://|\?|/|=|(?<=www).", url)))
        return url_list

    def remove_percent(self, text):
        return re.sub('(?<=\d) *percentage|(?<=\d) *percent', "%", text)

    def num_manipulation(self, num):
        # TODO: Add to DOH 2020(year example) and remove 0(round) 1000M to 1B?!
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
        try:
            url_dict = eval(url)  # maybe call eval in pars_doc ?
        except:
            url_dict = eval(re.sub(r'null', '""', url))

        return_dict = {}
        for key, val in url_dict.items():
            return_dict[key] = self.split_url(key)
            return_dict[val] = self.split_url(val)
        return return_dict

    def hashtag_parser(self, hashtag):
        splitted_hashtag = map(lambda x: x.lower(),
                               filter(lambda x: len(x) > 0, re.split(r'_|(?<=[^A-Z])(?=[A-Z])', hashtag)))
        return list(splitted_hashtag)[1:] + [hashtag.lower()]

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
        indices = doc_as_list[4]
        retweet_text = doc_as_list[5]
        retweet_url = doc_as_list[6]
        retweet_indices = doc_as_list[7]
        quote_text = doc_as_list[8]
        quote_url = doc_as_list[9]
        quote_indices = doc_as_list[10]
        retweet_quote_text = doc_as_list[11]
        retweet_quote_url = doc_as_list[12]
        retweet_quote_indices = doc_as_list[13]

        x = self.hashtag_parser("#ASAP_PartyAtHome")

        self.url_parser(url)

        term_dict = {}
        tokenized_text = self.parse_sentence(full_text)

        doc_length = len(tokenized_text)  # after text operations.

        for term in tokenized_text:
            if term not in term_dict.keys():
                term_dict[term] = 1
            else:
                term_dict[term] += 1

        document = Document(tweet_id, tweet_date, full_text, url, retweet_text, retweet_url, quote_text,
                            quote_url, term_dict, doc_length)
        return document
