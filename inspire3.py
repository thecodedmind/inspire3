import memory
from textblob import TextBlob, Word
from textblob.sentiments import NaiveBayesAnalyzer
from textblob.np_extractors import ConllExtractor
import shlex

class InspireListener:
	"""Class for learning new objects and templates"""
	def __init__(self, **kwargs):
		self.data = memory.Memory(path='inspire.toml', engine='toml')
		self.analyzer = NaiveBayesAnalyzer()
		self.extractor = ConllExtractor()
		self.debug = kwargs.get('debug', False)
		self.name = kwargs.get('name', 'Athena')
		self.identity = self.data.get(self.name.lower(), {})
		print(f"== IDENTITY ==\n {self.name}\n{self.identity}")
		self.parsers = [
		{ 'pattern': [ "NN", "VBZ", "JJ" ], 'trigger': self._xisy_Parser },
		{ 'pattern': [ "NNS", "VBP", "JJ" ], 'trigger': self._xisy_Parser },
		{ 'pattern': [ "NNP", "VBZ", "JJ" ], 'trigger': self._xisy_Parser },
		{ 'pattern': ['NN', 'VBZ', 'RB', 'JJ'], 'trigger': self._xisnoty_Parser },
		{ 'pattern': ['NNS', 'VBP', 'RB', 'VB'], 'trigger': self._xisnoty_Parser },
		{ 'pattern': ['NNP', 'VBZ', 'RB', 'JJ'], 'trigger': self._xisnoty_Parser },
		{ 'pattern': ['NN', 'NNP'], 'trigger': self._xprop_Parser },
		{ 'pattern': ['NN', 'NNS'], 'trigger': self._xprop_Parser },
		{ 'pattern': ['NN', 'VBZ', 'RB', 'VB'], 'trigger': self._xnotprop_Parser },
		{ 'pattern': ['NNP', 'VBZ', 'RB', 'VB'], 'trigger': self._xnotprop_Parser },
		{ 'pattern': ['PRP', 'VBP', 'JJ'], 'trigger': self._introspective_positive_Parser },
		{ 'pattern': ['PRP', 'VBP', 'VBG'], 'trigger': self._introspective_positive_Parser },
		{ 'pattern': ['PRP', 'VBP', 'RB', 'VBG'], 'trigger': self._introspective_modifier_Parser },
		{ 'pattern': ['PRP', 'VBP', 'RB', 'JJ'], 'trigger': self._introspective_negative_Parser },
		# ['NNS', 'VBP', 'RB', 'JJ'] x are y z
		# ['NN', 'VBP', 'JJ'] possibly i am x
		# ['NN', 'VBP', 'RB', 'JJ'] i am not x
		# ['NNP', 'NNS', 'NNS'] x y(does) z
		# ['NNP', 'VBZ', 'NNP'] x y(does) z
		]
	
	def _introspective_modifier_Parser(self, text, author):
		target = self.extract('PRP', text).lower()
		mid = self.extract('VBP', text).lower()
		mod = self.extract('RB', text).lower()
		is_prop = self.extract('JJ', text) or self.extract('VBG', text)
		is_prop = is_prop.lower()
		
		if mid == "are":
			mid = "am"
			
		if target == "you":
			target = self.name.lower()
		
		data = self.data.get(target, {})
		
		if data.get(is_prop, 'null') == 'null':
			data[is_prop] = 'null'
			
		if data.get(is_prop) == mod:
			return f"Yes, I {mid} {mod} {is_prop}."
		
		if self.identity.get('learning', '') == 'always':
			msg = f"Understood, I {mid} {mod} {is_prop}."
			if not data.get(is_prop) != mod:
				msg = f"Understood, I {mid} {mod} {is_prop} now."
				
			data[is_prop] = mod	
			self.data._set(target, data)
			return msg
		
		elif self.identity.get('learning', '') == 'restricted':
			if author == self.identity.get('master', None) or author == 'master':
				msg = f"Understood, I {mid} {mod} {is_prop}."
				if not data.get(is_prop) == mod:
					msg = f"Understood, I {mid} {mod} {is_prop} now."
					
				data[is_prop] = mod
				self.data._set(target, data)
				return msg
			else:
				return f"No, I {mid} not {mod} {is_prop}."
		else:
			return f"No, I {mid} not {mod} {is_prop} and you can't change my mind."
		
	def _introspective_positive_Parser(self, text, author):
		target = self.extract('PRP', text).lower()
		mid = self.extract('VBP', text).lower()
		is_prop = self.extract('JJ', text) or self.extract('VBG', text)
		is_prop = is_prop.lower()
		
		if mid == "are":
			mid = "am"
			
		if target == "you":
			target = self.name.lower()
		
		data = self.data.get(target, {})
		
		if data.get(is_prop, 'null') == 'null':
			data[is_prop] = 'null'
			
		if data.get(is_prop) == True:
			return f"Yes, I {mid} {is_prop}."
		
		if self.identity.get('learning', '') == 'always':
			msg = f"Understood, I {mid} {is_prop}."
			if not data.get(is_prop):
				msg = f"Understood, I {mid} {is_prop} now."
				
			data[is_prop] = True	
			self.data._set(target, data)
			return msg
		
		elif self.identity.get('learning', '') == 'restricted':
			if author == self.identity.get('master', None) or author == 'master':
				msg = f"Understood, I {mid} {is_prop}."
				if not data.get(is_prop):
					msg = f"Understood, I {mid} {is_prop} now."
					
				data[is_prop] = True
				self.data._set(target, data)
				return msg
			else:
				return f"No, I {mid} not {is_prop}."
		else:
			return f"No, I {mid} not {is_prop}."

	def _introspective_negative_Parser(self, text, author):
		target = self.extract('PRP', text).lower()
		is_prop = self.extract('JJ', text) or self.extract('VBG', text)
		is_prop = is_prop.lower()
		
		mid = "am not"
			
		if target == "you":
			target = self.name.lower()
		
		data = self.data.get(target, {})
		
		if data.get(is_prop, 'null') == 'null':
			data[is_prop] = 'null'
			
		if data.get(is_prop) == False:
			return f"Yes, I am not {is_prop}."
		
		if self.identity.get('learning') == 'always':
			msg = f"Understood, I am not {is_prop}."
			if not data.get(is_prop):
				msg = f"Understood, I am not {is_prop} now."
				
			data[is_prop] = False	
			self.data._set(target, data)
			return msg
		
		elif self.identity.get('learning', '') == 'restricted':
			if author == self.identity.get('master', None) or author == 'master':
				msg = f"Understood, I am not {is_prop}."
				if not data.get(is_prop):
					msg = f"Understood, I am not {is_prop} now."
					
				data[is_prop] = False
				self.data._set(target, data)
				return msg
			else:
				return f"No, I am {is_prop}."
		else:
			return f"No, I am {is_prop}."
		
	def _xnotprop_Parser(self, text, author):
		target = self.extract('NN', text) or self.extract('NNP', text)
		target = target.lower()
		is_prop = self.extract('VB', text).lower()
		data = self.data.get(target, {})
		props = data.get('properties', [])
		
		if is_prop not in props:
			return f"I can confirm {target} does not {is_prop}."
		
		if self.identity.get('learning', '') == 'always':
			props.remove(is_prop)
			data['properties'] = props
			self.data._set(target, data)
			return f"Understood, {target} does not {is_prop}"
		
		elif self.identity.get('learning', '') == 'restricted':
			if author == self.identity.get('master', None) or author == 'master':
				props.remove(is_prop)
				data['properties'] = props
				self.data._set(target, data)
				return f"Understood, {target} does not {is_prop}"
			else:
				return f"I have no information for wether {target} {is_prop} or not."
		else:
			return f"I have no information for wether {target} {is_prop} or not."
		
	def _xprop_Parser(self, text, author):
		target = self.extract('NN', text).lower()
		is_prop = self.extract('NNP', text) or self.extract('NNS', text)
		is_prop = is_prop.lower()
		data = self.data.get(target, {})
		props = data.get('properties', [])
		
		if is_prop in props:
			return f"I can confirm {target} {is_prop}."
		
		if self.identity.get('learning', '') == 'always':
			props.append(is_prop)
			data['properties'] = props
			self.data._set(target, data)
			return f"Understood, {target} {is_prop}"
		
		elif self.identity.get('learning', '') == 'restricted':
			if author == self.identity.get('master', None) or author == 'master':
				props.append(is_prop)
				data['properties'] = props
				self.data._set(target, data)
				return f"Understood, {target} {is_prop}"
			else:
				return f"I have no information for wether {target} {is_prop} or not."
		else:
			return f"I have no information for wether {target} {is_prop} or not."
		
	def _xisnoty_Parser(self, text, author):
		target = self.extract('NN', text) or self.extract('NNP', text) or self.extract('NNS', text)
		target = target.lower()
		is_prop = self.extract('JJ', text) or self.extract('NN', text, 1) or self.extract('VB', text)
		is_prop = is_prop.lower()
		
		data = self.data.get(target, {})
		
		mid = self.extract('VBP', text).lower()
			
		if data.get(is_prop, 'null') == 'null':
			data[is_prop] = 'null'	
			
		if data.get(is_prop) == False:
			return f"Yes, {target} {mid} not {is_prop}."
		
		if self.identity.get('learning', '') == 'always':
			msg = f"Understood, {target} {mid} not {is_prop}."
			if data.get(is_prop) == True:
				msg = f"Understood, {target} {mid} not {is_prop} anymore."
				
			data[is_prop] = False
			self.data._set(target, data)
			return msg
		
		elif self.identity.get('learning', '') == 'restricted':
			if author == self.identity.get('master', None) or author == 'master':
				msg = f"Understood, {target} {mid} not {is_prop}."
				if data.get(is_prop) == True:
					msg = f"Understood, {target} {mid} not {is_prop} anymore."
				data[is_prop] = False	
				self.data._set(target, data)
				return msg
			else:
				return f"No, {target} {mid} {is_prop}."
		else:
			return f"No, {target} {mid} {is_prop}."
			
	def _xisy_Parser(self, text, author):
		target = self.extract('NN', text) or self.extract('NNP', text) or self.extract('NNS', text)
		target = target.lower()
		mid = self.extract('VBP', text) or self.extract('VBZ', text)
		mid = mid.lower()
		is_prop = self.extract('JJ', text) or self.extract('NN', text, 1)
		is_prop = is_prop.lower()
		data = self.data.get(target, {})
		
		if data.get(is_prop, 'null') == 'null':
			data[is_prop] = 'null'
			
		if data.get(is_prop) == True:
			return f"Yes, {target} {mid} {is_prop}."
		
		if self.identity.get('learning', '') == 'always':
			msg = f"Understood, {target} {mid} {is_prop}."
			if not data.get(is_prop):
				msg = f"Understood, {target} {mid} {is_prop} now."
				
			data[is_prop] = True	
			self.data._set(target, data)
			return msg
		
		elif self.identity.get('learning', '') == 'restricted':
			if author == self.identity.get('master', None) or author == 'master':
				msg = f"Understood, {target} {mid} {is_prop}."
				if not data.get(is_prop):
					msg = f"Understood, {target} {mid} {is_prop} now."
					
				data[is_prop] = True
				self.data._set(target, data)
				return msg
			else:
				return f"No, {target} {mid} not {is_prop}."
		else:
			return f"No, {target} {mid} not {is_prop}."
		
	def extract(self, tag, sent, index=0):
		count = 0
		for item in sent.tags:
			if item[1].lower() == tag.lower():
				if count == index:
					return item[0]
				count += 1
	def saveTemplate(self, ls):
		tags = []
		for item in ls:
			tags.append(item[1])
			
		data = self.data._get('templates', [])
		
		if tags not in data:
			self.log(f"Saving sentence template")
			data.append(tags)
			self.data._set('templates', data)	
		
		return tags
		
	def log(self, message="", *, tag='debug'):
		if not self.debug and tag == 'debug':
			return
		
		print(f'{tag}: {message}')
			
	def read(self, message, *, sender="master"):
		self.log(f'I heard... {message}', tag=self.name)
		for line in TextBlob(message, analyzer=self.analyzer, np_extractor=self.extractor).sentences:
			self.log(tag='')
			
			self.log(line)

			tags = line.tags
			self.log(f"{tags}", tag='tags')
			#np = line.noun_phrases
			#self.log(f"{np}", tag='np')
			template = self.saveTemplate(tags)
			self.log(template, tag='template')
			for item in self.parsers:
				if item['pattern'] == template:
					return f"{self.name}: {item['trigger'](line, sender)}" 
			
ls = InspireListener(debug=True, name='Silmeria')
print("=== Inspire3 Debug Environment ===")
print(ls.read("traps are sometimes gay"))
#print(ls.read("you aren't dumb"))
#print(ls.read("i am smart", sender='Kaiser'))
#print(ls.read("i am not dumb", sender='Kaiser'))
#print(ls.read('kronix is weird'))
