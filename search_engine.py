from reader import ReadFile
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
from searcher import Searcher
from utils import save_obj,load_obj
import time
from multiprocessing.pool import Pool
from multiprocessing import cpu_count
from tqdm import tqdm

CPUCOUNT = cpu_count()


def run_engine():
    """

    :return:
    """

    number_of_documents = 0

    config = ConfigClass()
    r = ReadFile(corpus_path=config.get__corpusPath())
    p = Parse()
    indexer = Indexer(config)

    documents_list = r.read_file(file_name='covid19_07-13.snappy.parquet')
    # more_urls = list(filter(lambda x: str(x[4]).count("[") > 2,documents_list))
    # Iterate over every document in the file
    start_time = time.time()
    with Pool(CPUCOUNT) as _p:
        for parsed_doc in tqdm(_p.imap_unordered(p.parse_doc, documents_list), total=len(documents_list),
                               desc="Parsing 1st Parquet"):
            number_of_documents += 1
            # indexer.add_new_doc(parsed_doc)
        _p.close()
        _p.join()
    print("--- Parallel Parser took %s seconds ---" % (time.time() - start_time))
    # start_time = time.time()
    # for idx, document in enumerate(documents_list):
    #     # parse the document
    #     parsed_document = p.parse_doc(document)
    #     number_of_documents += 1
    #     # index the document data
    #     #indexer.add_new_doc(parsed_document)
    # print("--- UnParallel Parser took %s seconds ---" % (time.time() - start_time))
    print('Finished parsing and indexing. Starting to export files')

    save_obj(indexer.inverted_idx, "inverted_idx")
    save_obj(indexer.postingDict, "posting")


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
