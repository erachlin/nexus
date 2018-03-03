import urllib 
from urllib import urlopen as uReq
import re
from string import ascii_lowercase as alpha
import bs4
from bs4 import BeautifulSoup as soup
from helper_functions import *
import pandas as pd
import networkx as nx



class wiki_page:

	url = ''

	def __init__(self, in_name):
		page_name = in_name.split('.')[0]
		self.name = page_name
		self.supercategories = []
		self.weight = 0
		self.unweighted_main_topic_name = ""
		self.weighted_main_topic_name = ""
		self.tree_traversal_list = []


	def add_supercategory(self, in_supercategory):
		
		self.supercategories.append(in_supercategory)

	def add_url(self, in_url):
		self.url = in_url

	def get_weight(self):

		return self.weight

	def get_highest_weighted_supercategory(self):
		if self.supercategories:
			highest_supercategory = self.supercategories[0]
			highest_supercategory_weight = self.supercategories[0].get_weight()
			if len(self.supercategories) > 1:
				for supercategory in self.supercategories:
					if supercategory.get_weight() > highest_supercategory_weight:
						highest_supercategory = supercategory
						highest_supercategory_weight = supercategory.get_weight()

			return highest_supercategory
		else:
			return self

	def add_unweighted_main_topic(self, in_main_topic):
		self.unweighted_main_topic = in_main_topic.name

	def get_unweighted_main_topic(self):

		return self.unweighted_main_topic_name

	def set_weighted_main_topic(self, starting_topic):

		if len(self.tree_traversal_list) == 0:
			self.weighted_main_topic_name == starting_topic

		elif self.tree_traversal_list[-1] == starting_topic:
			self.weighted_main_topic_name = self.tree_traversal_list[-2].name

		else:
			self.weighted_main_topic_name = self.tree_traversal_list[-1].name

		
	def get_weighted_main_topic(self):

		return self.weighted_main_topic_name



	def add_tree_traversal_list(self, in_category_list):

		self.tree_traversal_list = in_category_list

	def add_weight(self, in_weight):

		self.weight += in_weight



	def make_node(self):
		print 'TODO'

class category(wiki_page):


	def __init__(self, in_name):
		page_name = in_name.split('.')[0]
		self.name = page_name
		self.supercategories = []
		self.subcategories = []
		self.subpages = []
		self.weight = 0
		self.has_populated = "false"
		self.closest_main_topic_name = ""

	def add_subcategory(self,in_subcategory):

		self.subcategories.append(in_subcategory)
		self.weight += 1

	def add_subpage(self, in_subpage, subpage_weight_factor):

		self.subpages.append(in_subpage)
		self.weight += 1 * subpage_weight_factor



		return self.get_weight()


	def populate_weight(self):

		weight = self.weight
		if self.has_populated == "true":

			return

		for supercategory in self.supercategories:
			
			supercategory.add_weight(weight)


		self.has_populated = "true"
  




def get_subcategories(current_category, page_soup, urls, BASE_URL, fixed_name, incomplete_categories, Graph):
		
		subcategory_data = page_soup.findAll("a", {"class":"CategoryTreeLabel"})

		name = fixed_name.replace('_', ":", 1)
		next_page_data = page_soup.findAll("a", {"title":name})
	
		next_page = check_for_next_page(name, next_page_data)

		if next_page != 'none':
			incomplete_categories.append(current_category.name)
		
		for subcategory in subcategory_data:
			class_name = fix_name(subcategory["href"])
			
			if len(urls) < 30000:
					urls.append(BASE_URL + subcategory["href"])
			current_category.add_subcategory(class_name)
			Graph.add_edge(current_category.name, class_name)


