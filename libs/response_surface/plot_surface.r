library(RColorBrewer)
library(raster)
library(colorspace)
source("D:/Doutorado/Future_projections_fire/response_surface/libs/cut_results.r")
source("D:/Doutorado/Future_projections_fire/response_surface/libs/find_levels.r")
source("D:/Doutorado/Future_projections_fire/response_surface/libs/legendColBar.r")
source("D:/Doutorado/Future_projections_fire/response_surface/libs/mtext.units.r")
source("D:/Doutorado/Future_projections_fire/response_surface/libs/time_series_from_nc.r")

############
## Set up ##
############
## file yout want to plot
#file = 'D:/Doutorado/Coding-python/outputs/pantanal/sem-frag-2020/figs/potential-response-maps/group_0-response_surface.csv'
#file = 'D:/Doutorado/Coding-python/outputs/pantanal/sem-frag-2020/figs/potential-response-maps/group_1-response_surface.csv'

#file = 'D:/Doutorado/Coding-python/outputs/pantanal/sem-frag-2020/figs/sensitivity-response-maps/group_0-response_surface.csv'
#file = 'D:/Doutorado/Coding-python/outputs/pantanal/sem-frag-2020/figs/sensitivity-response-maps/group_1-response_surface.csv'

#file = 'D:/Doutorado/Coding-python/outputs/pantanal/sem-frag-2020/figs/standard-response-maps/group_0-response_surface.csv'
#file = 'D:/Doutorado/Coding-python/outputs/pantanal/sem-frag-2020/figs/standard-response-maps/group_1-response_surface.csv'
file = "D:/Doutorado/Coding-python/outputs/pantanal/sem-frag-2020/figs/standard-response-zero/group_1-response_surface.csv"

## choose from https://r-graph-gallery.com/38-rcolorbrewers-palettes.html


#choose your color gradient

#potential
#palette_name = "RdBu"

#standard
palette_name = "Reds"

#sensitivity
#palette_name = "PuBuGn"

reverse_palette = FALSE ## set to true if you need to flip the colours
reverse_surface = FALSE ## set to true if the surface is outputted the wrong way round (i.e potential)

#######################################
## Open stuff and set coords/colours ##
#######################################
## Read in csv file to plot surface
dat = read.csv(file)
x = dat[,1]; y = dat[,2] ; z = as.matrix(dat[,c(3, 5)])

## changing precipitation and temperature units
#x = dat[,1] - 273.15; y = dat[,2] * 60 * 60 * 24 * 30 ; z = as.matrix(dat[,c(3, 5)])

#for potential response
#if (reverse_surface) z = -z[,2:1]


## preparing time series from nc files

time_series <- calculate_mean_climate(
        dir_tasmax = "D:/Doutorado/Sanduiche/research/maxent-variables/variables_masked_na/fixed_gfed_reference/2002-2021/grassland.nc",
        dir_precip = "D:/Doutorado/Sanduiche/research/maxent-variables/variables_masked_na/fixed_gfed_reference/2002-2021/wetland.nc",
        dir_shapefile = "D:/Doutorado/Malhas/biomas/Pantanal.shp",
        target_years = 2002:2020
)

#if your variable is monthly 
#months = c("08", "09", "10"),

#dir_tasmax = "D:/Doutorado/Sanduiche/research/maxent-variables/era5/tas_max.nc",
#dir_precip = "D:/Doutorado/Sanduiche/research/maxent-variables/era5/precip.nc",


ntime = dim(time_series)[1]

## work out colour of each point
levels = find_levels(z)

#if you need to constrain to above zero values (standard response)
levels = levels[levels > 0]

brewer_colors = brewer.pal(length(levels)+1, palette_name)
if (reverse_palette) brewer_colors = rev(brewer_colors)

##########
## plot ##
##########
#setwd("D:/Doutorado/Coding-python/outputs/pantanal/sem-frag-2020/figs/potential-response-maps/")
#setwd("D:/Doutorado/Coding-python/outputs/pantanal/sem-frag-2020/figs/sensitivity-response-maps/")
#setwd("D:/Doutorado/Coding-python/outputs/pantanal/sem-frag-2020/figs/standard-response-maps/")
setwd("D:/Doutorado/Coding-python/outputs/pantanal/sem-frag-2020/figs/standard-response-zero/")

png("response_surface_group1_abovezero.png", height =6, width = 5, units = 'in', res = 300)  
layout(cbind(1:2, 3), width = c(1, 0.2))  
par(mar = c(3, 3, 1, 1))


##without time series
for_Percentile <- function(z, name) {
        color_levels = cut_results(z, levels)
        cols = brewer_colors[color_levels]
        
        ## plot base plot
        plot(x, y, pch = 19, cex = 2, col = cols, xlab = '', ylab = '')
        grid()
        title(name)
        ## blend in points
        cols = paste0(cols, '44')
        for (cex in seq(2, 0.1, by = -0.1))
                points(x, y, col = cols, pch = 19, cex = cex)
}

### with time series

for_Percentile <- function(z, name) {
        color_levels = cut_results(z, levels)
        brewer_colors = brewer.pal(length(levels)+1, palette_name)
        if (reverse_palette) brewer_colors = rev(brewer_colors)
        cols = brewer_colors[color_levels]
        
        ## plot base plot
        plot(x, y, pch = 19, cex = 2, col = cols, xlab = '', ylab = '')
        grid()
        title(name)
        ## blend in points
        cols = paste0(cols, '44')
        for (cex in seq(2, 0.1, by = -0.1))
                points(x, y, col = cols, pch = 19, cex = cex)
        
        ## Add time series
        lines(time_series[,2], time_series[,3], lty = 2)
        text(time_series[1,2], time_series[1,3], time_series[1,1], adj = c(-0.1,-0.1))
        text(time_series[ntime,2], time_series[ntime,3], time_series[ntime,1], 
             adj = c(-0.1,-0.1))
        
        ## Add time series trend
        find_trend <- function(i)
                predict(lm(time_series[,i] ~ time_series[,1]))[c(1, ntime)]
        
        x_trend = find_trend(2)
        y_trend = find_trend(3)
        arrows(x_trend[1], y_trend[1], x_trend[2], y_trend[2], lwd = 3)
}
for_Percentile(z[,1], '10th percentile')
for_Percentile(z[,2], '90th percentile')

## add legend
par(mar = rep(0, 4))
legendColBar(col = brewer_colors, limits = levels, xx = c(0.0, 0.5), yy = c(0.1, 0.9),
             xtext_pos_scale = 0.55)
dev.off()




