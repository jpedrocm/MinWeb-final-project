def rewrite_domain_labels(part_set):
	domain_data_file = open('most_common_specs.txt', 'r')
	output = open('common_specs.txt', 'w')

	for line in domain_data_file:
		data_line = line.split('`')
		old_label = data_line[0].strip()
		if old_label in part_set:
			domain_label = part_set[old_label]
			sentence = data_line[1].strip()
			output.write(domain_label + '`' + sentence+'\n')
	output.close()
	domain_data_file.close()

FILENAMES = ['screen', 'name', 'cpu', 'storage']

def get_translate_set():
	part_set = {}
	for filename in FILENAMES:
		fi = open(filename+'Attributes.txt', 'r')

		for line in fi:
			new_line = line.strip()
			part_set[new_line] = filename
		fi.close()
	return part_set

def rewrite():
	part_set = get_translate_set()
	rewrite_domain_labels(part_set)

rewrite()