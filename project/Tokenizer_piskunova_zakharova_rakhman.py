import re
import time
from pyaspeller import Word
import csv
# import pymorphy2
# morph = pymorphy2.MorphAnalyzer()


class Profiler(object):
    """Returns running time of the program."""
    def __enter__(self):
        self._startTime = time.time()

    def __exit__(self, type, value, traceback):
        print("Elapsed time: {:.3f} секунд".format(time.time() - self._startTime))


class Tokenizer(object):
    """Contains splitter, tokenizer, speller functions, and function that converts the result to csv."""
    def __init__(self, text):
        self.sentences = []
        self.entities = []
        self.hyps = []
        self.entities.extend(re.findall('[А-ЯЁ][а-яё]*\.\s{0,2}[А-ЯЁ]\.\s{0,2}[А-ЯЁ][а-яё]+', text))
        geo = open('geo_objects_par.txt', 'r', encoding='utf-8').read().split('\n')
        hyp = open('hyp_words_par.txt', 'r', encoding='utf-8').read().split('\n')
        for i in geo:
            if len(i) >= 4:
                fnd = re.search('('+i.strip('\ufeff')+')'+'(?:[\s,.!\(\);\"\':?\«\»-])+', text)
                if fnd is not None:
                    x = fnd.group(0).strip(' -')
                    if x not in self.entities:
                        self.entities.append(x)
        for ent in self.entities:
            text = text.replace(ent, 'ŧ' + ent + 'ŧ')
        for h in hyp:
            fnd2 = re.findall(h, text)
            for k in fnd2:
                self.hyps.extend(fnd2)
        for w in self.hyps:
            text = text.replace(w, 'ɀ' + w + 'ɀ')
        self.text = text.replace('\ufeff', '')
        self.splitted = []

    def split_to_sentences(self):
        """Takes a string (text) and returns list of sentences."""
        endings = re.findall('([^\.а-яёА-ЯЁ]\.+ |[а-яё])\.+ |!+ |\?+ |$', self.text)
        self.splitted = re.split('[^\.а-яёА-ЯЁ]\.+ |[а-яё]\.+ |!+ |\?+ ', self.text.replace('#', ' #'))
        for i in range(len(self.splitted)):
            self.splitted[i] += endings[i]
        return self.splitted

    def tokenize(self):
        """Takes sentences from the function above and returns lists of 
        tuples with pairs like %%word%% --- %%tag%%."""
        emojis = self.add_list('emojis.txt')
        smiles = self.add_list('text_smiles.txt')
        for k in range(len(smiles)):
            smiles[k] = smiles[k].replace('\\', '\\\\')
            smiles[k] = smiles[k].replace('|', '\|')
            smiles[k] = smiles[k].replace('[', '\[')
            smiles[k] = smiles[k].replace('*', '\*')
            smiles[k] = smiles[k].replace(']', '\]')
            smiles[k] = smiles[k].replace('.', '\.')
        emoji_string = '[' + ''.join(emojis) + ']'
        pre_smile_string = '|'.join(smiles).replace('(', '\(')
        pre_smile_string = pre_smile_string.replace(')', '\)')
        smile_string = '('+pre_smile_string+')'
        scanner = re.Scanner([
            ("[^#ŧɀ][0-9]+", lambda scanner, token: (token.strip(), "num")),
            ("[^#ŧ\"\«»,:;!\?\(\.ɀ-][а-яёА-ЯЁ]+[^\.,!]", lambda scanner, token: (token.strip(), "word")),
            ("[^#ŧ/:](h[^t]|t[^t]|w[^w])[a-zA-Z]+[^\.,!]", lambda scanner, token: (token.strip(), "enword")),
            ("[^#ŧ(](http|www)[\/:a-zA-Z0-9_\.]+", lambda scanner, token: (token.strip(), "link")),
            ("[^#ŧ(][a-z0-9\.-_]+@[a-z]{2,}(\.[a-z]+)+", lambda scanner, token: (token.strip(), "link")),
            ("[^\s][(+9*(*]+", lambda scanner, token: (token.strip(), "smile")),
            ("[)+0*)*]{2,}", lambda scanner, token: (token.strip(), "smile")),
            ("[>:;xX]+[-]*[()Pp]+", lambda scanner, token: (token.strip(), "smile")),
            (smile_string, lambda scanner, token: (token.strip(), "smile")),
            ("#[a-zA-Zа-яёА-ЯЁ_]+", lambda scanner, token: (token.strip(), "hashtag")),
            ("ŧ([a-zA-Zа-яёА-ЯЁ\s\.\-]*)ŧ", lambda scanner, token: (token.strip('ŧ'), "entity")),
            ("[^#ŧ\"\.«»,:;!\?]ɀ([а-яёА-ЯЁ]+)ɀ", lambda scanner, token: (token.strip('ɀ'), "word")),
            ("ɀ([а-яёА-ЯЁ]+-[а-яёА-ЯЁ]+)ɀ", lambda scanner, token: (token.strip('ɀ'), "word")),
            ("ɀ([а-яё]+\.[а-яё]+\.)ɀ", lambda scanner, token: (token.strip('ɀ'), "word")),
            ("[,\.!\(\);\"\':?\«\»-]+", lambda scanner, token: (token.strip(), "punct")),
            (emoji_string, lambda scanner, token: (token.strip(), "emoji")),
            ("\W[а-яёА-ЯЁ]\s", lambda scanner, token: (token.strip(), "word")),
            ("\s+", None)  # None == skip token.
        ])
        for sent in self.split_to_sentences():
            result = []
            result.extend(scanner.scan(sent)[0])
            sent_rest = scanner.scan(sent)[1]
            while sent_rest != '':
                result.append((sent_rest.split()[0], 'unknown'))
                sent_rest = ' '.join(sent_rest.split()[1:])
                result.extend(scanner.scan(sent_rest)[0])
                sent_rest = scanner.scan(sent_rest)[1]
            self.sentences.append(list(result))
        return self.sentences

    def speller(self):
        """Takes lists of tuples from the function below, 
        checks word spelling and returns corrected pairs %%word%% --- %%tag%%."""
        words = [i for i in self.tokenize()]
        pairs = []
        for i in words:
            for j in i:
                pairs.append(list(j))
        for p in pairs:
            if p[1] == 'word':
                check = Word(p[0].lower())
                if check.correct == False:
                    p.pop(0)
                    p.insert(0, check.spellsafe)
        return pairs

    @staticmethod
    def add_list(filename):
        f = open(filename, 'r', encoding='utf-8')
        return [line.strip() for line in f]