def get_pages(current_category, page_soup, page_list, fixed_name, BASE_URL, SUBPAGE_WEIGHT_FACTOR, Graph):

	url_list = []
	pagedata = page_soup.findAll("div", {"id":"mw-pages"})
	#print str(pagedata)
	text = str(pagedata)
	page_pattern = '<a href="(/wiki/[^"]+)" title="([^"]+)"'
	matches = re.findall(page_pattern, text)
	name = fixed_name.replace('_', ":", 1)
	name = name.replace('_', " ")

	next_page_data = page_soup.findAll("a", {"title":name})
	
	next_page = check_for_next_page(name, next_page_data)

	for hit in matches:

		if BASE_URL + hit[0] != 'https://en.wikipedia.org/wiki/Wikipedia:FAQ/Categorization#Why_might_a_category_list_not_be_up_to_date?':
			url_list.append(BASE_URL + hit[0])
			page_class_name = fix_name(BASE_URL + hit[0])
			page_class = wiki_page(page_class_name)
			page_class.add_supercategory(current_category)
			page_class.add_url(BASE_URL + hit[0])
			current_category.add_subpage(page_class_name, SUBPAGE_WEIGHT_FACTOR)
			page_list.append(page_class)
			Graph.add_edge(current_category.name, page_class_name)



	if next_page != "none":
		
		

		new = "https://en.wikipedia.org/w/index.php?title=" + name.split('/')[-1] + "&from="
		
		num = new + "0"

		urls = []

		uClient = uReq(num)
		page_html = uClient.read()
		uClient.geturl()
		uClient.close()

		page_soup = soup(page_html, "html.parser")
		pagedata = page_soup.findAll("div", {"id":"mw-pages"})
		text = str(pagedata)
		page_pattern = '<a href="(/wiki/[^"]+)" title="([^"]+)"'
		matches = re.findall(page_pattern, text)

		for page in pagedata:
			
			for hit in matches:
				if BASE_URL + hit[0] != 'https://en.wikipedia.org/wiki/Wikipedia:FAQ/Categorization#Why_might_a_category_list_not_be_up_to_date?':
					if BASE_URL + hit[0] not in url_list:
						url_list.append(BASE_URL + hit[0])
						page_class_name = fix_name(BASE_URL + hit[0])
						page_class = wiki_page(page_class_name)
						page_class.add_supercategory(current_category)
						page_class.add_url(BASE_URL + hit[0])
						current_category.add_subpage(page_class_name, SUBPAGE_WEIGHT_FACTOR)
						page_list.append(page_class)
						Graph.add_edge(current_category.name, page_class_name)


		for c in alpha:
			alphabet = new + c
			uClient = uReq(alphabet)
			page_html = uClient.read()
			uClient.geturl()
			uClient.close()

			page_soup = soup(page_html, "html.parser")
			pagedata = page_soup.findAll("div", {"id":"mw-pages"})
			text = str(pagedata)
			page_pattern = '<a href="(/wiki/[^"]+)" title="([^"]+)"'
			matches = re.findall(page_pattern, text)

			for page in pagedata:
				
				for hit in matches:
					if BASE_URL + hit[0] != 'https://en.wikipedia.org/wiki/Wikipedia:FAQ/Categorization#Why_might_a_category_list_not_be_up_to_date?':
						if BASE_URL + hit[0] not in url_list:
							url_list.append(BASE_URL + hit[0])
							page_class_name = fix_name(BASE_URL + hit[0])
							page_class = wiki_page(page_class_name)
							page_class.add_supercategory(current_category)
							page_class.add_url(BASE_URL + hit[0])
							current_category.add_subpage(page_class_name, SUBPAGE_WEIGHT_FACTOR)
							page_list.append(page_class)
							Graph.add_edge(current_category.name, page_class_name)

	
	return page_list




def get_supercategories(current_category, page_soup, BASE_URL, Graph):
	

	supercategory_data = page_soup.findAll("div", {"class":"mw-normal-catlinks"})
	text = str(supercategory_data)
	pattern = '<a href="(/wiki/[^"]+)" title="([^"]+)"' 
	matches = re.findall(pattern, text)

	for hit in matches:
		if BASE_URL + hit[0] != 'https://en.wikipedia.org/wiki/Help:Category':
			page_class_name = wiki_page(fix_name(BASE_URL + hit[0]))
			current_category.add_supercategory(page_class_name)
			Graph.add_edge(fix_name(BASE_URL + hit[0]), current_category.name)
