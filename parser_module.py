import re
from nltk.corpus import stopwords
from document import Document
from stemmer import Stemmer

BILLION_PATTERN = r'(?<=\d|.) *Billion|(?<=\d|.) *billion'
MILLION_PATTERN = r'(?<=\d|.) *Million|(?<=\d|.) *million'
THOUSAND_PATTERN = r'(?<=\d|.) *Thousand|(?<=\d|.) *thousand'
BILLION_PATTERN_NUM = r'([0-9]+)(,{0,1})([0-9]{3})(,{0,1})([0-9]{3})(,{0,1})([0-9]{3})'
MILLION_PATTERN_NUM = r'([0-9]+)(,{0,1})([0-9]{3})(,{0,1})([0-9]{3})'
THOUSAND_PATTERN_NUM = r'([0-9]+)(,{0,1})([0-9]{3})'
GENERAL_PATTERN = r'([0-9]+).([0]*)([1-9]{0,3})([0]*)(K|M|B)'
DECIMAL_PATTERN = r'([0-9]{1,3}).([0]{3})(K|M|B)'
PERCENT_PATTERN = r'(?<=\d)(?<=M|B|K)* *((p|P)(e|E)(r|R)(c|C)(e|E)(n|N)(t|T)|(p|P)(e|E)(r|R)(c|C)(e|E)(n|N)(t|T)(a|A)(g|G)(e|E)|%)'
DOLLAR_PATTERN = r'(?<=\d[M|B|K]) *((d|D)(o|O)(l|L)(l|L)(a|A)(r|R)(s|S)*|$)|(?<=\d) *((d|D)(o|O)(l|L)(l|L)(a|A)(r|R)(s|S)*|$)'
SPLIT_URL_PATTERN = "://|\?|/|=|-|(?<=www)."
REMOVE_URL_PATTERN = r"http\S+"
HASHTAG_PATTERN = r'_|(?<=[^A-Z])(?=[A-Z])'
TWITTER_STATUS_PATTERN = r'(twitter.com\/)(\S*)(\/status\/)(\d)*'
TOKENIZER_PATTERN = r"(?x)\d+\ +\d+\/\d+|\d+\/\d+|\d+\.*\d*(?:[MKBG])*(?:[$%])*|(?:[A-Z]\.)+| (?:[#@])*\w+\’*\'*\w*| \$?\d+(?:\.\d+)?%?"
ENTITY_PATTERN = r'(?:[A-Z][A-Za-z]*(?:(?: |-)[A-Z][A-Za-z]*)+)'

