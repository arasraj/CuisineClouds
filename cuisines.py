#!/usr/bin/python

import urllib
import BeautifulSoup
from urllib2 import *

URL_BASE = 'http://www.foodnetwork.com'

def retrieve_cuisine():
  url = URL_BASE + '/topics/%s/index.html?No=%d'
  cuisines = ['mexican']

  alllinks = []
  for cuisine in cuisines:
    for i in range(0, 20, 20):
    #for i in range(0, 100, 20):
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

    ingredients = soup.findAll('li',attrs = {'class': 'ingredient'})
    total_ingredients = [ingredients.text.lower() 
                         for ingredients in ingredients]

links = retrieve_cuisine()
ingredients(links)



    

