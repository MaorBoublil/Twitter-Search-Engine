# import glob
# import os
# import spacy
# from configuration import ConfigClass
# from reader import ReadFile
import json
import pickle
# from tqdm import tqdm
# import re
# hashtag_pattern = r'#\w*'
# reserved_word_pattern = r'(RT|rt|FAV|fav|VIA|via|:|\n)'
# emojis_pattern = u'\U0001F600-\U0001F64F"|\U0001F300-\U0001F5FF|\U0001F680-\U0001F6FF|\U0001F1E0-\U0001F1FF'
# mention_pattern = r'@\w*'
# if __name__ == '__main__':
#     emoji_pattern = re.compile("["
#                                u"\U0001F600-\U0001F64F"  # emoticons
#                                u"\U0001F300-\U0001F5FF"  # symbols & pictographs
#                                u"\U0001F680-\U0001F6FF"  # transport & map symbols
#                                u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
#                                u"\U0001F1F2-\U0001F1F4"  # Macau flag
#                                u"\U0001F1E6-\U0001F1FF"  # flags
#                                u"\U0001F600-\U0001F64F"
#                                u"\U00002702-\U000027B0"
#                                u"\U000024C2-\U0001F251"
#                                u"\U0001f926-\U0001f937"
#                                u"\U0001F1F2"
#                                u"\U0001F1F4"
#                                u"\U0001F620"
#                                u"\u200d"
#                                u"\u2640-\u2642"
#                                "]+", flags=re.UNICODE)
#     save_set = set()
#     allEntities = set()
#     term_set = set()
#     y = list(glob.iglob(os.getcwd()+"/Data/" + '**/**.parquet', recursive=True))
#     x = [x.split("Engine/")[1] for x in list(glob.iglob(os.getcwd()+"/Data/" + '**/**.parquet', recursive=True))]
#     config = ConfigClass()
#     r = ReadFile(corpus_path=config.get__corpusPath())
#     document_list = []
#     nlp = spacy.load('en_core_web_sm',
#                          disable=['tagger', 'textcat', 'entity_linker', 'entity_ruler', 'sentencizer'])
#     for i in range(len(x)):
#         document_list+=r.read_file(file_name=x[i])
#     texts = [emoji_pattern.sub(r'',re.sub(hashtag_pattern+"|"+reserved_word_pattern+"|"+mention_pattern+"|http\S+","",x[2])) for x in document_list]
#     docs = nlp.pipe(texts,n_process=os.cpu_count())
#     for item in tqdm(docs,total=len(document_list),desc="Entity Recognition"):
#         allEntities.add(item.ents)
#     for tuple in allEntities:
#         for term in tuple:
#             aterm = term.text
#             if aterm not in term_set:
#                 term_set.add(aterm)
#             else:
#                 save_set.add(aterm)
import time

import utils

# x = utils.load_obj("PostingFiles/2")
# new_dict = {}
# for key in x:
#     new_dict[key[0]+key[1]] = x[key]
with open('C:/Users/maorb/OneDrive/Desktop/Twitter-Search-Engine/goodData/Stemmed_BigSmallWords.pkl', 'rb') as f:
    x = pickle.load(f)

print(1)