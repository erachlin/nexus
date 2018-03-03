import networkx as nx
import pickle
from wiki_classes import *
from helper_functions import *
import pandas as pd
import matplotlib.pyplot as plt


category_data = []
category_data_pickle1 = open('Nervous_system_categories01.pickle', 'rb')
category_data = pickle.load(category_data_pickle1)

category_data_pickle2 = open('Nervous_system_categories02.pickle', 'rb')
category_data += pickle.load(category_data_pickle2)


page_data = []
page_data_pickle1 = open('Nervous_system_pages01.pickle', 'rb')
page_data = pickle.load(page_data_pickle1)

page_data_pickle2 = open('Nervous_system_pages02.pickle', 'rb')
page_data += pickle.load(page_data_pickle2)

starting_topic = "Category_Nervous_system"


def main():
	
	#uncomment code below to set main topics
	
	pages_with_main_topic_data = {}

	pages_with_main_topic_data = set_main_topics(page_data, category_data, starting_topic)

	main_topics_pickle = open(STARTING_TOPIC + "_pages_with_main_topics.pickle", "wb")
	pickle.dump(pages_with_main_topic_data, main_topics_pickle, pickle.HIGHEST_PROTOCOL)
	main_topics_pickle.close()

	print "successfully added main topics"
	

	#find_closest_categories()

def find_closest_categories():


	while raw_input("continue? (y/n) ") == ("y"):
			
		#page names
		page1_found = False
		page2_found = False
		
		#lists of categories found in search
		accessible1 = []
		accessible2 = []

		#supercategories to traverse for page 1
		page1_supercategory_cue = []

		#supercategories to traverse for page 2
		page2_supercategory_cue = []

		supercategories_traversed_page1 = []
		supercategories_traversed_page2 = []

		#closest categories found when checking both accessible lists
		closest_categories_found = False

		#page name entry
		page1_entry = raw_input("Enter page one name: ")
		page2_entry = raw_input("Enter page two name: ")

		
		#runs through page data to find first page
		for page1 in page_data:
			
			if page1.name == page1_entry:	

				accessible1.append(page1.supercategories[0].name)
				#print page1.supercategories[0].name + " is supercategory of "  + page1.name
				page1_supercategory_cue.append(page1.supercategories[0])
				page1_found = True
		
		
		for page2 in page_data:

			if page2.name == page2_entry:
				
				accessible2.append(page2.supercategories[0].name)
				#print page2.supercategories[0].name + " is supercategory of " + page2.name
				page2_supercategory_cue.append(page2.supercategories[0])
				page2_found = True

			
		if (page1_found and page2_found) == True:

			#checks if initial supercategories have overlap
			closest_categories_found = check_category_overlap(accessible1, accessible2)
			iteration = 0
			while closest_categories_found == False and (page1_supercategory_cue or page2_supercategory_cue):

				page1_new_supercategories = []
				page2_new_supercategories = []

				for supercat in page1_supercategory_cue:
					print supercat.name + " currently in supercategory cue 1"
			
				for supercat in page2_supercategory_cue:
					print supercat.name + " currently in supercategory cue 2"

					
				for supercategory1 in page1_supercategory_cue:

					if supercategory1.name not in supercategories_traversed_page1:
						
						add_subcategories(supercategory1, accessible1)

						page1_new_supercategories += add_supercategories(supercategory1.name, accessible1)
						supercategories_traversed_page1.append(supercategory1.name)

					else:
						page1_supercategory_cue.pop(0)

				for supercategory2 in page2_supercategory_cue:

					if supercategory2.name not in supercategories_traversed_page2:
						
						add_subcategories(supercategory2, accessible2)
						
						page2_new_supercategories += add_supercategories(supercategory2.name, accessible2)
						supercategories_traversed_page2.append(supercategory2.name)

					else:
						page2_supercategory_cue.pop(0)


				closest_categories_found = check_category_overlap(accessible1, accessible2)

				page1_supercategory_cue = page1_new_supercategories
				page2_supercategory_cue = page2_new_supercategories

				iteration += 1
				print "iteration " + str(iteration)
			
			print "finished"

		else:
			if page1_found == False and page2_found == True:
				print page1_entry + " is not a valid page, please try again"

			elif page1_found == True and page2_found == False:
				print page2_entry + " is not a valid page, please try again"

			else:
				print page1_entry + " and " + page2_entry + " are not valid pages, please try again"
			



def add_subcategories(supercategory, accessible):

	#check if supercategory has subcategories
	if isinstance(supercategory, category) and supercategory.subcategories:
		
		#adds subcategories this category to accessible list	    	
	    for subcat in supercategory.subcategories:
			#print subcat + " is subcategory of " + supercategory.name
			accessible.append(subcat)
	

def add_supercategories(new_category_name, accessible):

	new_supercategories = []

	for category in category_data:

		if category.name == new_category_name:
			for supercat in category.supercategories:
				
				accessible.append(supercat.name)
				new_supercategories.append(supercat)
			

	return new_supercategories


def check_category_overlap(accessible1, accessible2):

	closest_categories = []
	closest_categories_named = []

	for category_iterator1 in accessible1:
	    for category_iterator2 in accessible2:
			if category_iterator1 == category_iterator2:
				closest_categories.append(category_iterator1)

	if closest_categories:

		for category in closest_categories:

			if category not in closest_categories_named:

				print "closest category is " + category
				closest_categories_named.append(category)

		return True

	else:
		return False
				
		
def set_weighted_main_topic(starting_topic, tree_traversal_list):

	weighted_main_topic_name = ""

	if len(tree_traversal_list) == 0:
		weighted_main_topic_name == starting_topic

	#elif tree_traversal_list[-1] == starting_topic:
	#	weighted_main_topic_name = tree_traversal_list[-2].name

	else:
		weighted_main_topic_name = tree_traversal_list[-1].name

	return weighted_main_topic_name

def set_main_topics(page_data, category_data, starting_topic):

	print "setting main topics"
	count = 0
	pages_with_main_topics = {}

	for page in page_data:
		main_topic = ""
		page_name = page.name
		high_category = page.get_highest_weighted_supercategory()
		high_category_weight = high_category.get_weight()

		for page in page_data:

			if page.name == page_name and page.get_highest_weighted_supercategory().get_weight > high_category_weight:
				high_category = page.get_highest_weighted_supercategory()
				high_category_weight = high_category.get_weight()

		for category in category_data:

			if category.name == high_category.name:
				tree_traversal_list = []
				current_category = category
				tree_traversal_list.append(current_category)
				last_category = ""
				while (current_category.name != starting_topic) and (current_category != last_category):
					last_category = current_category
					current_category = current_category.get_highest_weighted_supercategory()
					tree_traversal_list.append(current_category)
					
					

				category.add_tree_traversal_list(tree_traversal_list)
				main_topic = set_weighted_main_topic(starting_topic, tree_traversal_list)
				

		pages_with_main_topics[page] = main_topic
		count += 1
		print str(count)
	print "finished setting main_topics"
	return pages_with_main_topics





if __name__ == '__main__':
	main()

