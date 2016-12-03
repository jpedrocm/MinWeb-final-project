# coding: utf-8

import random, time, re
from nltk import word_tokenize
from nltk.tag import CRFTagger
from nltk.metrics import *

COMMON_LABEL = u'O'
STOP_LABELS = [u'CPU', u'D', u'HD', u'B']
LABELS = [u'CPU', u'D', u'HD', u'B', u'O']
DEBUG = []

def get_common_words():
	common_words = []
	common_file = open('common_words.txt', 'r')
	for word in common_file:
		common_words.append(code_sentence(word))
	common_file.close()
	return common_words

def code_sentence(sentence):
	return unicode(sentence.strip().decode('utf-8').replace(u'\xa0', u' '))

def get_domain_set(no_stopwords):
	full_set = []
	domain_data_file =  open('common_specs.txt', 'r')
	count = 0
	for line in domain_data_file:
		data_line = line.split('`')
		sentence = code_sentence(data_line[1])
		if sentence != "":
			domain_label = unicode(translate_label(data_line[0]))
			tagged_sentence = ""
			if no_stopwords:
				tagged_sentence = tag_sentence_no_stopwords(domain_label, sentence)
			else:
				tagged_sentence = tag_sentence(domain_label, sentence)
			full_set.append(tagged_sentence)
	domain_data_file.close()
	return full_set

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

def tag_sentence_no_stopwords(domain_label, sent):
	tokenized_sent = word_tokenize(sent)
	unicode_sent = [unicode(w) for w in tokenized_sent if w not in COMMON_WORDS]
	return [(word, domain_label) for word in unicode_sent]

def get_other_set():
	other_set = []
	other_file = open('other_specs.txt', 'r')
	for line in other_file:
		sentence = code_sentence(line)
		if sentence != "":
			domain_label = COMMON_LABEL
			tagged_sentence = tag_sentence(domain_label, sentence)
			other_set.append(tagged_sentence)
	other_file.close()
	return other_set

def divide_sets(full_set, pct):
	full_size = len(full_set)
	indexes = [i for i in range(full_size)]
	train_indexes = random.sample(indexes, int(pct*full_size))
	test_indexes = list(set(indexes) - set(train_indexes))

	train_set = [full_set[j] for j in train_indexes]
	test_set = [full_set[k] for k in test_indexes]
	return train_set, test_set

COMMON_WORDS = get_common_words()

def map_test_set(test_set, word):
	final_test_set = []
	for sent in test_set:
		if word:
			final_test_set.append(map(lambda (u, t): u, sent))
		else:
			final_test_set.append(map(lambda (u, t): t, sent))
	return final_test_set

def get_manual_set(no_stopwords):
	manual_set = []
	manual_file = open('manual_tags.txt', 'r')
	for line in manual_file:
		new_line = code_sentence(line)
		vector_sentence = new_line.split(' ')
		vector_sentence = filter(lambda w: w != u" " or w!= u'', vector_sentence)
		tagged_sentence = [(vector_sentence[i], vector_sentence[i+1]) for i in range(0, len(vector_sentence), 2)]
		if no_stopwords:
			tagged_sentence = filter(lambda (w,l): l != u'O', tagged_sentence)
		if len(tagged_sentence) > 0:
			manual_set.append(tagged_sentence)
	manual_file.close()
	return manual_set

