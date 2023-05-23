# Extract region and time of entries

# Load libraries
library(tidyverse)
library(data.table)
library(sf)
library(testthat)

# Load data
data <- fread("../data/raw/drh.csv")
answers <- fread("../data/raw/answers.csv")
seshat_NGA <- fread("../data/raw/seshat_NGA.csv")

# Extract only entries with answers to questions of interest
data_filt <- data[`Entry ID` %in% answers$`Entry ID`]
data_filt <- unique(data_filt)

# Extract time variables
data_time <- data_filt[, list(`Entry name`, `Entry ID`, start_year, end_year)]
data_time <- unique(data_time)

# Split data into individual years
data_year <- data_time[
  , list(Year = start_year:end_year),'`Entry name`,`Entry ID`,start_year,end_year'][
  , list(`Entry ID`, `Entry name`, Year)]
data_year <- unique(data_year)

# Extract first 1/2 characters of year to find the century
data_century <- data_year %>%
  mutate(Date = as.character(Year)) %>%
  mutate(Date = str_sub(Date, 1, -3)) %>%
  mutate(Date = as.numeric(paste0(Date, "00"))) %>%
  select(`Entry name`, `Entry ID`, Date) %>%
  distinct() 

# Extract region variables
data_region <- data_filt[, list(`Entry name`, `Entry ID`, `Region name`, `Region ID`)]
data_region <- unique(data_region)

# Convert Seshat NGA regions to sf 
seshat_NGA <- st_as_sf(seshat_NGA, coords = c("Longitude", "Latitude"), crs = 4326)

# Extract entry IDs
region_ID_names <- list.files(path = "../data/raw/kml_files", pattern = "*.kml", full.names = F, recursive = T)
region_ID_names <- gsub(".kml", "", region_ID_names)
region_ID_names <- region_ID_names[region_ID_names %in% (unique(data_filt$`Region ID`))]
region_ID <- paste(region_ID_names, ".kml", sep="")
region_ID <- paste("../data/raw/kml_files/", region_ID, sep="")

# Create list of sf polygons from kml
poly_list <- list()
for (i in 1:length(region_ID)){
  poly_list[[i]] <- st_read(region_ID[i])
}

# Reduce to single data frame
region_df <- reduce(poly_list, rbind)

# Make valid
region_df <- st_make_valid(region_df)

# Rename for joining
region_df <- region_df %>%
  mutate(`Region name` = Name)

# Make valid
region_df <- st_make_valid(region_df)

# Split into valid and invalid polygons
valid_status <- st_is_valid(region_df)
valid_regions <- region_df[valid_status,]
invalid_regions <- region_df[!valid_status,]

# Find overlaps 
valid_overlaps <- st_intersection(seshat_NGA, valid_regions)

# For invalid regions use planar intersects 
sf_use_s2(FALSE)
invalid_overlaps <- st_intersection(seshat_NGA, invalid_regions)
sf_use_s2(TRUE)

# Recombine data and extract entries that overlap
seshat_overlaps <- bind_rows(valid_overlaps, invalid_overlaps) %>%
  as_tibble %>%
  select(NGA, World.Region, Region.name) %>%
  rename(`Region name` = Region.name) %>%
  left_join(data_region, by = join_by(`Region name`), relationship = "many-to-many") %>%
  distinct()

# Extract DRH regions that do not have overlaps with Seshat NGAs
no_overlaps <- data_region %>%
  anti_join(seshat_overlaps, by = join_by(`Entry name`, `Entry ID`, `Region name`, `Region ID`))

expect_equal(length(unique(data_region$`Region ID`)), length(unique(seshat_overlaps$`Region ID`)) + length(unique(no_overlaps$`Region ID`)))


