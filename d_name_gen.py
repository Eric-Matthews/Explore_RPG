import random

class Culture_type(object):
	names = {'Ca': ['ssidy', 'rlie', 'dan', 'ri', 'lica', 'ctor', 'rles', 'mi', 'rea', 'nda'], 
	'Cha': ['ssidy', 'rlie', 'dan', 'ri', 'lica', 'ctor', 'rles', 'mi', 'rea', 'nda'], 
	'Ai': ['ssidy', 'rlie', 'dan', 'ri', 'lica', 'ctor', 'rles', 'mi', 'rea', 'nda'], 
	'Yu': ['ssidy', 'rlie', 'dan', 'ri', 'lica', 'ctor', 'rles', 'mi', 'rea', 'nda'],
	'Ange': ['ssidy', 'rlie', 'dan', 'ri', 'lica', 'ctor', 'rles', 'mi', 'rea', 'nda'],
	'Vi': ['ssidy', 'rlie', 'dan', 'ri', 'lica', 'ctor', 'rles', 'mi', 'rea', 'nda'],
	'A': ['ssidy', 'rlie', 'dan', 'ri', 'lica', 'ctor', 'rles', 'mi', 'ndrea', 'nda'],
	'Li': ['ssidy', 'rlie', 'dan', 'ri', 'lica', 'ctor', 'rles', 'mi', 'rea', 'nda']}
	
	def __init__(self, name_parts = None):
		self.name_stems = []
		if name_parts == None: name_array = type(self).names
		else: name_array = name_parts
		if __debug__ == False: print 'initialising name_gen'
		
		for entry in name_array:
			if __debug__ == False: print entry
			self.name_stems.append(entry)
			setattr(self, entry, name_array[entry])
		if __debug__ == False: print self, "online."

def person_name_gen(culture = Culture_type(), existing_names = []):
	attempt = 0
	is_name = True
	while is_name == True:
		if __debug__ == False: print "failed attempts: {}".format(attempt)
		first = random.choice(culture.name_stems)
		second = ''
		if hasattr(culture, first):
			second = random.choice(getattr(culture, first))
		name = first + second
		if name not in existing_names:
			existing_names.append(name)
			is_name = False
		else:
			is_name = True
			attempt += 1
	if __debug__ == False: print len(existing_names)
	return name
	
	
if __name__ == '__main__':
	print "Name Gen Running!"
	for i in range(1,20):
		print person_name_gen()