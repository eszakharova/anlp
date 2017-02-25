
# coding: utf-8

# In[5]:

import wikipedia


def get_texts_for_lang(lang, n=10): # функция для скачивания статей из википедии
    wikipedia.set_lang(lang)
    wiki_content = []
    pages = wikipedia.random(n)
    for page_name in pages:
        try:
            page = wikipedia.page(page_name)
        except wikipedia.exceptions.WikipediaException:
            print('Skipping page {}'.format(page_name))
            continue

        wiki_content.append('{}\n{}'.format(page.title, page.content.replace('==', '')))

    return wiki_content


# In[45]:

import codecs
import collections
import sys


def tokenize(text):
    return text.split(' ')


def get_freqs_from_corpus(corpus):
    
    freqs = collections.defaultdict(lambda: 0)
    
    for article in corpus:
        for word in tokenize(article.replace('\n', '').lower()):
            freqs[word] += 1
            
    return freqs

def remove_common_words(dicts):
    number_of_dicts = len(dicts)
    word_present_in_multiple_lists = False
    
    for i in range(number_of_dicts):   
        for word in list(dicts[i].keys()):
            word_present_in_multiple_lists = False
            
            for j in range(i+1,number_of_dicts):
                if word in dicts[j]:
                    del[dicts[j][word]]
                    word_present_in_multiple_lists = True
            
            if word_present_in_multiple_lists:
                del[dicts[i][word]]


# In[46]:

def detect_language_first_method(text, langs, debug=False, number_of_docs_for_lang = 100):
   
    wiki_texts = {}
    for lang in langs:
        wiki_texts[lang] = get_texts_for_lang(lang, number_of_docs_for_lang)
#         print(lang, len(wiki_texts[lang]))
    
    freq_list = []
    for i in range(len(langs)):
        freq_list.append(get_freqs_from_corpus(wiki_texts[langs[i]]))
        
    remove_common_words(freq_list)
    number_of_words = [0 for i in range(len(langs))]
    
        
    for word in tokenize(text):
        for i in range(len(langs)):
            if word in freq_list[i]:
                number_of_words[i] += 1
                
        
    if(debug):
        print(number_of_words)
    return (langs[number_of_words.index(max(number_of_words))])


# In[17]:

# detect_language_first_method('және', ('kk', 'uk', 'be', 'fr'), debug=True, number_of_docs_for_lang = 2)


# In[9]:

from itertools import islice, tee

def make_ngrams(text):
    N = 3 # задаем длину n-граммы
    ngrams = zip(*(islice(seq, index, None) for index, seq in enumerate(tee(text, N))))
    ngrams = [''.join(x) for x in ngrams]
    return ngrams


# In[28]:

def get_ngram_freqs(corpus):
    freqs = collections.defaultdict(lambda: 0)
    for article in corpus:
        for ngram in make_ngrams(article.replace('\n', '').lower()):
            freqs[ngram] += 1
    return freqs


# In[41]:

def detect_language_second_method(text, langs, debug=False, number_of_docs_for_lang = 100):
    wiki_texts = {}
    for lang in langs:
        wiki_texts[lang] = get_texts_for_lang(lang, number_of_docs_for_lang)
#         print(lang, len(wiki_texts[lang]))
    
    freq_list = []
    for i in range(len(langs)):
        freq_list.append(get_ngram_freqs(wiki_texts[langs[i]]))
        
    remove_common_words(freq_list)
    number_of_words = [0 for i in range(len(langs))]
    
        
    for ngram in make_ngrams(text):
        for i in range(len(langs)):
            if ngram in freq_list[i]:
                number_of_words[i] += 1
                
        
    if(debug):
        print(number_of_words)
    return (langs[number_of_words.index(max(number_of_words))])


# In[36]:

# detect_language_second_method('le maman', ('kk', 'uk', 'be', 'fr'), debug=True, number_of_docs_for_lang = 5)


# In[42]:

# test_articles = {}
# for l in ['kk', 'uk', 'be', 'fr']:
#     articles = get_texts_for_lang(lang, n=10)
#     for art in articles:
#         test_articles[art] = l


# In[44]:

# first_wrong = 0
# second_wrong = 0
# for article in test_articles:
#     print(test_articles[article])
#     first = detect_language_first_method(article, ('kk', 'uk', 'be', 'fr'), number_of_docs_for_lang = 5)
#     second = detect_language_second_method(article, ('kk', 'uk', 'be', 'fr'), number_of_docs_for_lang = 5)
#     if first != test_articles[article]:
#         first_wrong += 1
#     if second != test_articles[article]:
#         second_wrong += 1
# print(first_wrong, second_wrong)


# In[50]:

filename = input('Название файла')
f = open(filename, 'r')
text = f.read()
print(detect_language_first_method(text, ('kk', 'uk', 'be', 'fr'), number_of_docs_for_lang = 20))
print(detect_language_second_method(text, ('kk', 'uk', 'be', 'fr'), number_of_docs_for_lang = 20))
