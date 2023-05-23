# Extract region and time of entries

# Load libraries
library(tidyverse)
library(data.table)
library(sf)

# Load data
data <- fread("../data/raw/drh.csv")
answers <- fread("../data/raw/answers.csv")

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
