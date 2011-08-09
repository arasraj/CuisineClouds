#!/usr/bin/python

import urllib
import BeautifulSoup
import operator
import stemmer
import sys
from urllib2 import *
import cPickle as pickle
from collections import defaultdict

URL_BASE = 'http://www.foodnetwork.com'

def retrieve_cuisine():
  url = URL_BASE + '/topics/%s/index.html?No=%d'
  cuisines = ['indian']

  alllinks = []
  for cuisine in cuisines:
    #for i in range(0, 20, 20):
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

      anchors = soup.findAll('a',attrs = {'class': 'cta'})
      links = [anchor['href'] for anchor in anchors 
              if anchor.text == 'Get Recipe']
      alllinks.extend(links)
  print alllinks
  print len(alllinks)
  return alllinks

def ingredients(links):
  # make this a constant; base
  url = URL_BASE + '%s'
  total_ingredients = []

  f2 = open('tmp2.txt', 'w')
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

    links = soup.findAll('a',attrs = {'class': 'crosslink'})
    #links = soup.findAll('a')
    for link in links:
    	atext = link.text
    	link.replaceWith(atext)


    ingredients = soup.findAll('li',attrs = {'class': 'ingredient'})
    total_ingredients.extend([str(ingred).lower().replace('<li class="ingredient">','').replace('</li>','').replace('\r','')
                              for ingred in ingredients])

    print total_ingredients
  # store in sqlite
  #print total_ingredients
  f2.close()
  f = open('ingredients_indian.pkl', 'wb')
  pickle.dump(total_ingredients, f)
  f.close()

def load():
  f = open('ingredients_indian.pkl', 'rb')
  ingredients_list = pickle.load(f)
  f.close()
  stopwords = [word[:-1] for word in open('stopwords.txt', 'r')]
  pstemmer = stemmer.PorterStemmer()

  freq = defaultdict(lambda : 1)
  mapping = {}
  for ingredients in ingredients_list:
    for ingredient in ingredients.split():
      ingredient = ingredient.replace(',', '').replace('(', '').replace(')','').replace('.','').replace("'","").strip()
      if ingredient not in stopwords:
        ingredient_stem = pstemmer.stem(ingredient, 0, len(ingredient)-1)
        #freq[ingredient] += 1
        freq[ingredient_stem] += 1
        #mapping[ingredient_stem] = ingredient

  #for x,y in sorted(freq.iteritems(), key=lambda x: x[1], reverse=True):
  for x,y in sorted(freq.iteritems(), key=operator.itemgetter(1), reverse=True):
    print x,y

links = retrieve_cuisine()
ingredients(links)
#load()



    

