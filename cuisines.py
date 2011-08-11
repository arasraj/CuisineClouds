#!/usr/bin/python

import stemmer
import sqlite3
import operator
import BeautifulSoup
from urllib2 import *
import cPickle as pickle
from collections import defaultdict
from HTMLParser import HTMLParseError

URL_BASE = 'http://www.foodnetwork.com'

def retrieve_cuisine():
  """ Grabs links to 100 recipes of the cuisine types provided """

  url = URL_BASE + '/topics/%s/index.html?No=%d'

  # this can be changed to include any cuisines which are valid
  # in the context of foodnetwork.com
  cuisines = ['mexican', 'indian', 'british', 'cajun', 
              'caribbean', 'chinese', 'french', 'greek', 'italian', 'southern', 
              'southwestern', 'spanish', 'thai', 'german', 'cuban', 
              'jewish', 'northeastern']

  # cuisine_type -> list of links to 100 recipes
  cuisine_dict = {}
  for cuisine in cuisines:
    alllinks = []
    for i in range(0, 100, 20):
      try:
        curl = url % (cuisine, i)
        conn = urlopen(curl)
        data = conn.read()
        conn.close()
        soup = BeautifulSoup.BeautifulSoup(data)
      except URLError as e:
        print 'Error retrieving %s; %s' % (curl, str(e))
        continue
      except HTMLParseError:
        continue

      # grap all links which point to the recipe
      anchors = soup.findAll('a',attrs = {'class': 'cta'})
      links = [anchor['href'] for anchor in anchors 
              if anchor.text == 'Get Recipe']
      alllinks.extend(links)
    cuisine_dict[cuisine] = alllinks

  #f = open('cuisine_dict.pkl', 'wb')
  #pickle.dump(cuisine_dict, f)
  #f.close()

  #for x,y in cuisine_dict.iteritems():
  #	print x,y
  return cuisine_dict

def ingredients(cuisine_links):
  """ Extracts all ingredients for each cuisine types 100 recipes """

  url = URL_BASE + '%s'

  dbconn, cursor = db_instance('db')
  createdb(cursor)

  i=1 # used as progress counter
  for cuisine, links in cuisine_links.iteritems():
    print i 
    total_ingredients = []
    for link in links:
      try:
        curl = url % link
        conn = urlopen(curl)
        data = conn.read()
        conn.close()
        soup = BeautifulSoup.BeautifulSoup(data)
      except URLError as e:
        print 'Error retrieving %s -> %s' % (curl, str(e))
        continue
      except HTMLParseError:
        continue

      # Hack to handle a formating issue with BeautifulSoup.
      # Replaces all anchor tags with the text they display
      links = soup.findAll('a',attrs = {'class': 'crosslink'})
      for link in links:
        atext = link.text
        link.replaceWith(atext)

      # extracts all ingredients
      ingredients = soup.findAll('li', attrs = {'class': 'ingredient'})
      total_ingredients.extend([strip_tags(str(ingred))
                                for ingred in ingredients])

    freq_analysis(dbconn, cursor, cuisine, total_ingredients)
    i += 1

  dbconn.commit()
  dbconn.close()

def strip_tags(s):
  """ Utility function to remove special case HTML elements """
  return s.lower().replace('<li class="ingredient">','').replace('</li>','').replace('\r','')

def remove_punc(s):
  """ Utility function to remove punctuation """
  return s.replace(',', '').replace('(', '').replace(')','').replace('.','').replace("'","").replace(':','').strip()

def freq_analysis(conn, cursor, cuisine, ingredients_list):
  """Performs analysis on a cuisine's list of 100 recipes.
     Finds term frequencies. Each ingredient is stemmed and
     checked against a stopwords list. Term frequencies are
     store in a SQLite db with their associated cuisine type.
  """

  stopwords = [word[:-1] for word in open('stopwords.txt', 'r')]
  pstemmer = stemmer.PorterStemmer()

  freq = defaultdict(lambda : 1)
  # used to map word stems to whole words
  mapping = defaultdict(list)

  for ingredients in ingredients_list:
    for ingredient in ingredients.split():
      ingredient = remove_punc(ingredient)
      if ingredient not in stopwords:
        ingredient_stem = pstemmer.stem(ingredient, 0, len(ingredient)-1)
        freq[ingredient_stem] += 1
        mapping[ingredient_stem].append(ingredient)

  #for x,y in sorted(freq.iteritems(), key=lambda x: x[1], reverse=True):
  for ingred, freq in sorted(freq.iteritems(), key=operator.itemgetter(1), reverse=True):
    nonstemmed_ingred = mapping[ingred]
    # if multiple words map to the same stem, take the shortest one in length
    dbingred = min(nonstemmed_ingred, key=lambda candidate: len(candidate))
    insert_ingred(cursor, cuisine, dbingred, freq)


def db_instance(path):
  """ Create DB """
  conn = sqlite3.connect(path)
  return (conn, conn.cursor())

def createdb(c):
  c.execute("""drop table if exists frequency""")
  c.execute("""create table frequency (cuisine_type text, ingredient text, freq real)""")

def insert_ingred(c, cuisine, ing, freq):
  c.execute("""insert into frequency values ('%s', '%s', '%s')""" % (cuisine, ing, freq))
  

if __name__ == '__main__':
  links = retrieve_cuisine()
  ingredients(links)



    

