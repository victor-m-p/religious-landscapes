# Run preprocessing

# Check if packages are installed and if they are not installed, install them
packages <- c("tidyverse", "data.table", "sf", "testthat", "rnaturalearth", "rnaturalearthdata")
cran_packages <- setdiff(packages, rownames(installed.packages()))
if( length(cran_packages) ) {
  if( length(grep("devtools", cran_packages))) {
    install.packages("devtools")
  }
  require(devtools)
  if( length(grep("tidyverse", cran_packages))) {
    install_version("tidyverse", version = "2.0.0", repos = "http://cran.us.r-project.org")
  }
  if( length(grep("data.table", cran_packages))) {
    install_version("data.table", version = "1.14.8", repos = "http://cran.us.r-project.org")
  }
  if( length(grep("sf", cran_packages))) {
    install_version("sf", version = "1.0-12", repos = "http://cran.us.r-project.org")
  }
  if( length(grep("testthat", cran_packages))) {
    install_version("testthat", version = "3.1.7", repos = "http://cran.us.r-project.org")
  }
  if( length(grep("rnaturalearth", cran_packages))) {
    install_version("rnaturalearth", version = "0.3.2", repos = "http://cran.us.r-project.org")
  }
  if( length(grep("rnaturalearthdata", cran_packages))) {
    install_version("rnaturalearthdata", version = "0.1.0", repos = "http://cran.us.r-project.org")
  }
}

# Load packages
library(tidyverse)
library(data.table)
library(sf)
library(testthat)
library(rnaturalearth)
library(rnaturalearthdata)

# Extract answers
source("extract_answers.R")
rm(list = ls())

# Extract metadata
source("extract_metadata.R")
rm(list = ls())