def feature_extraction(tokens, idx):
	token = tokens[idx]

	DEBUG.append(tokens[idx])
	feature_list = []

	#if tokens[idx] in LABELS:
	#	print tokens[idx-1].encode('utf-8')

	if not token:
		return feature_list

	# First letter capitalized
	if token[0].isupper():
		feature_list.append('FIRST_CAPITALIZED')
	# All letters capitalized
	if token.isupper():
		feature_list.append('ALL_CAPITALIZED')
	# Has a number
	if re.search("\d", token) is not None:
		feature_list.append('HAS_NUM')
	# Does not have chars
	if re.search("[^a-zA-Z]*", token) is not None:
		feature_list.append('NOT_CHARS')
	#Has colon
	if re.search("\:", token) is not None:
		feature_list.append("HAS_COLON")
	# Has quotes
	if u"'" in token or u'"' in token:
		feature_list.append("HAS_QUOTES")
	# Is a number TODO
	#if re.search(, token) is not None:
	#	feature_list.append('IS_NUM')
	# Has a dot
	if re.search(u"\.", token) is not None:
		feature_list.append('HAS_DOT')
	#Has parenthesis
	if re.search(u"\(", token) is not None:
		feature_list.append('HAS_PARENTHESIS(')
	elif re.search(u"\)", token) is not None:
		feature_list.append('HAS_PARENTHESIS)')
	#Has an hifen
	if re.search(u"-", token) is not None:
		feature_list.append('HAS_HIFEN')
	# Previous word
	if idx-1 >= 0:
		feature_list.append('PREVIOUS_WORD_' + tokens[idx-1])
	else:
		feature_list.append('PREVIOUS_WORD_<s>')
	## Next word
	if idx+1 < len(tokens):
		feature_list.append('NEXT_WORD_' + tokens[idx+1])
	else:
		feature_list.append('NEXT_WORD_<\s>')
	#	
	#Is punctuation
	#punc_cat = set(["Pc", "Pd", "Ps", "Pe", "Pi", "Pf", "Po"])
	#if all (unicodedata.category(x) in punc_cat for x in token):
	#	feature_list.append('PUNCTUATION')
	#	feature_list.append('SENT_SIZE_'+str(len(tokens)))

	if len(token) > 1:
		feature_list.append('SUF_' + token[-1:])
	if len(token) > 2: 
		feature_list.append('SUF_' + token[-2:])

	feature_list.append('WORD_' + token)
	return feature_list

def create_vector_of_predicted_labels(tagged_sents):
	predicted_labels = []
	labels_per_sent = map_test_set(tagged_sents, word=False)

	for labels in labels_per_sent:
		predicted_labels.extend(labels)
	return predicted_labels

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

def calculate_micro_accuracy(predicted, golden, no_stopwords):
	metric = {}
	considered_labels = []

	conf_matrix = ConfusionMatrix(golden, predicted)

	if no_stopwords:
		considered_labels = STOP_LABELS
	else:
		considered_labels = LABELS
	print considered_labels

	den = sum([conf_matrix[class1, class2] for class1 in considered_labels for class2 in considered_labels])
	num = sum([conf_matrix[class1, class1] for class1 in considered_labels])
	metric['SYSTEM_ACC'] = float(num)/den

	for ithclass in considered_labels:
		part_den_row = sum([conf_matrix[ithclass, class_column_idx] if class_column_idx != ithclass else 0 for class_column_idx in considered_labels])
		part_den_column = sum([conf_matrix[class_row_idx, ithclass] if class_row_idx != ithclass else 0 for class_row_idx in considered_labels])
		metric[ithclass+'_ACC'] = float(num)/(num+part_den_row+part_den_column)

	return metric

def main(no_stopwords, use_manual_train_set):

	print "MAINTAIN COMMON WORDS: " + str(not no_stopwords)
	print "USING HAND LABELED TRAIN DATA: " + str(use_manual_train_set)

	full_set = get_domain_set(no_stopwords)
	if not no_stopwords:
		full_set.extend(get_other_set())

	train_set, test_set_auto = divide_sets(full_set, 0.75)
	set_manual = get_manual_set(no_stopwords)

	train_set_manual = []
	test_set_manual = []
	if use_manual_train_set:
		train_set_manual, test_set_manual = divide_sets(set_manual, 0.28)
		train_set.extend(train_set_manual)
	else:
		test_set_manual = set_manual

	tagger = CRFTagger(feature_func=feature_extraction)
	try:
		tagger.train(train_set, 'laptop.crf.tagger')
	except ValueError:
		fi = open('DEBUG', 'w')
		for li in DEBUG:
			fi.write(str(li.encode('utf-8')) + '\n')
		fi.close()

	print "AUTOMATIC LABELED TEST"
	tagged_sents_auto = tagger.tag_sents(map_test_set(test_set_auto, word=True))
	predicted_auto = create_vector_of_predicted_labels(tagged_sents_auto)
	golden_auto = create_vector_of_predicted_labels(test_set_auto)

	print calculate_micro_accuracy(predicted_auto, golden_auto, no_stopwords)

	print "MANUAL LABELED TEST"
	tagged_sents_manual = tagger.tag_sents(map_test_set(test_set_manual, word=True))
	predicted_manual = create_vector_of_predicted_labels(tagged_sents_manual)
	golden_manual = create_vector_of_predicted_labels(test_set_manual)
	
	print calculate_micro_accuracy(predicted_manual, golden_manual, no_stopwords)
	print ""
	
main(True, True)
main(False, True)
main(True, False)
main(False, False)