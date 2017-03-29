library(reshape2)
library(ggplot2)
library(plotly)

setwd("~/Desktop/fit/fitting_data")
files=list.files("~/Desktop/fit/fitting_data")

# Function that returns Root Mean Squared Error
rmse <- function(error)
{
  sqrt(mean(error^2))
}


seg_b_rmse <- vector()
seg_f_rmse <- vector()
noseg_b_rmse <- vector()
noseg_f_rmse <- vector()

seg_b_nrmse1 <- vector()
seg_f_nrmse1 <- vector()
noseg_b_nrmse1 <- vector()
noseg_f_nrmse1 <- vector()

seg_b_nrmse2 <- vector()
seg_f_nrmse2 <- vector()
noseg_b_nrmse2 <- vector()
noseg_f_nrmse2 <- vector()

hoax <- vector()

i=1
for(j in seq(1,length(files),2)){
 #if(j!=31 && j!=55 && j!=21 && j!=27){
  #seg
  seg <- read.table(files[j], header = TRUE, sep=",")
  seg_for =seg$For_empirico
  seg_against=seg$Against_empirico
  seg_ba = seg$For_BA
  seg_fa = seg$Against_FA
  
  seg_error_b = abs(seg_for-seg_ba)
  seg_error_f = abs(seg_against-seg_fa)
  
  name=strsplit(files[j],"*_with_segregation.csv")
  #name1=strsplit(name[[1]],"hoaxy_*")
  hoax[i]= name[[1]][1]
  print(hoax[i])
  seg_b_rmse[i]=rmse(seg_error_b)
  seg_f_rmse[i]=rmse(seg_error_f)

  
  print(paste0("rmse FOR:",rmse(seg_error_b)))
  print(paste0("den_1 FOR (max-min):", (max(seg_for)-min(seg_for))))
  print(paste0("den_2 FOR (mean):", mean(seg_for)))
  seg_b_nrmse1[i]=rmse(seg_error_b)/(max(seg_for)-min(seg_for))
  seg_b_nrmse2[i]=rmse(seg_error_b)/(mean(seg_for))
  
  if(mean(seg_against)!=0){
    print(paste0("rmse AGAINST:",rmse(seg_error_f)))
    print(paste0("den_1 AGAINST (max-min):", (max(seg_against)-min(seg_against))))
    print(paste0("den_2 AGAINST (mean):", mean(seg_against)))
    seg_f_nrmse1[i]=rmse(seg_error_f)/(max(seg_against)-min(seg_against))
    seg_f_nrmse2[i]=rmse(seg_error_f)/(mean(seg_against))
  }else{
    print("media 0!")
    print(paste0("rmse AGAINST:",rmse(seg_error_f)))
    seg_f_nrmse1[i]=rmse(seg_error_f)
    seg_f_nrmse2[i]=rmse(seg_error_f)
  }
  
  #noseg
  noseg <- read.table(files[j+1], header = TRUE, sep=",")
  noseg_for =noseg$For_empirico
  noseg_against=noseg$Against_empirico
  noseg_ba = noseg$For_BA
  noseg_fa = noseg$Against_FA
  
  noseg_error_b = abs(noseg_for-noseg_ba)
  noseg_error_f = abs(noseg_against-noseg_fa)

  noseg_b_rmse[i]=rmse(noseg_error_b)
  noseg_f_rmse[i]=rmse(noseg_error_f)
  
  noseg_b_nrmse1[i]=rmse(noseg_error_b)/(max(noseg_for)-min(noseg_for))
  noseg_b_nrmse2[i]=rmse(noseg_error_b)/(mean(noseg_for))
  if(mean(noseg_against)!=0){
    print(paste0("rmse AGAINST:",rmse(noseg_error_f)))
    print(paste0("den_1 AGAINST (max-min):",(max(noseg_against)-min(noseg_against))))
    print(paste0("den_2 AGAINST (mean):",mean(noseg_against)))
    noseg_f_nrmse1[i]=rmse(noseg_error_f)/(max(noseg_against)-min(noseg_against))
    noseg_f_nrmse2[i]=rmse(noseg_error_f)/(mean(noseg_against))
  }else{
    noseg_f_nrmse1[i]=rmse(noseg_error_f)
    noseg_f_nrmse2[i]=rmse(noseg_error_f)
  }
  i <-i+1
  #}
}

#rmse
ave_seg_b_rmse <- mean(seg_b_rmse)
ave_seg_f_rmse <- mean(seg_f_rmse)
ave_noseg_b_rmse  <- mean(noseg_b_rmse)
ave_noseg_f_rmse <- mean(noseg_f_rmse)

