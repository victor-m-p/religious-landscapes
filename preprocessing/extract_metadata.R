# Extract region and time of entries

# Load functions
source("functions.R")

# Load data
data <- fread("../data/raw/drh.csv")
answers <- fread("../data/raw/answers.csv")
seshat_NGA <- fread("../data/raw/seshat_NGA.csv")
world_regions <- read_csv("../data/raw/world_regions.csv")

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
data_region <- data_region[, `Region name` := ifelse(`Region ID` == "1848", 'Cult Sites of "Maritime Hera"', `Region name`)]

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
  mutate(`Region name` = Name) %>%
  mutate(`Region name` = ifelse(grepl("Maritime Hera",`Region name`), 'Cult Sites of "Maritime Hera"', `Region name`))

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
  distinct() %>%
  select(`Entry name`, `Entry ID`, NGA, World.Region)

# Find DRH regions that do not have overlaps with Seshat NGAs
no_overlaps <- data_region %>%
  anti_join(seshat_overlaps, by = join_by(`Entry name`, `Entry ID`))

# Extract DRH regions that do not have overlaps with Seshat NGAs
valid_regions_no_NGA <- valid_regions %>% 
  filter(`Region name` %in% no_overlaps$`Region name`)
invalid_regions_no_NGA <- invalid_regions %>% 
  filter(`Region name` %in% no_overlaps$`Region name`)

# Extract country data
countries <- extract_countries() %>%
  mutate(id = row_number())

# Join country polygons with which world region each country belongs to
countries_regions <- right_join(countries, world_regions, by = join_by(iso_a3)) %>%
  filter(!is.na(name))

# Make valid
countries_regions <- st_make_valid(countries_regions)

# Find overlaps with world regions
world_regions_valid <- st_intersects(valid_regions_no_NGA, countries_regions)

# Set region names
names(world_regions_valid) <- valid_regions_no_NGA$`Region name`

expect_equal(nrow(valid_regions_no_NGA), length(world_regions_valid))

# Extract regions with overlapping world regions
world_regions_overlaps <- world_regions_valid[lengths(world_regions_valid) > 0L]

# Extract regions without overlapping world regions
world_regions_no_overlaps <- world_regions_valid[lengths(world_regions_valid) == 0L]

# Convert to list of strings
world_regions_overlaps_str <- lapply(world_regions_overlaps, function(x) toString(x))

# Convert to tibble and split each sampled location into rows
world_regions_overlaps_tib <- enframe(world_regions_overlaps_str, name = "Region name", value = "id") %>%
  mutate(id = as.character(id)) %>%
  mutate(id = strsplit(id, ","))
world_regions_overlaps_dt <- as.data.table(world_regions_overlaps_tib)
world_regions_overlaps_dt <- world_regions_overlaps_dt[, list(id = as.character(unlist(id))), by = setdiff(names(world_regions_overlaps_dt), "id")][
  , id := as.numeric(id)]

# Join regions with overlaps with corresponding world regions
world_regions_overlaps <- world_regions_overlaps_dt %>%
  left_join(data_region, by = join_by(`Region name`), relationship = "many-to-many") %>%
  left_join(countries_regions, by = join_by(id), relationship = "many-to-many") %>%
  select(`Entry name`, `Entry ID`, `Region name`, `Region ID`, World.Region) %>%
  distinct()

# Manually add world regions for countries missing overlaps
invalid_no_world_regions <- data_region %>%
  filter(`Region name` %in% invalid_regions_no_NGA$`Region name`)
world_regions_no_overlaps <- data_region %>%
  filter(`Region name` %in% names(world_regions_no_overlaps)) %>%
  bind_rows(invalid_no_world_regions) %>%
  mutate(World.Region = case_when(
    `Region name` == "Kapingamarangi" ~ "Oceania-Australia",
    `Region name` == "Tikopia" ~ "Oceania-Australia",
    `Region name` == "Tikopia Island" ~ "Oceania-Australia",
    `Region name` == "Wogeo Island" ~ "Oceania-Australia",
    `Region name` == "Northern Somalia" ~ "Africa",
    `Region name` == "Island of Tikopia" ~ "Oceania-Australia",
    `Region name` == "Romonum Island" ~ "Oceania-Australia",
    `Region name` == "Dobu Island" ~ "Oceania-Australia",
    `Region name` == "San Blas Archipelago ca. 1927" ~ "North America",
    `Region name` == "Putuo Mountain" ~ "East Asia",
    `Region name` == "Southeast Sulawesi" ~ "Southeast Asia",
    TRUE ~ ""))

# Combine all world region data for entries
data_world_regions <- bind_rows(world_regions_overlaps, world_regions_no_overlaps)

# Create empty list
NGA_list <- list()

# Find the closest NGA for each DRH region without overlaps
for(i in 1:length(unique(data_world_regions$`Region ID`))) {
  
  # Extract region
  region <- unique(data_world_regions$`Region ID`)[i]
  
  # Extract world regions covered
  regions_covered <- data_world_regions %>% filter(`Region ID` %in% region)
  
  # Filter Seshat NGAs by world regions DRH region covers
  world_regions_NGA <- seshat_NGA %>%
    filter(World.Region %in% regions_covered$World.Region)
  
  # Find the closest NGA for each DRH region without overlaps
  if(unique(regions_covered$`Region name`) %in% valid_regions_no_NGA$`Region name`) {
    drh_region <- valid_regions_no_NGA %>% filter(`Region name` %in% regions_covered$`Region name`)
    closest_NGA <- st_nearest_feature(drh_region, world_regions_NGA)
  } else {
    sf_use_s2(FALSE)
    drh_region <- invalid_regions_no_NGA %>% filter(`Region name` %in% regions_covered$`Region name`)
    closest_NGA <- st_nearest_feature(drh_region, world_regions_NGA)
    sf_use_s2(TRUE)
  }
  
  # Extract closest Seshat NGA for each region
  region_NGA <- world_regions_NGA[closest_NGA,] %>%
    select(NGA, World.Region)
  
  # Save to list 
  NGA_list[[i]] <- region_NGA
}

# Reduce to single data frame
NGA_df <- reduce(NGA_list, rbind)

# Extract DRH regions missing Seshat NGA
region_no_NGA <- data_world_regions %>%
  select(`Region name`, `Region ID`) %>% 
  distinct() %>%
  filter(`Region name` %in% c(valid_regions_no_NGA$`Region name`, invalid_regions_no_NGA$`Region name`)) %>%
  ungroup()

# Extract Seshat NGAs closest to each DRH entry
data_NGA <- bind_cols(region_no_NGA, NGA_df) %>%
  left_join(data_region, by = join_by(`Region name`, `Region ID`)) %>%
  select(`Entry name`, `Entry ID`, NGA, World.Region) %>%
  distinct() %>%
  bind_rows(seshat_overlaps) %>%
  rename(`World Region` = World.Region)
  
# Combine region and time metadata for export
metadata <- data_century %>%
  left_join(data_NGA, by = join_by(`Entry name`, `Entry ID`), relationship = "many-to-many") %>%
  select(-`Entry name`)

# Save entry metadata
write_csv(metadata, "../data/raw/metadata.csv")
