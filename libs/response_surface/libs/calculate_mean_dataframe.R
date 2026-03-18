library(raster)


calculate_mean_climate <- function(dir_tasmax, dir_precip, dir_shapefile, target_years, months = NULL) {
        # Read the rasterbrick files for temperature and precipitation
        raster_tasmax <- brick(dir_tasmax)
        raster_precip <- brick(dir_precip)
        
        # Define the region to crop (specify extent)
        extent <- shapefile(dir_shapefile)
        
        # Crop the raster data to the defined extent
        raster_tasmax <- crop(raster_tasmax, extent)
        raster_tasmax <- mask(raster_tasmax, extent)
        
        raster_precip <- crop(raster_precip, extent)
        raster_precip <- mask(raster_precip, extent)
        
        if (is.null(months)) {
                # Create an empty data frame to store the results
                mean_df <- data.frame(year = numeric(length(target_years)), tasmax = numeric(length(target_years)), precip = numeric(length(target_years)))
                
                for (i in seq_along(target_years)) {
                        year <- target_years[i]
                        
                        # Subset the raster data for the current year
                        year_data_tasmax <- raster_tasmax[[grep(paste(year, collapse = "|"), names(raster_tasmax))]]
                        year_data_precip <- raster_precip[[grep(paste(year, collapse = "|"), names(raster_precip))]]
                        
                        #year_data_tasmax <- year_data_tasmax - 273.15  # Convert to Celsius
                        #year_data_precip <- year_data_precip * 60 * 60 * 24 * 30  # Convert mm/sec to mm/month
                        
                        # Calculate the mean of values for all pixels for the selected months (tasmax)
                        year_mean_tasmax <- mean(year_data_tasmax[], na.rm = TRUE)
                        
                        # Calculate the mean of values for all pixels for the selected months (precip)
                        year_mean_precip <- mean(year_data_precip[], na.rm = TRUE)
                        
                        # Store the year and mean values in the data frame
                        mean_df[i, "year"] <- year
                        mean_df[i, "tasmax"] <- year_mean_tasmax
                        mean_df[i, "precip"] <- year_mean_precip
                }
        } else {
                # Ensure months is a character vector
                if (length(months) == 1) {
                        months <- as.character(months)
                }
                
                # Subset the raster data for the months of interest
                raster_subset_tasmax <- raster_tasmax[[unlist(lapply(months, function(m) grep(paste0("\\.", m, "\\."), names(raster_tasmax))))]]
                raster_subset_precip <- raster_precip[[unlist(lapply(months, function(m) grep(paste0("\\.", m, "\\."), names(raster_precip))))]]
                
                # Create an empty data frame to store the results
                mean_df <- data.frame(year = numeric(length(target_years)), tasmax = numeric(length(target_years)), precip = numeric(length(target_years)))
                
                for (i in seq_along(target_years)) {
                        year <- target_years[i]
                        
                        # Subset the raster data for the current year and months
                        year_data_tasmax <- raster_subset_tasmax[[grep(paste(year, collapse = "|"), names(raster_subset_tasmax))]]
                        year_data_precip <- raster_subset_precip[[grep(paste(year, collapse = "|"), names(raster_subset_precip))]]
                        
                        #year_data_tasmax <- year_data_tasmax - 273.15  # Convert to Celsius
                        #year_data_precip <- year_data_precip * 60 * 60 * 24 * 30  # Convert mm/sec to mm/month
                        
                        # Calculate the mean of values for all pixels for the selected months (tasmax)
                        year_mean_tasmax <- mean(year_data_tasmax[], na.rm = TRUE)
                        
                        # Calculate the mean of values for all pixels for the selected months (precip)
                        year_mean_precip <- mean(year_data_precip[], na.rm = TRUE)
                        
                        # Store the year and mean values in the data frame
                        mean_df[i, "year"] <- year
                        mean_df[i, "tasmax"] <- year_mean_tasmax
                        mean_df[i, "precip"] <- year_mean_precip
                }
        }
        
        return(mean_df)
}
