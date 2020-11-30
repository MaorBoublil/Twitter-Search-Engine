import random
import os
from utils import save_obj, load_obj
from cmath import log10

MAX_DOCS = 100000
NUMBER_OF_BUCKETS = 500

class Indexer:

    def __init__(self, config,path):
        self.term_dict = {}
        self.document_dict = {}
        self.upper_terms = {}
        self.current_dump = 0
        self.config = config
        self.buckets = {}
        self.doc_counter = 0
        self.suspected_entities = {} # ENTITY: (TWEETID,tf)
        self.POSTING_PATH = path

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
                # Add entity as term
                bucket_id = str(random.randint(0, NUMBER_OF_BUCKETS))
                prev_tweet_id = self.suspected_entities[entity][0]
                prev_tf = self.suspected_entities[entity][1]
                prev_max_tf = self.document_dict[prev_tweet_id][1]
                self.term_dict[entity] = [[prev_tweet_id], 1, prev_tf, str(bucket_id), None]
                if bucket_id not in self.buckets:
                    self.buckets[bucket_id] = {}
                self.buckets[bucket_id].update({(entity, prev_tweet_id): [None, prev_tf / prev_max_tf, 0]})
                # Add to document term list to process, and remove from suspected
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
                        term_set = self.upper_terms.get(bucket_id, set())  # add to fix list
                        term_set.add(term.upper())
                        self.upper_terms[bucket_id] = term_set
                        self.term_dict[term] = [[tweet_id], 1, tf, str(bucket_id), None]
                    elif term.lower() in self.term_dict:  # we have upper and lower is inside
                        term = term.lower()
                        term_rec = self.term_dict[term]
                        term_rec[0].append(tweet_id)
                        term_rec[1] += 1  # df
                        term_rec[2] += tf  # cf
                        self.term_dict[term] = term_rec
                    else: # new word
                        bucket_id = str(random.randint(0, NUMBER_OF_BUCKETS))
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
        to_delete = {} # {BUCKETID : [terms]}
        delete_list = filter(lambda term : self.term_dict[term][2] <= 1,self.term_dict)
        for term in delete_list:
            bucket_id = self.term_dict[term][3]
            if bucket_id not in self.upper_terms or term.upper() not in self.upper_terms[bucket_id]:
                tweet_id = self.term_dict[term][0][0]
                to_delete[bucket_id] = to_delete.get(bucket_id,[]) + [(term,tweet_id)]

        N = len(self.document_dict)
        for bucket_id in self.buckets:
            bucket_id = str(bucket_id)
            file_path = self.POSTING_PATH + '/' + bucket_id
            posting_file = {}
            posting_file.update(self.buckets[bucket_id])
            for dump_num in range(self.current_dump):
                posting_file.update(load_obj(file_path + "_" + str(dump_num)))
                os.remove(file_path + "_" + str(dump_num) + ".pkl")

            if bucket_id in to_delete:
                for term,tweet_id in to_delete[bucket_id]:
                    self.term_dict.pop(term)
                    posting_file.pop((term,tweet_id))

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

            # Calculate document |d| for ranking
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
            save_obj(posting_file, file_path)

    def clean_memory(self):
        # clear all buckets
        for bucket_id, bucket_dict in self.buckets.items():
            save_obj(bucket_dict, self.POSTING_PATH + '/' + bucket_id + "_" + str(self.current_dump))
            self.buckets[bucket_id] = {}
        self.current_dump += 1
