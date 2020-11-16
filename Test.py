import time
import re

from urllib3.util import parse_url


def num_manipulation(num):
    num = re.sub(r'(?<=\d|.) *Billion|(?<=\d|.) *billion', "B", num)
    num = re.sub(r'(?<=\d|.) *Million|(?<=\d|.) *million', "M", num)
    num = re.sub(r'(?<=\d|.) *Thousand|(?<=\d|.) *thousand', "K", num)
    num = re.sub(r'([0-9]+)(,{0,1})([0-9]{3})(,{0,1})([0-9]{3})(,{0,1})([0-9]{3})', r'\1.\3B', num)
    num = re.sub(r'([0-9]+)(,{0,1})([0-9]{3})(,{0,1})([0-9]{3}).*([0-9]*)', r'\1.\3M', num)
    num = re.sub(r'([0-9]+)(,{0,1})([0-9]{3}).*\d*', r'\1.\3K', num)
    num = re.sub(r'([0-9]+).([0]*)([1-9]{0,3})([0]*)(K|M|B)', r'\1.\2\3\5', num)
    return re.sub(r'([0-9]{1,3}).([0]{3})(K|M|B)', r'\1\3', num)


print(num_manipulation("1000000000000"))


def refunc(url):
    url_list = list(filter(None, re.split("://|\?|/|=|(?<=www).", url)))
    return url_list


def oldfunc(url):
    parsedUrl = parse_url(url)
    val_list = [parsedUrl[0], parsedUrl[2]]
    if parsedUrl[4] != None:
        val_list += parsedUrl[4].split('/')[1:]
    if parsedUrl[5] != None:
        val_list += parsedUrl[5].split('=')
    return val_list


url = 'https://www.wlwt.com/article/hundreds-of-people-celebrated-the-july-4-weekend-at-a-michigan-lake-now-some-have-covid-19/33289945'

start_time = time.time()
for i in range(100000):
    refunc(url)
print("--- %s seconds ---" % (time.time() - start_time))

start_time = time.time()
for i in range(100000):
    oldfunc(url)
print("--- %s seconds ---" % (time.time() - start_time))
