# -*- coding: utf-8 -*-
from __future__ import division
from collections import defaultdict
from math import log
import re
import sys
import codecs


CHARSET = "utf-8"
DELIMITER = u'@@@@@@@@@@@@@@@@@'


class PoetryClassifier:
    PATHS = list()
    TEST_PATHS = list()

    def __init__(self, sample_paths, test_paths):
        self.features = list()
        self.classifier = tuple()
        PoetryClassifier.PATHS = sample_paths
        PoetryClassifier.TEST_PATHS = test_paths

    def get_words(self, text):
        reg = re.compile(ur'[А-Яа-я\w]+')
        return reg.findall(text)

    def get_3gramms(self, poem):
        for line in poem.split('\n'):
            for word in self.get_words(line):
                if len(word) < 3:
                    continue
                _3gramm = list(word[:2])
                for letter in word[2:]:
                    _3gramm.append(letter)
                    yield ''.join(_3gramm)
                    _3gramm = _3gramm[1:]

    def get_poems(self, fileobj):
        poem = []
        for line in fileobj:
            line = line.strip()
            if len(line) == 0:
                continue
            if line == DELIMITER:
                yield u' '.join(poem)
                poem = []
                continue
            poem.append(line)
        if len(poem) > 0:
            yield u' '.join(poem)


    def get_features(self, sample):
        return tuple(self.get_3gramms(sample))

    def learn(self):
        samples = []
        for index, path in enumerate(PoetryClassifier.PATHS):
            f = codecs.open(path, 'r', encoding=CHARSET)
            samples.extend([(poem, index) for poem in self.get_poems(f)])
        self.features = [(self.get_features(feat), label) for feat, label in samples]
        self.classifier = self.train()

    def train(self):
        class_freq = defaultdict(lambda: 0)
        feat_freq = defaultdict(lambda: 0)
        for feats, label in self.features:
            class_freq[label] += 1                 # count classes frequencies
            for feat in feats:
                feat_freq[label, feat] += 1          # count features frequencies

        for label, feat in feat_freq:                # normalize features frequencies
            feat_freq[label, feat] /= class_freq[label]
        for class_ in class_freq:                       # normalize classes frequencies
            class_freq[class_] /= len(self.features)

        return class_freq, feat_freq                   # return P(C) and P(O|C)

    def classify(self, features):
        classes, prob = self.classifier
        return min(classes.keys(),              # calculate argmin(-log(C|O))
            key = lambda class_: -log(classes[class_]) + \
                sum(-log(prob.get((class_,feature), 10**(-7))) for feature in features))


    def test(self):
        tests = []
        for index, path in enumerate(self.TEST_PATHS):
            f = codecs.open(path, 'r', encoding = CHARSET)
            tests.extend([(poem, index) for poem in self.get_poems(f)])
        features = [(self.get_features(feat), label) for feat, label in tests]

        correct = 0

        for test, ans in features:
            if self.classify(test) == ans:
                correct += 1

        print("{} correct; {} incorrect".format(correct, len(features) - correct))
        print("Root-mean square error: {0:.2f}%".format((len(features) - correct) * 100 / len(features)))


if __name__ == "__main__":
    if (len(sys.argv) != 5):
        print "USAGE: PoetryRecognizer.py <sample_file_Black_poetry> <sample_file_Block_poetry>" \
              "<test_file_1_path> <test_file_2_path>"
        sys.exit(1)

    sample_block_path = sys.argv[1]
    sample_black_path = sys.argv[2]

    test_block_path = sys.argv[3]
    test_black_path = sys.argv[4]

    sample_paths = [sample_block_path, sample_black_path]
    test_paths = [test_block_path, test_black_path]

    poetry_classifier = PoetryClassifier(sample_paths, test_paths)
    poetry_classifier.learn()
    poetry_classifier.test()