def tokens_to_file(documents):
    """Creates a csv file from the pairs %%word%% --- %%tag%% (without spell checking)."""
    file = open('tokens2.csv', 'w', encoding='utf-8')
    writer = csv.writer(file, delimiter = '\t', lineterminator="\n")
    row0 = ['TextId', 'Id', 'Token', 'Type']
    writer.writerow(row0)
    textid = 0
    tokid = 0
    for document in documents:
        for sentence in Tokenizer(document).tokenize():
            for token in sentence:
                print(token)
                row = [textid, tokid, token[0], token[1]]
                writer.writerow(row)
                tokid += 1
        textid += 1

    file.close()

def tokens_to_file_speller(documents):
    """Creates a csv file from the pairs %%word%% --- %%tag%% (with spell checking)."""
    file = open('tokens.csv', 'w', encoding='utf-8')
    writer = csv.writer(file, delimiter = '\t', lineterminator="\n")
    row0 = ['TextId', 'Id', 'Token', 'Type']
    writer.writerow(row0)
    textid = 0
    tokid = 0
    for document in documents:
        for token in Tokenizer(document).speller():
            row = [textid, tokid, token[0], token[1]]
            writer.writerow(row)
            tokid += 1
        textid += 1

    file.close()

f = open('VKCorpClean.csv', 'r', encoding='utf-8')
tokens_to_file([f.read()])
