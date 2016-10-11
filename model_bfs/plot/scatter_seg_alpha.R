#plot 2 scatterplots alpha vs segregation for different values of forget (0.1-0.8)

library(aqfig)
library(ggplot2)
library(reshape2)
library(grid)

setwd("~/plot/data")
temp01 = read.csv("survivors_alpha_seg_forg01.csv", sep=",", row.names=1)
temp08 = read.csv("survivors_alpha_seg_forg08.csv", sep=",", row.names=1)

seg=seq(0.5,0.99,0.01)
alpha=seq(0.75,0.99,0.01)

names(temp01)[1:25] <- alpha
rownames(temp01)[1:50] <- seg
s01<- as.matrix(temp01) 
m01=melt(s01)

names(temp08)[1:25] <- alpha
rownames(temp08)[1:50] <- seg
s08<- as.matrix(temp08) 
m08=melt(s08)

maxz=max(max(s01),max(s08))
minz=min(min(s01),min(s08))

#add column 
#m01$value08 <- m08$value

#to remove grey zone add following line in theme(...)
# panel.background=element_blank(),axis.line=element_line(colour="black")

p1 <- ggplot(data=m01,aes(x=Var1,y=Var2,fill=value))+
  geom_tile()+
  scale_fill_gradient(low='darkseagreen1', high='darkgreen',lim=c(minz, maxz))+
  ggtitle("(a)")+
  theme_bw()+
  theme(axis.line = element_line(colour = "black"),
        panel.border=element_blank(),
        panel.grid.major=element_blank(), 
        panel.grid.minor=element_blank(),
        plot.title=element_text(size=14),
        legend.position="none", 
        text= element_text(size=12))+
  scale_x_continuous(name= "segregation", expand = c(0, 0))+
  scale_y_continuous(name="credibility",  expand = c(0, 0))
p2 <- ggplot(data=m08,aes(x=Var1,y=Var2,fill=value))+
  geom_tile()+
  scale_fill_gradient(name= "Number of\n Believers",
                      low='darkseagreen1', high='darkgreen',lim=c(minz, maxz))+
  ggtitle("(b)")+
  theme_bw()+
  theme(axis.line = element_line(colour = "black"),
        panel.border=element_blank(),
        panel.grid.major=element_blank(), 
        panel.grid.minor=element_blank(),
        plot.title=element_text(size=14),
        legend.title=element_text(size=12, face="bold"),
        axis.title.y=element_blank(),
        axis.text.y=element_blank(),
        axis.ticks.y=element_blank(),
        text= element_text(size=12))+
  labs(y=NULL)+
  scale_x_continuous(name= "segregation", expand = c(0, 0))+
  scale_y_continuous( expand = c(0, 0))


layt<- grid.layout(nrow=1,ncol=2,heights=1, widths=c(4/5,1),default.units=c('null','null'))
grid.show.layout(layt)
grid.newpage()
pushViewport(viewport(layout=layt))

#tiff(filename="prova.tiff", width=5.25, units='in', res=300)
#bitmap(filename="Prova.tiff", width = 5.25, units='in', type="tifflzw", res=300)
#postscript(filename="Prova.eps", width = 5.25, units='in', res=300)
#library(cairoDevice)
#Cairo(file="something.png", type="png", units="in", width=5.25, height=7, pointsize=12, dpi=300)
print(p1, vp=viewport(layout.pos.row=1,layout.pos.col=1))
print(p2, vp=viewport(layout.pos.row=1,layout.pos.col=2))
#dev.off()

