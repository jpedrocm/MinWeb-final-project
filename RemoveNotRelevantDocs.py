import os

relevant_file = open('Data\RelevantDocs.txt', 'r')

relevant_map = {}

for line in relevant_file:
	split_line = line.split()
	folder_name = split_line[0]
	filename = split_line[1].split('\n')[0]
	if folder_name not in relevant_map:
		relevant_map[folder_name] = [filename]
	else:
		relevant_map[folder_name].append(filename)

MY_PATH = os.getcwd() + '\\'

for folder in relevant_map:
	cur_path = MY_PATH + folder + '\\'
	for item in os.listdir(cur_path):
		if item not in relevant_map[folder]:
			os.remove(cur_path+item)