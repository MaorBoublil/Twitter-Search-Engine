import random
import os
import glob
from utils import save_obj,load_obj

MAX_DOCS = 100000
NUMBER_OF_BUCKETS = 100
POSTING_PATH = "PostingFiles/"
TEXT = "_txt"

class Indexer:

    def __init__(self, config):
        self.term_dict = {}
        self.upper_terms = {}
        self.document_dict = {}
        #self.postingDict = {}
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

                    # Fix upper terms in fix list in relevant bucket
                    for upper_term in self.upper_terms[bucket_id]:
                        # Updating term dictionary for lower term
                        lower_term = upper_term.lower()
                        upper_record = self.term_dict[upper_term]
                        lower_record = self.term_dict[lower_term]
                        for i in range(3):
                            lower_record[i] += upper_record[i]
                        self.term_dict[lower_term] = lower_record
                        # Updating posting files to lower term
                        for tweet in self.term_dict[upper_term][0]:
                            tmp_dict[(lower_term,tweet)] = tmp_dict[(upper_term,tweet)]
                            tmp_dict.pop((upper_term,tweet))
                        # Remove from term dictionary
                        self.term_dict.pop(upper_term)

                    save_obj(tmp_dict, POSTING_PATH + bucket_id)

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
            old_term = term
            try:
                # Updating term dictionary
                if term not in self.term_dict:
                    # We want to make sure lower term and upper term are in the same bucket
                    if term.upper() in self.term_dict: # we have lower and upper is inside
                        bucket_id = self.term_dict[term.upper()][3]
                        term_list = self.upper_terms.get(bucket_id, [])  # add to fix list
                        term_list.append(term.upper())
                        self.upper_terms[bucket_id] = term_list
                    elif term.lower() in self.term_dict: # we have upper and lower is inside
                        term = term.lower()
                        bucket_id = self.term_dict[term.lower()][3]
                    else:
                        bucket_id = random.randint(0, NUMBER_OF_BUCKETS)
                    self.term_dict[term] = [[tweet_id], 1, tf, str(bucket_id)]


                else:  # existing term - update term parameters
                    if term.lower() in self.term_dict:
                        term = term.lower()
                    term_rec = self.term_dict[term]
                    term_rec[0].append(tweet_id)  # TODO: sort list
                    term_rec[1] += 1
                    term_rec[2] += len(document_dictionary[old_term])
                    self.term_dict[term] = term_rec

                bucket_id = self.term_dict[term][3]
                if bucket_id not in self.buckets:
                    self.add_bucket(bucket_id)

                # TODO: decide if max tf or doc length
                self.buckets[bucket_id] += f"(\"{term}\",\"{tweet_id}\"): ({document_dictionary[old_term]},{tf/document.max_tf}),"

            except:
                print('problem with the following key {}'.format(term))

        if self.doc_counter == MAX_DOCS:
            self.doc_counter = 0
            self.clean_memory()