contractions = {
"ain't": "is not",
"aren't": "are not",
"can't": "cannot",
"can't've": "cannot have",
"'cause": "because",
"could've": "could have",
"couldn't": "could not",
"couldn't've": "could not have",
"didn't": "did not",
"doesn't": "does not",
"don't": "do not",
"hadn't": "had not",
"hadn't've": "had not have",
"hasn't": "has not",
"haven't": "have not",
"he'd": "he had",
"he'd've": "he would have",
"he'll": "he will",
"he'll've": "he will have",
"he's": "he is",
"how'd": "how did",
"how'd'y": "how do you",
"how'll": "how will",
"how's": "how is",
"I'd": "I would",
"I'd've": "I would have",
"I'll": "I will",
"I'll've": "I will have",
"I'm": "I am",
"I've": "I have",
"isn't": "is not",
"it'd": "it had",
"it'd've": "it would have",
"it'll": "it will",
"it'll've": "it will have",
"it's": "it is",
"let's": "let us",
"ma'am": "madam",
"mayn't": "may not",
"might've": "might have",
"mightn't": "might not",
"mightn't've": "might not have",
"must've": "must have",
"mustn't": "must not",
"mustn't've": "must not have",
"needn't": "need not",
"needn't've": "need not have",
"o'clock": "of the clock",
"oughtn't": "ought not",
"oughtn't've": "ought not have",
"shan't": "shall not",
"sha'n't": "shall not",
"shan't've": "shall not have",
"she'd": "she had",
"she'd've": "she would have",
"she'll": "she will",
"she'll've": "she will have",
"she's": "she is",
"should've": "should have",
"shouldn't": "should not",
"shouldn't've": "should not have",
"so've": "so have",
"so's": "so is",
"that'd": "that would",
"that'd've": "that would have",
"that's": "that is",
"there'd": "there would",
"there'd've": "there would have",
"there's": "there is",
"they'd": "they would",
"they'd've": "they would have",
"they'll": "they will",
"they'll've": "they will have",
"they're": "they are",
"they've": "they have",
"to've": "to have",
"wasn't": "was not",
"we'd": "we would",
"we'd've": "we would have",
"we'll": "we will",
"we'll've": "we will have",
"we're": "we are",
"we've": "we have",
"weren't": "were not",
"what'll": "what will",
"what'll've": "what will have",
"what're": "what are",
"what's": "what is",
"what've": "what have",
"when's": "when is",
"when've": "when have",
"where'd": "where did",
"where's": "where is",
"where've": "where have",
"who'll": "who will",
"who'll've": "who will have",
"who's": "who is",
"who've": "who have",
"why's": "why is",
"why've": "why have",
"will've": "will have",
"won't": "will not",
"won't've": "will not have",
"would've": "would have",
"wouldn't": "would not",
"wouldn't've": "would not have",
"y'all": "you all",
"y'all'd": "you all would",
"y'all'd've": "you all would have",
"y'all're": "you all are",
"y'all've": "you all have",
"you'd": "you would",
"you'd've": "you would have",
"you'll": "you will",
"you'll've": "you will have",
"you're": "you are",
"you've": "you have",
"ain’t": "is not",
"aren’t": "are not",
"can’t": "cannot",
"can’t’ve": "cannot have",
"’cause": "because",
"could’ve": "could have",
"couldn’t": "could not",
"couldn’t’ve": "could not have",
"didn’t": "did not",
"doesn’t": "does not",
"don’t": "do not",
"hadn’t": "had not",
"hadn’t’ve": "had not have",
"hasn’t": "has not",
"haven’t": "have not",
"he’d": "he had",
"he’d’ve": "he would have",
"he’ll": "he will",
"he’ll’ve": "he will have",
"he’s": "he is",
"how’d": "how did",
"how’d’y": "how do you",
"how’ll": "how will",
"how’s": "how is",
"I’d": "I would",
"I’d’ve": "I would have",
"I’ll": "I will",
"I’ll’ve": "I will have",
"I’m": "I am",
"I’ve": "I have",
"isn’t": "is not",
"it’d": "it had",
"it’d’ve": "it would have",
"it’ll": "it will",
"it’ll’ve": "it will have",
"it’s": "it is",
"let’s": "let us",
"ma’am": "madam",
"mayn’t": "may not",
"might’ve": "might have",
"mightn’t": "might not",
"mightn’t’ve": "might not have",
"must’ve": "must have",
"mustn’t": "must not",
"mustn’t’ve": "must not have",
"needn’t": "need not",
"needn’t’ve": "need not have",
"o’clock": "of the clock",
"oughtn’t": "ought not",
"oughtn’t’ve": "ought not have",
"shan’t": "shall not",
"sha’n’t": "shall not",
"shan’t’ve": "shall not have",
"she’d": "she had",
"she’d’ve": "she would have",
"she’ll": "she will",
"she’ll’ve": "she will have",
"she’s": "she is",
"should’ve": "should have",
"shouldn’t": "should not",
"shouldn’t’ve": "should not have",
"so’ve": "so have",
"so’s": "so is",
"that’d": "that would",
"that’d’ve": "that would have",
"that’s": "that is",
"there’d": "there would",
"there’d’ve": "there would have",
"there’s": "there is",
"they’d": "they would",
"they’d’ve": "they would have",
"they’ll": "they will",
"they’ll’ve": "they will have",
"they’re": "they are",
"they’ve": "they have",
"to’ve": "to have",
"wasn’t": "was not",
"we’d": "we would",
"we’d’ve": "we would have",
"we’ll": "we will",
"we’ll’ve": "we will have",
"we’re": "we are",
"we’ve": "we have",
"weren’t": "were not",
"what’ll": "what will",
"what’ll’ve": "what will have",
"what’re": "what are",
"what’s": "what is",
"what’ve": "what have",
"when’s": "when is",
"when’ve": "when have",
"where’d": "where did",
"where’s": "where is",
"where’ve": "where have",
"who’ll": "who will",
"who’ll’ve": "who will have",
"who’s": "who is",
"who’ve": "who have",
"why’s": "why is",
"why’ve": "why have",
"will’ve": "will have",
"won’t": "will not",
"won’t’ve": "will not have",
"would’ve": "would have",
"wouldn’t": "would not",
"wouldn’t’ve": "would not have",
"y’all": "you all",
"y’all’d": "you all would",
"y’all’d’ve": "you all would have",
"y’all’re": "you all are",
"y’all’ve": "you all have",
"you’d": "you would",
"you’d’ve": "you would have",
"you’ll": "you will",
"you’ll’ve": "you will have",
"you’re": "you are",
"you’ve": "you have"
}

# TODO: if we want in helek gimel - HOK 3 - U.S.A to USA

