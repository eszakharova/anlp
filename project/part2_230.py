import re
import collections as cl
import pymorphy2
morph = pymorphy2.MorphAnalyzer()

def abbreviations(text):
    pattern1 = re.compile(r'[^А-ЯЁ](([А-ЯЁ]\. ?){1,3})') # инициалы
    pattern2 = re.compile(r'[\(\):;" ]([а-яёА-ЯЁ]\. ?[а-яё]\.)[\(\):;" ]') # сокращения типа т.п. (без пробела)
    #pattern3 = re.compile(r'[\(\):;" ]([а-яёА-ЯЁ]\. [а-яё]\.)[\(\):;" ]') # сокращения типа т. п. (с пробелом)
    pattern4 = re.compile(r'[\(\):;" ]([а-яё]{2,3}\.)[\(\):;" ]') # сокращения типа см., таб. (2-3 символа до точки)
    pattern5 = re.compile(r'[\(\):;" ]((\w\.){3,10})[\(\):;" ]') # сокращения типа с.ш.а.
    abb = []
    abb.append([i[0] for i in re.findall(pattern1, text)])
    abb.append(re.findall(pattern2, text))
    #abb.append(re.findall(pattern3, text))
    abb.append([i for i in re.findall(pattern4, text) if 'UNKN' in morph.parse(i[0:len(i)-1])[0].tag])
    abb.append([i[0] for i in re.findall(pattern5, text)])
    return abb

def list_top(list, **n):
    top = cl.Counter(list)
    if not n:
        n = len(list)
    #print (top)
    #print (top.keys())
    top = [(k, top[k]) for k in sorted(cl.OrderedDict(top))]
    top = sorted(top, key=lambda t: (t[1], t[0]), reverse = True)
    #top = cl.OrderedDict(top)
    #top = [(k, top[k]) for k in sorted(top)]
    return top[0:n]

test = 'А.Федорова, М.Д.Триковозова, А.Казарцева, В.Пирожникова, с.ш.а и его шпионы'
print (abbreviations(test))

file = open(input('enter corpus file name'), 'r', encoding='utf-8')
text = file.read()
file.close()
abbs = abbreviations(text)
print (abbs)
file = open ('abb_list.txt', 'w', encoding='utf-8')
out = ''
for i in abbs:
    for j in list_top(i):
        out += '-'.join([str(el) for el in j])
        out += '\n'
file.write(out)
file.close()



