#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import csv
import pymorphy2
from glob import glob
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from fuzzysearch import find_near_matches

def breadth_first_search(graph, start_vertex):
	visited = [start_vertex]
	for vertex in visited:
		if vertex in graph.keys():
			visited.extend(graph[vertex])
	return visited
		

def read_onotolgy(ontology_path, categories):
	ontology_data_dict = {}
	with open(ontology_path) as ontology:
		data = csv.reader(ontology, delimiter = '\t')
		ontology_graph = {}
		for line in data:
			ontology_data_dict[line[0]] = line
			if line[2] not in ontology_graph.keys():
				ontology_graph[line[2]] = [line[0]]
			else:
				ontology_graph[line[2]].append(line[0])
				
	vertices = []
	for category in categories:
		if str(category) not in vertices:
			bfs_result = breadth_first_search(ontology_graph,str(category))
			vertices.extend(bfs_result)
		
	result = []
	for term_id in vertices:
		result_dictionary = {
			"id" : ontology_data_dict[term_id][0],
			"term" : ontology_data_dict[term_id][1],
			"category" : ontology_data_dict[term_id][2]}
		result.append(result_dictionary)
		
	return result
	
def calculate_stat(text_paths, categories_info):
	morph = pymorphy2.MorphAnalyzer()
	
	for data in categories_info:
		for word in morph.parse(data["term"]):
			if "NOUN" in word.tag:
				data["term"] = word.normal_form
				break
	
	result = []
	for text_path in text_paths:
		terms_dictionary = {}
		terms_dictionary["filename"] = text_path.split('/')[-1]
		terms_dictionary["term_categories"] = {}
		
		with open(text_path,'r') as text:
			clear_text = re.sub("[^\u0400-\u04FF \-\n]", "", text.read())
			normalized_text = ''
			normalized_words = []
			for word in word_tokenize(clear_text):
				if word not in stopwords.words('russian'):
					normalized_words.append(morph.parse(word)[0].normal_form)
			normalized_text = " ".join(normalized_words)
			
		for data in categories_info:
			term = data['term']
			score = len(find_near_matches(' %s ' % term, normalized_text, max_l_dist=0))
			if score != 0:
				if data['category'] not in terms_dictionary["term_categories"].keys():
					terms_dictionary["term_categories"][data['category']] = {
						"found_terms": [],
						"total_terms": 0}
				terms_dictionary["term_categories"][data['category']]["found_terms"].append(term)
				terms_dictionary["term_categories"][data['category']]["total_terms"] += score
		result.append(terms_dictionary)
				
	return result
		
if __name__ == '__main__':
	categories_info = read_onotolgy("./test_data/ontology.csv", [2,3])
	print("categories_info")
	for line in categories_info:
		print(line)
		
	text_paths = glob("./test_data/texts/*.txt")
	stats = calculate_stat(text_paths, categories_info)
	print("-----------\n-----------")
	print("calculate_stat")
	for line in stats:
		print(line)
