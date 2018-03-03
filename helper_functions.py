import urllib 
from urllib import urlopen as uReq
import re
import bs4
from bs4 import BeautifulSoup as soup
from wiki_classes import *
import pickle
import pandas as pd
import networkx as nx

STARTING_TOPIC = "Category:Israeli-Palestinian_conflict"

def make_files(page_data, weighted_tree, files_made):

	pages_weighted_supercategories = populate_weights(page_data, weighted_tree)
	closest_main_topic_data = {}
	page_names = []
	main_topics = []

	find_closest_main_topic(pages_weighted_supercategories, STARTING_TOPIC)
	for page in pages_weighted_supercategories:

		closest_main_topic_data[page] = page.get_weighted_main_topic()

	subcategories_pickle = open(fix_name(STARTING_TOPIC) + str(files_made) + ".pickle", 'wb')
	pickle.dump(pages_weighted_supercategories, subcategories_pickle, pickle.HIGHEST_PROTOCOL)
	
	subcategories_pickle.close()

	print "made pickle " + str(files_made)

	for page in closest_main_topic_data:

		if page.name not in page_names:
			page_names.append(page.name)
		
			main_topic_name = page.get_weighted_main_topic()

			main_topics.append(main_topic_name)

	pages = pd.DataFrame(data=page_names)
	mains = pd.DataFrame(data=main_topics)



	cat_info = pd.concat([pages,mains],axis=1,ignore_index=True)
	
	cat_info.columns = ['Page','Main Topic']
	
	name = fix_name(STARTING_TOPIC) + "_main_topic_data" + str(files_made) + ".csv"
	
	cat_info.to_csv(os.path.join(BASE_PATH,name))



	print "finished main topic csv " + str(files_made)

	if incomplete_categories:
		file = open("incomplete_categories" + str(files_made) + ".txt", "w")
		for category in incomplete_categories:
			file.write(category)
		file.close()




def find_closest_main_topic(page_data, starting_topic):
	for cat_page in page_data:
		category_edge_list = []

		
		next_category = cat_page.get_highest_weighted_supercategory()
		while next_category.supercategories and next_category.get_highest_weighted_supercategory().name != starting_topic:
			#print category.name  + "'s highest supercateogry: " + category.get_highest_weighted_supercategory().name
			category_edge_list.append(next_category)

			next_category = next_category.get_highest_weighted_supercategory()
			#next_category.add_weights()


		cat_page.add_tree_traversal_list(category_edge_list)

		cat_page.set_weighted_main_topic(starting_topic)




def fix_name(url):

	name = url.split('/')[-1].replace(':','_')

	apostrophe = "%27"

	hyphen = "%E2%80%93"
	if re.search(hyphen, name):
		name = name.split(hyphen)[0] + "-" + name.split(hyphen)[1]



	if re.search(apostrophe, name):
		name = name.split(apostrophe)[0] + "'" + name.split(apostrophe)[1]		



	return name

def fix_page_name(url):

	name = url.split('/')[-1]
	return name

def check_for_next_page(current_category_name, next_page_data):

	#print next_page_data
	
	next_url = "none"
	
	for page in next_page_data:
		
		text = page["href"]
		
		if re.search("pagefrom", text):
			next_url = "next_page"

	#print next_url
	
	return next_url

	



def scrape_links(page_html, urls):

	page_soup = soup(page_html, "html.parser")

	subcategory_data = page_soup.findAll("a", {"class":"CategoryTreeLabel"})
	
	for subcategory in subcategory_data:
		link = subcategory["href"].replace("%27", "'")
		link = subcategory["href"].replace("%E2%80%93")
		urls.append(BASE_URL + subcategory["href"])
		class_name = BASE_URL + link
		current_category.add_subcategory(class_name)
		


	pagedata = page_soup.findAll("div", {"id":"mw-pages"})
	text = str(pagedata)
	pattern = '<a href="(/wiki/[^"]+)" title="([^"]+)"'
	matches = re.findall(pattern, text)

	for hit in matches:
		if BASE_URL + hit[0] != 'https://en.wikipedia.org/wiki/Wikipedia:FAQ/Categorization#Why_might_a_category_list_not_be_up_to_date?':
			pages.append(BASE_URL + hit[0])
			


	supercategory_data = page_soup.findAll("div", {"class":"mw-normal-catlinks"})
	text = str(supercategory_data)
	pattern = '<a href="(/wiki/[^"]+)" title="([^"]+)"' 
	matches = re.findall(pattern, text)

	for hit in matches:
		if BASE_URL + hit[0] != 'https://en.wikipedia.org/wiki/Help:Category':
			page_class_name = wiki_page(fix_page_name(BASE_URL + hit[0]))
			current_category.add_supercategory(fixBASE_URL + hit[0])
		
	

	

	if current_category not in cat_data:
		cat_data.append(current_category)
	

	return cat_data


def populate_weights(page_data, weighted_tree):

	pages_high_supercategory = {}

	print "populating_weights"
	
	for page in page_data:

		for supercategory in page.supercategories:
			
			supercategory.populate_weight(SUBPAGE_WEIGHT_FACTOR)
	
			weighted_tree[supercategory] = supercategory.get_highest_weighted_supercategory()
				

			pages_high_supercategory[page] = page.get_highest_weighted_supercategory()
					

	return pages_high_supercategory

