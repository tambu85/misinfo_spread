#plot 6 scatterplots seg vs size 
#density represents the number of believers at equilibrium
#considering all nodes, gullible and skeptic
#and 2 values of forgetting probability (0.1 - 0.8)

library(aqfig)
library(ggplot2)
library(reshape2)
library(grid)
library(gridExtra)
library(gtable)

setwd("~/plot/data")
temp01gul = read.csv("survivors_segsize_forg01_gul.csv", sep=",", row.names=1)
temp01sk = read.csv("survivors_segsize_forg01_sk.csv", sep=",", row.names=1)
temp01tot = read.csv("survivors_segsize_forg01_tot.csv", sep=",", row.names=1)

temp08gul = read.csv("survivors_segsize_forg08_gul.csv", sep=",", row.names=1)
temp08sk = read.csv("survivors_segsize_forg08_sk.csv", sep=",", row.names=1)
temp08tot = read.csv("survivors_segsize_forg08_tot.csv", sep=",", row.names=1)

seg2=c(seq(0.5,0.9,0.1),0.99)
seg=seq(0.5,1,0.1)
size=seq(100,900,100)

names(temp01gul)[1:9] <- size
rownames(temp01gul)[1:6] <- seg
s01gul<- as.matrix(temp01gul) 
m01g=melt(s01gul)

names(temp01sk)[1:9] <- size
rownames(temp01sk)[1:6] <- seg
s01sk<- as.matrix(temp01sk) 
m01s=melt(s01sk)

names(temp01tot)[1:9] <- size
rownames(temp01tot)[1:6] <- seg
s01tot<- as.matrix(temp01tot) 
m01t=melt(s01tot)

names(temp08gul)[1:9] <- size
rownames(temp08gul)[1:6] <- seg
s08gul<- as.matrix(temp08gul) 
m08g=melt(s08gul)

names(temp08sk)[1:9] <- size
rownames(temp08sk)[1:6] <- seg
s08sk<- as.matrix(temp08sk) 
m08s=melt(s08sk)

names(temp08tot)[1:9] <- size
rownames(temp08tot)[1:6] <- seg
s08tot<- as.matrix(temp08tot) 
m08t=melt(s08tot)

maxz=max(max(s01gul),max(s01sk),max(s01tot),max(s08gul),max(s08sk),max(s08tot))
minz=min(min(s01gul),min(s01sk),min(s01tot),min(s08gul),min(s08sk),min(s08tot))


p01_gul <- ggplot(data=m01g,aes(x=Var1,y=Var2,fill=value))+
  geom_tile()+
  scale_fill_gradient(name= "Number of\n Believers",low='darkseagreen1', high='darkgreen',lim=c(minz, maxz))+
  ggtitle("(e)")+
  theme_bw()+
  theme(axis.line = element_line(colour = "black"),
        panel.border=element_blank(),
        panel.grid=element_blank(),
        plot.title=element_text(size=14),
        legend.position="none", 
        axis.title=element_blank(),
        axis.text=element_text(size=10))+
  scale_x_continuous(name= "segregation", breaks=seg2, expand = c(0, 0))+
  scale_y_continuous(name="size", breaks=size,  expand = c(0, 0)) 

p01_sk <- ggplot(data=m01s,aes(x=Var1,y=Var2,fill=value))+
  geom_tile()+
  scale_fill_gradient(name= "Number of\n Believers",low='darkseagreen1', high='darkgreen',lim=c(minz, maxz))+
  ggtitle("(c)")+
  theme_bw()+
  theme(axis.line = element_line(colour = "black"),
        panel.border=element_blank(),
        panel.grid=element_blank(),
        plot.title=element_text(size=14),
        legend.position="none",
        axis.title=element_blank(),
        axis.text.x=element_blank(),
        axis.text.y=element_text(size=10))+
  scale_x_continuous(name= "segregation", breaks=seg2, expand = c(0, 0))+
  scale_y_continuous(name="size", breaks=size,  expand = c(0, 0))

