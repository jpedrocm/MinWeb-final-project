# coding: utf-8

import random, time
from nltk import word_tokenize
from nltk.tag import CRFTagger

COMMON_LABEL = u'O'
LABELS = [COMMON_LABEL, u'CPU', u'D', u'HD', u'B']

def get_common_words():
	common_words = []
	common_file = open('common_words.txt', 'r')
	for word in common_file:
		common_words.append(unicode(word.strip()))
	common_file.close()
	return common_words

def get_domain_set():
	full_set = []
	domain_data_file =  open('common_specs.txt', 'r')
	count = 0
	for line in domain_data_file:
		data_line = line.split('`')
		sentence = unicode(data_line[1].strip().decode('utf-8'))
		if sentence != "":
			domain_label = unicode(translate_label(data_line[0]))
			tagged_sentence = tag_sentence(domain_label, sentence)
			full_set.append(tagged_sentence)
	domain_data_file.close()
	return full_set

def get_other_set():
	other_set = []
	other_file = open('other_specs.txt', 'r')
	for line in other_file:
		sentence = unicode(line.strip().decode('utf-8'))
		if sentence != "":
			domain_label = COMMON_LABEL
			tagged_sentence = tag_sentence(domain_label, sentence)
			other_set.append(tagged_sentence)
	other_file.close()
	return other_set

def translate_label(label):
	if label == 'cpu':
		return 'CPU'
	elif label == 'screen':
		return 'D'
	elif label == 'storage':
		return 'HD'
	elif label == 'name':
		return 'B'
	else:
		raise TypeError

def tag_sentence(domain_label, sent):
	tokenized_sent = word_tokenize(sent)
	unicode_sent = map(lambda w: unicode(w), tokenized_sent)
	return [(word, COMMON_LABEL) if word in COMMON_WORDS else (word, domain_label) for word in unicode_sent]

def divide_sets(full_set, pct):
	full_size = len(full_set)
	indexes = [i for i in range(full_size)]
	train_indexes = random.sample(indexes, int(pct*full_size))
	test_indexes = list(set(indexes) - set(train_indexes))

	train_set = [full_set[j] for j in train_indexes]
	test_set = [full_set[k] for k in test_indexes]
	return train_set, test_set

COMMON_WORDS = get_common_words()

def map_test_set(test_set):
	final_test_set = []
	for sent in test_set:
		final_test_set.append(map(lambda (u, t): u, sent))
	return final_test_set

def main():
	start = time.time()

	full_set = get_domain_set()
	full_set.extend(get_other_set())

	train_set, test_set = divide_sets(full_set, 0.75)

	created_sets = time.time()
	print "Created sets in " + str(created_sets-start)

	tagger = CRFTagger()
	tagger.train(train_set, 'laptop.crf.tagger')

	trained = time.time()
	print "Trained tagger in " + str(trained-created_sets)

	evaluated_sents = tagger.tag_sents(map_test_set(test_set))

	print tagger.evaluate(test_set)
	print tagger.tag([u"This", u"is", u"a", u"Dell", u"computer", u"with", u"i5", u"processor"])

	evaluated = time.time()
	print "Evaluated sentences in " + str(evaluated-trained)

main()