#nrmse1
ave_seg_b_nrmse1 <- mean(seg_b_nrmse1)
ave_seg_f_nrmse1 <- mean(seg_f_nrmse1)
ave_noseg_b_nrmse1  <-mean(noseg_b_nrmse1)
ave_noseg_f_nrmse1<- mean(noseg_f_nrmse1)

#nrmse2
ave_seg_b_nrmse2 <- mean(seg_b_nrmse2)
ave_seg_f_nrmse2 <- mean(seg_f_nrmse2)
ave_noseg_b_nrmse2  <- mean(noseg_b_nrmse2)
ave_noseg_f_nrmse2 <- mean(noseg_f_nrmse2)

print("====RMSE====")
print(paste0("noseg_AB:",ave_noseg_b_rmse))
print(paste0("noseg_AF:",ave_noseg_f_rmse))
print(paste0("seg_AB:",ave_seg_b_rmse))
print(paste0("seg_AF:",ave_seg_f_rmse))

print("====NRMSE1(range)====")
print(paste0("noseg_AB:",ave_noseg_b_nrmse1))
print(paste0("noseg_AF:",ave_noseg_f_nrmse1))
print(paste0("seg_AB:",ave_seg_b_nrmse1))
print(paste0("seg_AF:",ave_seg_f_nrmse1))

print("====NRMSE2(mean)====")
print(paste0("noseg_AB:",ave_noseg_b_nrmse2))
print(paste0("noseg_AF:",ave_noseg_f_nrmse2))
print(paste0("seg_AB:",ave_seg_b_nrmse2))
print(paste0("seg_AF:",ave_seg_f_nrmse2))

ave_df1 <- data.frame(ave_noseg_b_nrmse1, ave_noseg_f_nrmse1, ave_seg_b_nrmse1, ave_seg_f_nrmse1)
colnames(ave_df1) <-c("noseg_b","noseg_f","seg_b","seg_f")
m_ave1 <- melt(ave_df1)
ap1 <- ggplot(data=m_ave1, aes(x=variable, y=value, fill=variable))+
  geom_bar(stat="identity",position=position_dodge())+
  scale_fill_brewer(palette="Spectral")+
  ylim(c(0,0.4))+
  xlab("model compartment")+
  #scale_x_discrete(labels=c("","","",""))+
  theme(axis.text.x =element_text(size=12))+
  ggtitle("NRMSE1 (range)")
ap1 <- ggplotly(ap1)
show(ap1)

ave_df2 <- data.frame(ave_noseg_b_nrmse2, ave_noseg_f_nrmse2, ave_seg_b_nrmse2, ave_seg_f_nrmse2)
colnames(ave_df2) <-c("noseg_b","noseg_f","seg_b","seg_f")
m_ave2 <- melt(ave_df2)
ap2 <- ggplot(data=m_ave2, aes(x=variable, y=value, fill=variable))+
  geom_bar(stat="identity",position=position_dodge())+
  scale_fill_brewer(palette="Spectral")+
  xlab("model compartment")+
  ylim(c(0,0.4))+
  #scale_x_discrete(labels=c("","","",""))+
  theme(axis.text.x =element_text(size=12))+
  ggtitle("NRMSE2 (mean)")

ap2 <- ggplotly(ap2)
show(ap2)

plot_df1 <- data.frame(hoax,
                       noseg_b_nrmse1, noseg_f_nrmse1,
                       seg_b_nrmse1, seg_f_nrmse1)
colnames(plot_df1) <-c("hoax","noseg_b","noseg_f", "seg_b","seg_f")
m1 <- melt(plot_df1)

p1 <- ggplot(data=m1, aes(x=hoax, y=value, fill=variable))+
  geom_bar(stat="identity", position=position_dodge())+
  theme(axis.text.x =element_text(size=8, angle=90))+
  scale_fill_brewer(palette="Spectral")+
  scale_x_discrete(labels=c(1:31))+
  ggtitle("NRMSE1 (range)")

p1 <- ggplotly(p1)
show(p1)

plot_df2 <- data.frame(hoax,
                       noseg_b_nrmse2, noseg_f_nrmse2,
                       seg_b_nrmse2, seg_f_nrmse2)                      
colnames(plot_df2) <-c("hoax","noseg_b","noseg_f", "seg_b","seg_f")
m2 <- melt(plot_df2)

p2 <- ggplot(data=m2, aes(x=hoax, y=value, fill=variable))+
  geom_bar(stat="identity", position=position_dodge())+
  theme(axis.text.x =element_text(size=8, angle=90))+
  scale_fill_brewer(palette="Spectral")+
  scale_x_discrete(labels=c(1:31))+
  ggtitle("NRMSE2 (mean)")

p2 <- ggplotly(p2)
show(p2)



