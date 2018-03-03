from wiki_classes import *
import networkx as nx
import bs4
import re
import urllib 
from urllib import urlopen as uReq
from bs4 import BeautifulSoup as soup
import pickle
import os	
from helper_functions import *
import matplotlib.pyplot as plt


BASE_URL = 'https://en.wikipedia.org'
MY_URL = 'https://en.wikipedia.org/wiki/Category:Main_topic_classifications'
STARTING_TOPIC = "Main_topics"
SUBPAGE_WEIGHT_FACTOR = 0.25
BASE_PATH = 'C:\Users\eli17\Documents\Eli\Personal\Nexus'


def page_crawler(urls, visited, category_data, page_data, incomplete_categories):
	
	count = 0
	files_made = 1
	G = nx.DiGraph()
	


	while len(urls) > 0 and count < 25000:
		
		if count % 1000 == 0 and count != 0:
			
			pages_pickle = open(STARTING_TOPIC + "_pages0" + str(files_made) + ".pickle", "wb")
			pickle.dump(page_data, pages_pickle, pickle.HIGHEST_PROTOCOL)
			pages_pickle.close()


			category_pickle = open(STARTING_TOPIC + "_categories0" + str(files_made) + ".pickle", "wb")
			pickle.dump(category_data, category_pickle, pickle.HIGHEST_PROTOCOL)
			category_pickle.close()

			files_made += 1

			



		if urls[0] not in visited:
			
			print urls[0]
			page_list = []
			uClient = uReq(urls[0])
			page_html = uClient.read()
			uClient.close()
			
			fixed_name = fix_name(urls[0])
			current_category = category(fixed_name)
			page_soup = soup(page_html, "html.parser")
			get_subcategories(current_category, page_soup, urls, BASE_URL, fixed_name, incomplete_categories, G)
			get_supercategories(current_category, page_soup, BASE_URL, G)
			page_list = get_pages(current_category, page_soup, page_list, fixed_name, BASE_URL, SUBPAGE_WEIGHT_FACTOR, G)
			category_data.append(current_category)
			page_data += page_list
			visited.append(urls[0])
			urls.pop(0)
			count += 1
			print "count is " + str(count) + ", cue is " + str(len(urls))
			print current_category.name + "[pages] : " + str(len(page_list))
			
			#print "current_weight is " + str(len(current_category.subcategories))

		else:
			urls.pop(0)



	return G








def main():
	urls = [MY_URL]
	visited = []
	incomplete_categories = []
	category_data = []
	page_data = []

	
	

	print "beginning to crawl from " + STARTING_TOPIC
	category_tree = page_crawler(urls, visited, category_data, page_data, incomplete_categories)
	
	
	print "beginning to make files"

	pages_pickle = open(STARTING_TOPIC + "_pages_complete.pickle", "wb")
	pickle.dump(page_data, pages_pickle, pickle.HIGHEST_PROTOCOL)
	pages_pickle.close()


	category_pickle = open(STARTING_TOPIC + "_categories_complete.pickle", "wb")
	pickle.dump(category_data, category_pickle, pickle.HIGHEST_PROTOCOL)
	category_pickle.close()

	print "writing gml file"
	nx.write_gml(category_tree, STARTING_TOPIC + ".gml")
	


	print "finished all files"




	




if __name__ == '__main__':
	main()






