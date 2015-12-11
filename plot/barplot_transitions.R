#plot 4 barplots related to skeptic/gullible communities and forgetting probability 0.1/0.8
#value of the barplot represents the rate of the transitions 
#susceptible>>believers and susceptible>>fact-checkers
#normalized by the number of susceptible users

library(reshape2)
library(ggplot2)

data_row <-read.csv("~/plot/data/table_trans.csv",sep=";", header=TRUE)
data=as.data.frame(data_row)

seg2=c(seq(0.5,0.9,0.1),0.99)
names(data)[2] <- paste("rate")
names(data)[3] <- paste("type")



mdata=melt(data,id.vars=c("type","segregation","forget","community"))

levels(mdata$type) <- c("Susceptible to Believer", "Susceptible to Fact-checker")


p <-ggplot(mdata, aes(segregation, value))+
  facet_grid(forget~community)+
  geom_bar( aes(fill=type),stat="identity",position="dodge")+
  scale_fill_grey()+
  labs(fill="", size=14)+
  theme_bw()+
  theme(panel.grid=element_blank(),
        strip.background=element_rect(colour="white",fill="white"),
        strip.text=element_text(size=14,face="bold"),
        axis.title=element_text(size=14),
        legend.text=element_text(size=12),
        axis.text=element_text(size=12))+
  scale_y_continuous(name="transitions")+
  scale_x_continuous(breaks=seg2)

print(p)
