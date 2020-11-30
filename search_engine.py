import os
from WordNet import WordNet
from reader import ReadFile
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
from searcher import Searcher
from utils import save_obj,load_obj
from multiprocessing.pool import Pool
from multiprocessing import cpu_count
from tqdm import tqdm

CPUCOUNT = cpu_count()

def run_engine(corpus_path='', output_path='', stemming=False):
    """

    :return:
    """
    # Create PostingFile directory if it doesn't exist
    try:
        os.mkdir(output_path)
    except:
        pass

    number_of_documents = 0
    config = ConfigClass()
    r = ReadFile(corpus_path=corpus_path)
    p = Parse(stemming)
    indexer = Indexer(config,output_path)
    # Get all parquet files from corpus path
    parquets = []
    for root, dirs, files in os.walk(corpus_path):
        for name in files:
            if name.endswith((".parquet", ".htm")):
                parquets.append(root + '/' + name)

    for index in range(len(parquets)):
        documents_list = r.read_file(file_name=parquets[index])
        # Create a new process for each document
        with Pool(CPUCOUNT) as _p:
            for parsed_doc in tqdm(_p.imap_unordered(p.parse_doc, documents_list), total=len(documents_list),
                                   desc="Parsing & Indexing Parquet #" + str(index)):
                number_of_documents += 1
                indexer.add_new_doc(parsed_doc)
            _p.close()
            _p.join()

    p.entities.clear()
    indexer.finish_index()
    print('Finished parsing and indexing. Starting to export files')
    save_obj(indexer.term_dict, output_path + "/inverted_idx")
    save_obj(indexer.document_dict, output_path + "/doc_dictionary")
    indexer.document_dict.clear()
    indexer.term_dict.clear()


def load_index(output_path=''):
    print('Load inverted index')
    docs = (load_obj(output_path + "/inverted_idx"),load_obj(output_path + "/doc_dictionary"))
    return docs


def search_and_rank_query(query, docs, k, stemming, output_path):
    p = Parse(stemming)
    wordnet = WordNet()
    query = wordnet.expand_query(p.remove_stopwords(query))
    parsed_query, parsed_entities = p.parse_query(query)
    searcher = Searcher(docs, output_path)
    relevant_docs = searcher.relevant_docs_from_posting(parsed_query, parsed_entities)
    ranked_docs = searcher.ranker.rank_relevant_docs(relevant_docs)
    return searcher.ranker.retrieve_top_k(ranked_docs, k)

def main(corpus_path='', output_path='', stemming=False, queries=None, num_docs_to_retrieve=10):
    run_engine(corpus_path,output_path,stemming)
    docs = load_index(output_path)
    if type(queries) != list:
        file1 = open(queries, 'r')
        queries = file1.readlines()
    for query in queries:
        query = query.replace('\n', '')
        print(query)
        for doc_tuple in search_and_rank_query(query, docs, num_docs_to_retrieve, stemming, output_path):
            print('tweet id: {}, score (unique common words with query): {}'.format(doc_tuple[0], doc_tuple[1]))
