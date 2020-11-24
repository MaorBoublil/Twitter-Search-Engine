import time

from nltk import stem


class Stemmer:
    def __init__(self):
        self.stemmer = stem.SnowballStemmer('english')
        self.dict = {}

    def stem_term(self, token):
        """
        This function stem a token
        :param token: string of a token
        :return: stemmed token
        """

        if token in self.dict:
             return self.dict[token]
        term = self.stemmer.stem(token)
        self.dict[token] = term
        return term



if __name__ == '__main__':
    words = ["He's", "https", "twitter.com"]
    stemmer = Stemmer()
    a = time.time()
    for i in range(100000):
        for word in words:
            stemmer.stem_term(word)
    print(time.time()-a)