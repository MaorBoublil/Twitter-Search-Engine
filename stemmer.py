from nltk.stem import snowball


class Stemmer:
    def __init__(self):
        self.stemmer = snowball.SnowballStemmer("english")

    def stem_term(self, token):
        """
        This function stem a token
        :param token: string of a token
        :return: stemmed token
        """
        return self.stemmer.stem(token)


if __name__ == '__main__':
    words = ["NBA", "Cities", "CITIES"]
    stemmer = Stemmer()
    for word in words:
        print(stemmer.stem_term(word))