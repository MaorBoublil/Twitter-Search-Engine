import glob
from reader import ReadFile
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
from searcher import Searcher
from utils import save_obj,load_obj
import time
from multiprocessing.pool import Pool
from multiprocessing import cpu_count,Manager
from tqdm import tqdm
import os
#import spacy

CPUCOUNT = cpu_count()

def run_engine():
    """

    :return:
    """
    print("Project was created successfully.")
    number_of_documents = 0

    #nlp = spacy.load('en_core_web_sm',
    #                 disable=['parser', 'tagger', 'textcat', 'entity_linker', 'entity_ruler', 'sentencizer'])
    #nerDict = {}
    #bigsmall = load_obj("BigSmallWords")


    config = ConfigClass()
    r = ReadFile(corpus_path=config.get__corpusPath())
    p = Parse()
    indexer = Indexer(config)
    x = [x.split("Engine/")[1] for x in list(glob.iglob(os.getcwd()+"/Data/" + '**/**.parquet', recursive=True))]
    start_time = time.time()

    for index in range(2,3):
        documents_list = r.read_file(file_name=x[index])

        # texts = [x[2] for x in documents_list]
        # docs = nlp.pipe(texts,n_process=CPUCOUNT)
        # tweetidgen = (n[0] for n in documents_list)
        # for item,tweetid in tqdm(zip(docs,tweetidgen),total=len(documents_list),desc="Entity Recognition #" + str(index)):
        #     nerDict[tweetid] = item.ents
        #parsed_doc_list = []
        with Pool(CPUCOUNT) as _p:
            for parsed_doc in tqdm(_p.imap_unordered(p.parse_doc, documents_list), total=len(documents_list),
                                   desc="Parsing & Indexing Parquet #" + str(index)):
                number_of_documents += 1
                indexer.add_new_doc(parsed_doc)
            _p.close()
            _p.join()

        # bigsmallwordsDocs = []
        # for parsed_doc in parsed_doc_list:
        #     bigsmallwordsDocs.append(func(parsed_doc))
        #
        # with Pool(CPUCOUNT) as _p:
        #     for doc_index in tqdm(range(len(bigsmallwordsDocs)), total=len(bigsmallwordsDocs),
        #                            desc="Indexing Parquet #" + str(index)):
        #         indexer.add_new_doc(bigsmallwordsDocs[doc_index])
        #     _p.close()
        #     _p.join()


    print("--- Parallel Parser + indexer took %s seconds ---" % (time.time() - start_time))
    start_time = time.time()
    indexer.finish_index()
    print("--- Finish indexer took %s seconds ---" % (time.time() - start_time))
    print('Finished parsing and indexing. Starting to export files')
    save_obj(indexer.term_dict, "inverted_idx")
    save_obj(indexer.document_dict, "doc_dictionary")


def load_index():
    print('Load inverted index')
    docs = (load_obj("inverted_idx"),load_obj("doc_dictionary"))
    return docs


def search_and_rank_query(query, docs, k):
    p = Parse()
    parsed_query, parsed_entities = p.parse_query(query)
    searcher = Searcher(docs)
    relevant_docs = searcher.relevant_docs_from_posting(parsed_query)
    ranked_docs = searcher.ranker.rank_relevant_docs(relevant_docs)
    return searcher.ranker.retrieve_top_k(ranked_docs, k)

def main():
    #run_engine()
    docs = load_index()
    query = ""
    while query is not "DONE":
        query = input("Please enter a query: ")
        k = int(input("Please enter number of docs to retrieve: "))
        for doc_tuple in search_and_rank_query(query, docs, k):
            print('tweet id: {}, score (unique common words with query): {}'.format(doc_tuple[0], doc_tuple[1]))
