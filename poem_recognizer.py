# -*- coding: utf-8 -*-
import sys
import math
import re
import codecs
from collections import Counter
from collections import defaultdict


CHARSET = "utf-8"
DELIMITER = u'@@@@@@@@@@@@@@@@@'


class PoetryRecognizer:
    def __init__(self, paths, test_paths):
        PoetryRecognizer.PATHS = paths
        PoetryRecognizer.TEST_PATHS = test_paths
        self.statistics = list()
        self.poems = 0

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

    def learn(self):
        self.statistics.append(defaultdict(lambda : [0.0, 0.0]))
        self.statistics.append(defaultdict(lambda : [0.0, 0.0]))

        for index, path in enumerate(PoetryRecognizer.PATHS):
            f = codecs.open(path, 'r', encoding=CHARSET)

            for poem in self.get_poems(f):
                three_gramms = Counter(self.get_3gramms(poem))
                for three_gramm in three_gramms:
                    self.statistics[index][three_gramm][0] += three_gramms[three_gramm]
                    self.statistics[index][three_gramm][1] += three_gramms[three_gramm] ** 2
                self.poems += 1

            for three_gramm in self.statistics[index].keys():
                self.statistics[index][three_gramm][0] *= 1.0
                self.statistics[index][three_gramm][0] /= self.poems

                self.statistics[index][three_gramm][1] = (self.statistics[index][three_gramm][1] * 1.0 / self.poems) -\
                                                         self.statistics[index][three_gramm][0] ** 2
                self.statistics[index][three_gramm][1] *= float(self.poems) / (self.poems - 1)

            self.poems = 0


    def count_normal_density(self, mean, var, point_value):
        if var == 0:
            return math.log(10 ** (-8))
        else:
            return  math.exp((-(point_value - mean)**2) / (2 * var)) / ((2 * math.pi * var) ** 0.5)


    def classify(self, poem):
        poem_three_gramms = Counter(self.get_3gramms(poem))

        multivariate_norm_density = [0, 0]
        for poetry_class in [0, 1]:
            for three_gramm in poem_three_gramms:
                if three_gramm in self.statistics[poetry_class]:
                    normal_density_args = self.statistics[poetry_class][three_gramm]
                    value = self.count_normal_density(normal_density_args[0],
                                                      normal_density_args[1],
                                                      float(poem_three_gramms[three_gramm]))
                    if value == 0:
                        value = 1
                    multivariate_norm_density[poetry_class] += math.log(value + 1)
                else:
                    multivariate_norm_density[poetry_class] += math.log(10**(-8))

        if multivariate_norm_density[0] > multivariate_norm_density[1]:
            return 0
        else:
            return 1

    def test(self):
        tests = []
        for index, path in enumerate(PoetryRecognizer.TEST_PATHS):
            f = codecs.open(path, 'r', encoding = CHARSET)
            tests.extend([(poem, index) for poem in self.get_poems(f)])

        correct = 0

        block_correct = 0
        block_incorrect = 0
        black_correct = 0
        black_incorrect = 0

        for poem, answer in tests:
            if self.classify(poem) == answer:
                correct += 1
                if answer == 0:
                    block_correct += 1
                else:
                    black_correct += 1
            else:
                if answer == 0:
                    block_incorrect += 1
                else:
                    black_incorrect += 1



        print("{}/{} Block; {}/{} Black".format(block_correct, block_incorrect + block_correct, black_correct, black_correct + black_incorrect))
        print("{} correct; {} incorrect".format(correct, len(tests) - correct))
        print("Root-mean square error: {0:.2f}%".format((len(tests) - correct) * 100 / len(tests)))



if __name__ == "__main__":
    if (len(sys.argv) != 5):
        print "USAGE: poem_recognizer.py <poem_paths> <test_paths>"
        sys.exit(1)

    sample_block_path = sys.argv[1]
    sample_black_path = sys.argv[2]

    test_block_path = sys.argv[3]
    test_black_path = sys.argv[4]

    sample_paths = [sample_block_path, sample_black_path]
    test_paths = [test_block_path, test_black_path]

    poetry_classifier = PoetryRecognizer(sample_paths, test_paths)
    poetry_classifier.learn()
    poetry_classifier.test()

