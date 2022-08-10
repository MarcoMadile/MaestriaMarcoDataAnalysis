#Cargar paquetes de R
library(tidyverse)
library(sp)
library(rgdal) 
library(rgeos)
library(maptools)
library(raster)
library(lubridate)
library(leaflet)
library(colorRamps)

setwd("/home/karina/TORTUGAS/TrayecIGOTO2022")

#data format Date, time, Latitude, Longitude
###empty rows separates chunks of consecutive dates, I drop those NAs
machos<-read.table("T10b.csv",header=TRUE,sep=",") %>% drop_na()
hembras<-read.table("T30b.csv",header=TRUE,sep=",") %>% drop_na()

alldata<-rbind(machos,hembras)

#Convert spatial object "coordinates"
coordsH<-as.data.frame(cbind(hembras$Latitude,hembras$Longitude))
names(coordsH)<-c("lat","lon")
coordinates(coordsH)=~lon+lat

#Especify projection
proj4string(coordsH)=CRS("+proj=longlat +datum=WGS84")

datesH<-unique(hembras$Date)
datesM<-unique(machos$Date)

colorsH <- c(colorRampPalette(c("#fb92e2","#c90223"))(length(datesH)))
palhembras <- colorFactor(colorsH, domain = datesH)
colorsM <- c(colorRampPalette(c("#3496ff","darkblue"))(length(datesM)))
palmachos <- colorFactor(colorsM, domain = datesM)


map<-leaflet()%>% addTiles()%>% addMarkers(lng=-66,lat=-41)
leaflet(alldata)%>% addTiles()%>% 
 addCircleMarkers(lng=~hembras$Longitude,lat=~hembras$Latitude,radius=4,color = ~palhembras(hembras$Date) ,fillOpacity = 0.8,stroke=FALSE)%>%
 addCircleMarkers(lng=~machos$Longitude,lat=~machos$Latitude,radius=4,color = ~palmachos(machos$Date),fillOpacity = 0.8,stroke=FALSE)%>%
 addProviderTiles("Esri.WorldImagery")


library(mapview)
mapshot(map,"IGOTO2022.png")


