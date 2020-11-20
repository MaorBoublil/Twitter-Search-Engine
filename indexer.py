import random
import os
import glob
from utils import save_obj,load_obj

MAX_DOCS = 50000
NUMBER_OF_BUCKETS = 100
POSTING_PATH = "PostingFiles/"
TEXT = "_txt"

class Indexer:

    def __init__(self, config):
        self.inverted_idx = {}
        self.document_dict = {}
        self.postingDict = {}
        self.config = config
        self.current_num_buckets = 0
        self.buckets = {}
        self.doc_counter = 0
        files = glob.glob(POSTING_PATH + '*')
        for f in files:
            os.remove(f)

    def add_bucket(self,bucket_id):
        if self.current_num_buckets == NUMBER_OF_BUCKETS:
            removeID = random.choice(list(self.buckets.keys()))
            with open(POSTING_PATH + removeID + TEXT, "a", encoding='utf-8') as file:
                file.write(self.buckets[removeID])
            self.buckets.pop(removeID)
            self.current_num_buckets-=1

        self.buckets[bucket_id] = ""
        self.current_num_buckets += 1

    def finish_index(self):
        self.clean_memory()

        for bucket_id in range(NUMBER_OF_BUCKETS):
            bucket_id = str(bucket_id)
            file_path = POSTING_PATH + bucket_id + TEXT
            if os.path.isfile(file_path):
                with open(file_path,'r',encoding='utf-8') as file:
                    tmp_dict = eval("{"+file.read()[:-1]+"}")
                    save_obj(tmp_dict, POSTING_PATH + bucket_id)

    #TODO: capital letters
    #TODO: remove words with low frequency

    def clean_memory(self):
        #clear all buckets
        for bucket_id, string in self.buckets.items():
            with open(POSTING_PATH + bucket_id + TEXT, "a", encoding='utf-8') as file:
                file.write(string)
            self.buckets[bucket_id] = ""

    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """
        self.doc_counter += 1
        self.document_dict[document.tweet_id] = (document.doc_length, document.max_tf, document.unique_words_count)
        document_dictionary = document.term_doc_dictionary
        tweet_id = document.tweet_id

        # Go over each term in the doc
        for term in document_dictionary.keys():
            tf = len(document_dictionary[term])
            try:
                # Updating term dictionary
                if term not in self.inverted_idx.keys():
                    bucket_id = random.randint(0, NUMBER_OF_BUCKETS)
                    self.inverted_idx[term] = [[tweet_id], 1, tf, str(bucket_id)]
                else:
                    term_rec = self.inverted_idx[term]
                    term_rec[0].append(tweet_id)  # TODO: sort list
                    term_rec[1] += 1
                    term_rec[2] += len(document_dictionary[term])
                    self.inverted_idx[term] = term_rec

                bucket_id = self.inverted_idx[term][3]
                if bucket_id not in self.buckets:
                    self.add_bucket(bucket_id)

                # TODO: decide if max tf or doc length
                self.buckets[bucket_id] += f"(\"{term}\",\"{tweet_id}\"): ({document_dictionary[term]},{tf/document.max_tf}),"

            except:
                print('problem with the following key {}'.format(term))

        if self.doc_counter == MAX_DOCS:
            self.doc_counter = 0
            self.clean_memory()