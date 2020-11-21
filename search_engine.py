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

CPUCOUNT = cpu_count()

def run_engine():
    """

    :return:
    """

    number_of_documents = 0

    config = ConfigClass()
    r = ReadFile(corpus_path=config.get__corpusPath())
    p = Parse(config.toStem)
    indexer = Indexer(config)

    y = list(glob.iglob(os.getcwd()+"/Data/" + '**/**.parquet', recursive=True))
    x = [x.split("Engine/")[1] for x in list(glob.iglob(os.getcwd()+"/Data/" + '**/**.parquet', recursive=True))]
    start_time = time.time()
    #number_of_documents = readnParse(r,p,x,number_of_documents)

    for index in range(20,21):
        # if index == 21:#TODO: WHAT THE HELL 21 Y U STUCk
        #    continue
        documents_list = r.read_file(file_name=x[index])

        with Pool(CPUCOUNT) as _p:
            for parsed_doc in tqdm(_p.imap_unordered(p.parse_doc, documents_list), total=len(documents_list),
                                   desc="Parsing Parquet #" + str(index)):
                number_of_documents += 1
                indexer.add_new_doc(parsed_doc)
            _p.close()
            _p.join()
    # more_urls = list(filter(lambda x: str(x[4]).count("[") > 2,documents_list))
    # Iterate over every document in the file

    print("--- Parallel Parser took %s seconds ---" % (time.time() - start_time))
    indexer.finish_index()

    print('Finished parsing and indexing. Starting to export files')
    save_obj(indexer.term_dict, "inverted_idx")
    save_obj(indexer.document_dict, "doc_dictionary")


def load_index():
    print('Load inverted index')
    inverted_index = load_obj("inverted_idx")
    return inverted_index


def search_and_rank_query(query, inverted_index, k):
    p = Parse()
    query_as_list = p.parse_sentence(query)
    searcher = Searcher(inverted_index)
    relevant_docs = searcher.relevant_docs_from_posting(query_as_list)
    ranked_docs = searcher.ranker.rank_relevant_doc(relevant_docs)
    return searcher.ranker.retrieve_top_k(ranked_docs, k)


def main():
    run_engine()
    query = input("Please enter a query: ")
    k = int(input("Please enter number of docs to retrieve: "))
    inverted_index = load_index()
    for doc_tuple in search_and_rank_query(query, inverted_index, k):
        print('tweet id: {}, score (unique common words with query): {}'.format(doc_tuple[0], doc_tuple[1]))