def set_main_topic(high_supercategory, starting_category_name, weighted_tree, original_page):

	if high_supercategory in weighted_tree:
		#print high_supercategory.name + " : " + weighted_tree[high_supercategory].name
		if high_supercategory.name != starting_category_name:
			if starting_category_name != high_supercategory.get_highest_weighted_supercategory().name:
				return set_main_topic(weighted_tree[high_supercategory], starting_category_name, weighted_tree, original_page)

	
		if starting_category_name == high_supercategory.get_highest_weighted_supercategory().name:
			if high_supercategory.supercategories:
				main_topic = high_supercategory
				#print "reached main topic " + main_topic.name
				original_page.add_closest_main_topic(main_topic)
				return original_page
			else:
				high_topic = high_supercategory
				#print "reached highest topic possible at " + high_topic.name
				original_page.add_closest_main_topic(high_topic)
				return original_page

		elif (high_supercategory.name == starting_category_name):
			#print "reached root topic"
			return original_page

	else:
		if high_supercategory.name == starting_category_name:
			#print "reached root topic"
			return original_page
		
		else:
			#print high_supercategory.name + " is not in weighted tree"
			return original_page



def add_subcategories(supercategory, accessible):

	#check if supercategory has subcategories
	if isinstance(supercategory, category) and supercategory.subcategories:
		
		#adds subcategories this category to accessible list	    	
	    for subcat in supercategory.subcategories:
			print subcat + " is subcategory of " + supercategory.name
			accessible.append(subcat)
	

def add_supercategories(category, accessible):

		#check if supercategory has subcategories
	if isinstance(category, category) and cateogry.supercategories:
		
		#adds subcategories this category to accessible list	    	
	    for supercategory in category.supercategories:
			print supercategory.name + " is subcategory of " + category.name
			accessible.append(supercategory.name)
			supercategories.append(supercategory)

	return supercategories


def check_category_overlap(accessible1, accessible2):

	closest_categories = []

	for category_iterator1 in accessible1:
	    for category_iterator2 in accessible2:
			if category_iterator1 == category_iterator2:
				closest_categories.append(category_iterator1)

	if closest_categories:

		for category in closest_categories_found:

			print "closest category is " + category

		return "true"


def traverse_category_tree(Graph):

	if raw_input("Begin category traverser? (y/n) ") == ("y"):


		while raw_input("continue? (y/n) ") == ("y"):
			

			
			#page name entry
			page1_entry = raw_input("Enter page one name: ")
			page2_entry = raw_input("Enter page two name: ")
				
			if (page1_entry and page2_entry) in Graph and nx.has_path(Graph, page1_entry, page2_entry): 

				print nx.shortest_path(Graph, source=page1_entry, target=page2_entry)
			'''

			#lists of categories found in search
			accessible1 = []
			accessible2 = []

			
			#page names
			page1_main_topic = ""
			page2_main_topic = ""


			#supercategories to traverse for page 1
			page1_supercategory_cue = []

			#supercategories to traverse for page 2
			page2_supercategory_cue = []

			supercategories_traversed_page1 = []
			supercategories_traversed_page2 = []

			#closest categories found when checking both accessible lists
			closest_categories_found = "false"

			#page name entry
			page1_entry = raw_input("Enter page one name: ")
			page2_entry = raw_input("Enter page two name: ")


			#max_supercat1 = category("dummy1")
			#max_supercat1_weight = 0
			
			#runs through page data to find first page
			for page1 in page_data:
				
				if page1.name == page1_entry:
					

					accessible1.append(page1.supercategories[0].name)
					page1_supercategory_cue.append(page1.supercategories[0])
					#print page1.supercategories[0].name + " is supercategory of " + page1.name

					#supercat1_weight = page1.get_highest_weighted_supercategory().get_weight()
					

					#if supercat1_weight > max_supercat1_weight:
					#	max_supercat1_weight = supercat1_weight
					#	max_supercat1 = page1.supercategories[0]

			#max_supercat2 = category("dummy2")		
			#max_supercat2_weight = 0
			
			for page2 in page_data:

				if page2.name == page2_entry:
					
					accessible2.append(page2.supercategories[0].name)
					page2_supercategory_cue.append(page2.supercategories[0])
					#print page2.supercategories[0].name + " is supercategory of " + page2.name

					#supercat2_weight = page2.get_highest_weighted_supercategory().get_weight()
					

					#if supercat2_weight > max_supercat2_weight:
					#	max_supercat2_weight = supercat2_weight
					#	max_supercat2 = page2.supercategories[0]

			
			#iterator1 = max_supercat1
			#iterator2 = max_supercat2

			#checks if initial supercategories have overlap
			closest_categories_found = check_category_overlap(accessible1, accessible2)

			while closest_categories_found != "true" and (page1_supercategory_cue or page2_supercategory_cue):

				page1_new_supercategories = []
				page2_new_supercategories = []

					
				for supercategory in page1_supercategory_cue:

					if supercategory.name not in supercategories_traversed_page1:
						add_subcategories(supercategory, accessible1)
						for grandparent in supercategory.supercategories:
							page1_new_supercategories += add_supercategories(grandparent, accessible1)
							supercategories_traversed_page1.append(supercategory.name)

				for supercategory2 in page2_supercategory_cue:

					if supercategory2.name not in supercategories_traversed_page2:
						
						add_subcategories(supercategory2, accessible2)
						
						for grandparent in supercategory2.supercategories:
							page2_new_supercategories += add_supercategories(grandparent, accessible2)
							supercategories_traversed_page2.append(supercategory2.name)


				closest_categories_found = check_category_overlap(accessible1, accessible2)

				page1_supercategory_cue = page1_new_supercategories
				page2_supercategory_cue = page2_new_supercategories

			for supercat in page1_supercategory_cue:
				print supercat.name + "currently in supercategory cue 1"
			
			for supercat in page2_supercategory_cue:
				print supercat.name + "currently in supercategory cue 1"

			print "finished"
			'''

	else:

		print "goodbye"