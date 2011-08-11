setwd('~/foodnetwork/')
library(RSQLite)
library(DBI)
library(wordcloud)
library(RColorBrewer)

dir.create(file.path('/home/kip/foodnetwork', 'png'), showWarnings = FALSE)

con <- dbConnect(SQLite(), "db")
sql <- "select distinct cuisine_type from frequency"
types.rs <- dbGetQuery(con, sql)
#types.rs[,1]

# creates word clouds for each cuisine type and stores them as a png
for(cuisine_type in types.rs[,1]) {
  sql <- sprintf("select ingredient, freq from frequency where cuisine_type = '%s' and freq > 10", cuisine_type)
  rs <- dbGetQuery(con, sql)
  d <- data.frame(word=rs[1], freq=rs[2])
  palette <- brewer.pal(8, "PuBuGn")
  filename = sprintf("png/%s_wordcloud.png", cuisine_type)
  png(filename, width=1080,height=800)
  wordcloud(d$ingredient,d$freq, scale=c(8,.5),min.freq=1,max.words=150,random.order=FALSE,random.color=FALSE,rot.per=.15, colors=palette)
  dev.off()
}
