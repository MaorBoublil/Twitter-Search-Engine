import random
import os
import glob
import time

from utils import save_obj, load_obj
from cmath import log10

MAX_DOCS = 100000
NUMBER_OF_BUCKETS = 500
POSTING_PATH = "PostingFiles/"
TEXT = "_txt"


class Indexer:

    def __init__(self, config):
        self.term_dict = {}
        self.document_dict = {}
        self.upper_terms = {}
        self.current_dump = 0
        self.config = config
        self.buckets = {}
        self.doc_counter = 0
        self.suspected_entities = {} # ENTITY: (TWEETID,tf)
        #Remove PKL FILES
        files = glob.glob(POSTING_PATH + '*')
        for f in files:
            os.remove(f)

    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """
        self.doc_counter += 1
        self.document_dict[document.tweet_id] = [document.doc_length, document.max_tf, document.unique_words_count, 0]
        terms_in_document = document.term_doc_dictionary
        tweet_id = document.tweet_id

        for entity in document.entities:
            if entity in self.term_dict:
                terms_in_document[entity] = document.entities[entity]
            elif entity in self.suspected_entities:
                bucket_id = random.randint(0, NUMBER_OF_BUCKETS)
                self.term_dict[entity] = [[self.suspected_entities[entity][0]], 1, self.suspected_entities[entity][1], str(bucket_id), None]
                terms_in_document[entity] = document.entities[entity]
                self.suspected_entities.pop(entity)
            else: # new entity
                self.suspected_entities[entity] = (tweet_id, document.entities[entity])

        # Go over each term in the doc
        for term in terms_in_document.keys():
            term_record = terms_in_document[term]
            if type(term_record) == int:
                tf = term_record
            else:
                tf = len(terms_in_document[term])

            old_term = term
            try:
                # Updating term dictionary
                if term not in self.term_dict:
                    # We want to make sure lower term and upper term are in the same bucket
                    if term.upper() in self.term_dict:  # we have lower and upper is inside
                        bucket_id = self.term_dict[term.upper()][3]
                        term_list = self.upper_terms.get(bucket_id, [])  # add to fix list
                        term_list.append(term.upper())
                        self.upper_terms[bucket_id] = term_list
                        self.term_dict[term] = [[tweet_id], 1, tf, str(bucket_id), None]
                    elif term.lower() in self.term_dict:  # we have upper and lower is inside
                        term = term.lower()
                        term_rec = self.term_dict[term]
                        term_rec[0].append(tweet_id)
                        term_rec[1] += 1  # df
                        term_rec[2] += tf  # cf
                        self.term_dict[term] = term_rec
                    else: # new word
                        bucket_id = random.randint(0, NUMBER_OF_BUCKETS)
                        self.term_dict[term] = [[tweet_id], 1, tf, str(bucket_id), None]

                else:  # existing term - update term parameters
                    if term.lower() in self.term_dict:
                        term = term.lower()
                    term_rec = self.term_dict[term]
                    term_rec[0].append(tweet_id)
                    term_rec[1] += 1  # df
                    term_rec[2] += tf  # cf
                    self.term_dict[term] = term_rec

                bucket_id = self.term_dict[term][3]
                if bucket_id not in self.buckets:
                    self.buckets[bucket_id] = {}

                self.buckets[bucket_id].update({(term, tweet_id): [terms_in_document[old_term], tf / document.max_tf, 0]})

            except:
                print('problem with the following key {}'.format(term))

        if self.doc_counter == MAX_DOCS:
            self.doc_counter = 0
            self.clean_memory()

    def finish_index(self):  # TODO: PARRALEL
        #self.clean_memory()  # TODO: if hierarchical then clean before
        N = len(self.document_dict)
        mergetimes = [] #TODO: REMOVE PRINTS
        calculationtimes = []
        bigsmalltime = []
        save_times = []
        for bucket_id in self.buckets:
            bucket_id = str(bucket_id)
            file_path = POSTING_PATH + bucket_id
            posting_file = {}
            posting_file.update(self.buckets[bucket_id])
            start_merge = time.time()
            for dump_num in range(self.current_dump):
                posting_file.update(load_obj(file_path + "_" + str(dump_num)))
            mergetimes.append(time.time() - start_merge)
            #os.remove(file_path + "_" + str(dump_num) + ".pkl") TODO: REMOVE LATER do remove after all dumps and not specific num_*.pkl

            bigsmall_start = time.time()
            # Fix upper terms in fix list in relevant bucket
            for upper_term in self.upper_terms.get(bucket_id,[]):
                # Updating term dictionary for lower term
                lower_term = upper_term.lower()
                upper_record = self.term_dict[upper_term]
                lower_record = self.term_dict[lower_term]
                for i in range(3):
                    lower_record[i] += upper_record[i]
                self.term_dict[lower_term] = lower_record
                # Updating posting files to lower term
                for tweet in self.term_dict[upper_term][0]:
                    posting_file[(lower_term, tweet)] = posting_file[(upper_term, tweet)]
                    posting_file.pop((upper_term, tweet))
                # Remove from term dictionary
                self.term_dict.pop(upper_term)
            bigsmalltime.append(time.time() - bigsmall_start)

            # Calculate document |d| for ranking
            start_calc = time.time()
            for key in posting_file:
                term, tweet_id = key
                idf = self.term_dict[term][4]
                if idf is None:
                    idf = (log10(N / self.term_dict[term][1])).real
                    self.term_dict[term][4] = idf
                tf_ij = posting_file[key][1]
                w_ij = tf_ij * idf
                posting_file[key][2] = w_ij
                self.document_dict[tweet_id][3] += w_ij ** 2
            calculationtimes.append(time.time()-start_calc)
            save_calc = time.time()
            save_obj(posting_file, file_path)
            save_times.append(time.time() - save_calc)
        print(f"save time is: {sum(save_times)}")
        print(f"Calc time is: {sum(calculationtimes)}")
        print(f"merge time is: {sum(mergetimes)}")
        print(f"bigsmall time is: {sum(bigsmalltime)}")

        # TODO: remove words with low frequency

    def clean_memory(self):
        # clear all buckets
        for bucket_id, bucket_dict in self.buckets.items():
            save_obj(bucket_dict, POSTING_PATH + bucket_id + "_" + str(self.current_dump))
            self.buckets[bucket_id] = {}
        self.current_dump += 1