class Parse:

    def __init__(self,stemming):
        self.stop_words = stopwords.words('english')
        self.stop_words+= ["rt", "http", "https", "www","twitter.com"] # TODO: check &amp
        self.terms = set()
        self.nonstopwords = 0
        self.max_tf = 0
        self.toStem = stemming
        self.entities = {}
        if self.toStem:
            self.stemmer = Stemmer()

    def parse_sentence(self, text):
        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        :param text:
        :return:
        """
        term_dict = {}
        entity_dict = {}

        for entity in re.findall(ENTITY_PATTERN, text):
            cleaned_entity = re.sub("-", " ", entity).upper()
            entity_dict[cleaned_entity] = entity_dict.get(cleaned_entity,0) + 1

        text_tokens = re.findall(TOKENIZER_PATTERN, text)
        indices_counter = 0
        for term in text_tokens:
            if len(term) < 1: continue
            indices_counter += 1
            if term[0] == "#":  # handle hashtags
                hashtag_list = self.hashtag_parser(term)
                for mini_term in hashtag_list:
                    self.dictAppender(term_dict, indices_counter, mini_term)
            elif term[0] == "@":  # handle tags
                no_tag = self.tags_parser(term)
                self.dictAppender(term_dict, indices_counter, no_tag)
            elif term in contractions:  # remove things like he'll
                new_terms = contractions[term].split(" ")
                for mini_term in new_terms:
                    self.dictAppender(term_dict, indices_counter, mini_term)
                    indices_counter += 1
                indices_counter -= 1
                continue
            self.dictAppender(term_dict, indices_counter, term)

        return term_dict, indices_counter, entity_dict

    def split_url(self, url):
        url_list = list(filter(None, re.split(SPLIT_URL_PATTERN, url)))
        return url_list

    def remove_percent_dollar(self, text):
        no_dollar = re.sub(DOLLAR_PATTERN,"$", text)
        return re.sub(PERCENT_PATTERN, "%", no_dollar)

    def num_manipulation(self,num):
        num = re.sub(BILLION_PATTERN, "B", num)
        num = re.sub(MILLION_PATTERN, "M", num)
        num = re.sub(THOUSAND_PATTERN, "K", num)
        num = re.sub(BILLION_PATTERN_NUM, r'\1.\3B', num)
        num = re.sub(MILLION_PATTERN_NUM, r'\1.\3M', num)
        num = re.sub(THOUSAND_PATTERN_NUM, r'\1.\3K', num)
        num = re.sub(GENERAL_PATTERN, r'\1.\2\3\5', num)
        return re.sub(DECIMAL_PATTERN, r'\1\3', num)

    def url_parser(self, url):
        """
        :param url: recieves a string based dictionary of all urls
        :return: dictionary with parsed urls
        """
        if len(url) <= 2:
            return []
        url_list = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', url[1:-1])

        finalList = []
        for val in url_list:
            if 'twitter.com/i/web/status/' in val or 't.co' in val:
                continue
            val = re.sub(TWITTER_STATUS_PATTERN,r'\2',val)
            finalList = self.split_url(val)
        return finalList

    def hashtag_parser(self, hashtag):
        splitted_hashtag = list(map(lambda x: x.lower(),
                               filter(lambda x: len(x) > 0, re.split(HASHTAG_PATTERN, hashtag))))
        if len(splitted_hashtag) < 2:
            return splitted_hashtag
        else:
            return splitted_hashtag[1:] + [hashtag.lower()]

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
        full_text = doc_as_list[2]
        docText = full_text
        url = doc_as_list[3]
        if len(doc_as_list) >= 14:
            quote_text = doc_as_list[8]
            if quote_text:
                docText += quote_text
        self.nonstopwords = 0
        self.max_tf = 0

        if tweet_id == '1288846358129127425':
            print('here')

        self.terms.clear()  # TODO: REMOVE THIS FOR PARALLEL
        docText = re.sub(REMOVE_URL_PATTERN, "", docText)  # link removal from fulltext
        docText = self.num_manipulation(docText)
        docText = self.remove_percent_dollar(docText)

        tokenized_dict, indices_counter, entity_dict = self.parse_sentence(docText)
        urlTermList = self.url_parser(url)
        for term in urlTermList:
            #if not term or len(term) < 1 : continue
            indices_counter += 1
            self.dictAppender(tokenized_dict, indices_counter, term)

        doc_length = self.nonstopwords  # after text operations.

        document = Document(tweet_id,term_doc_dictionary=tokenized_dict, doc_length=doc_length, max_tf=self.max_tf, entities_dict=entity_dict)
        return document

    def parse_query(self,query):  # return {term: ([indices,tf])}
        self.nonstopwords = 0
        self.max_tf =0
        docText = self.num_manipulation(query)
        docText = self.remove_percent_dollar(docText)

        tokenized_dict, indices_counter, entity_dict = self.parse_sentence(docText)
        return tokenized_dict, entity_dict

    def remove_stopwords(self,query):
        text_tokens = re.findall(TOKENIZER_PATTERN, query)
        tokens = list(filter(lambda x: x.lower() not in self.stop_words, text_tokens))
        query = ' '.join(tokens)
        return query
