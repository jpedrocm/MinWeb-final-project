import os

MY_PATH = os.getcwd() + '\Data\\'
TEXTS_PATH = MY_PATH + 'Texts\\'
FILT_PATH = MY_PATH + 'Filtered\\'

for filename in os.listdir(TEXTS_PATH):
	name = filename[:-12] + '_filtered.txt'
	new_file = open(FILT_PATH+name, 'w')
	old_file = open(TEXTS_PATH+filename)

	before_line = ""
	for line in old_file:
		strip_line = line.strip() + '\n'
		if strip_line != before_line:
			new_file.write(strip_line)
		before_line = strip_line