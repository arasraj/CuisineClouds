# CuisineCloud

This project provides a means to determine which ingredients are the most characteristic of a certain cuisine. The method used to accomplish this was extracting term frequencines of serveral hundred recipes and visualizing them in a word cloud. All recipes are scraped from FoodNetwork.com, so take the accuracy of these word clouds for what they're worth. It uses the "wordcloud" R package to visualize the ingredients.

## How to use:

1. Run:

   > ./cuisines.py
   
   This will scrape foodnetwork, perform the data analysis, and create/insert into SQLite db. 

   Run in R:

   > source('visualize.r')

   This will run the R script and generate the word clouds as png's
   in the png subdirectory.

 <img src="https://github.com/arasraj/CuisineClouds/blob/master/png/indian_wordcloud.png" alt="Indian Word Cloud" align="center" />