p01_tot <- ggplot(data=m01t,aes(x=Var1,y=Var2,fill=value))+
  geom_tile()+
  scale_fill_gradient(name= "Number of\n Believers",low='darkseagreen1', high='darkgreen',lim=c(minz, maxz))+
  ggtitle("(a)")+
  theme_bw()+
  theme(axis.line = element_line(colour = "black"),
        panel.border=element_blank(),
        panel.grid=element_blank(),
        plot.title=element_text(size=14),
        legend.position="none",
        axis.title=element_blank(),
        axis.text.x=element_blank(),
        axis.text.y=element_text(size=10))+
  scale_x_continuous(name= "segregation", breaks=seg2, expand = c(0, 0))+
  scale_y_continuous(name="size", breaks=size,  expand = c(0, 0))

p08_gul <- ggplot(data=m08g,aes(x=Var1,y=Var2,fill=value))+
  geom_tile()+
  scale_fill_gradient(name= "Number of\n Believers",low='darkseagreen1', high='darkgreen',lim=c(minz, maxz))+
  ggtitle("(f)")+
  theme_bw()+
  theme(axis.line = element_line(colour = "black"),
        panel.border=element_blank(),
        panel.grid=element_blank(),
        plot.title=element_text(size=14),
        legend.position="none", 
        axis.title=element_blank(),
        axis.text.y=element_blank(),
        axis.text.x=element_text(size=10))+
  scale_x_continuous(name= "segregation", breaks=seg2, expand = c(0, 0))+
  scale_y_continuous(name="size", breaks=size,  expand = c(0, 0)) 

p08_sk <- ggplot(data=m08s,aes(x=Var1,y=Var2,fill=value))+
  geom_tile()+
  scale_fill_gradient(name= "Number of\n Believers",low='darkseagreen1', high='darkgreen',lim=c(minz, maxz))+
  ggtitle("(d)")+
  theme_bw()+
  theme(axis.line = element_line(colour = "black"),
        panel.border=element_blank(),
        panel.grid=element_blank(),
        plot.title=element_text(size=14),
        legend.position="right",
        legend.title=element_text(size=12, face="bold"),
        axis.title=element_blank(),
        axis.text=element_blank())+
  scale_x_continuous(name= "segregation", breaks=seg2, expand = c(0, 0))+
  scale_y_continuous(name="size", breaks=size,  expand = c(0, 0))

p08_tot <- ggplot(data=m08t,aes(x=Var1,y=Var2,fill=value))+
  geom_tile()+
  scale_fill_gradient(name= "Number of\n Believers",low='darkseagreen1', high='darkgreen',lim=c(minz, maxz))+
  ggtitle("(b)")+
  theme_bw()+
  theme(axis.line = element_line(colour = "black"),
        panel.border=element_blank(),
        panel.grid=element_blank(),
        plot.title=element_text(size=14),
        legend.position="none", 
        axis.title=element_blank(),
        axis.text=element_blank())+
  scale_x_continuous(name= "segregation", breaks=seg2, expand = c(0, 0))+
  scale_y_continuous(name="size", breaks=size,  expand = c(0, 0))


legend = gtable_filter(ggplot_gtable(ggplot_build(p08_sk)),"guide-box")


#grid.arrange(arrangeGrob(p01_tot,p08_tot,
#                         p01_sk,p08_sk+theme(legend.position="none"),
#                         p01_gul, p08_gul,
#                         nrow=3,
#                         ncol=2,
#                         left=textGrob("size of gullible group", rot=90, vjust=1)),
#             legend,
#             widths=unit.c(unit(1,"npc") - legend$width, legend$width),
#             nrow=1)

grid.layout(nrow=3,ncol=2,heights=c(1,1,1), widths=c(1,1),default.units=c('null','null'))

plot <- arrangeGrob(p01_tot,p08_tot,
                    p01_sk,p08_sk+theme(legend.position="none"),
                    p01_gul, p08_gul,
                    widths=c(1,9/10),
                    nrow=3)

theight=unit(28,"points")
plot <- arrangeGrob(plot, 
                    textGrob("segregation", gp=gpar(fontsize=14)),
                    heights=unit.c(unit(1,"npc")-theight, theight))
plot <- arrangeGrob(plot,
                    left=textGrob("size of gullible group",gp=gpar(fontsize=14), rot=90, vjust=0.5),                    
                    legend,
                    widths=unit.c(unit(1,"npc") - legend$width, legend$width),
                    nrow=1)


print(plot)

