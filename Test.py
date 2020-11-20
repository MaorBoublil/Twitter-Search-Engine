import time
import re
import pickle
import gzip
from urllib3.util import parse_url
dct = {1:2}

with gzip.open("PostingFiles/"+"1", 'wb') as _pickle:
    pickle.dump(dct, _pickle, -1)
