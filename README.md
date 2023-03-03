# Overview
Collaborative, interdisciplinary project to model the religious cultures in the Database of Religious History (DRH). We appreciate feedback and input. 

# Directory Structure
```
|- MPF/
	|- tests 
	|- data
	|- plots
	|- ...
|- preprocessing/
	|- preprocessing.py # convert .json to .csv
	|- curation.py # selection of questions, and wrangling format
	|- ...
|- analysis/ 
	|- parameters_figure.py # figure showing model params
	|- landscape_figure.py # landscape figure
	|- tables.py # generating tables
	|- ...
|- documents/
	|- todo_list.txt # to-do list
	|- questions.txt # overview of questions
	|- ...
|- data/
	|- raw/
	|- preprocessing/
	|- model/
	|- analysis/ 
	|- ...
```

# Components
## `/preprocessing`
Preprocessing of data from the Database of Religious History (DRH).

## `/MPF`
Optimized C coded to implement Minimum Probability Flow (MPF).

## `/analysis`
Analysis of the data and model (e.g. plots, tables, etc.)  

## `/data` 
Data processed at various stages (e.g. raw data, preprocessed, model fits, etc.)

## `/overview`
Folder for non-code documents (e.g. todo-lists, ...)

# Installation
1. Clonse the repo
``` git clone https://github.com/victor_m_p/religious_landscapes.git ```

2. Install Python/R/Julia environment (we will add this later)


# License
Distributed under the MIT Licence. See `LICENSE.txt` for more information.

# Contact
Please feel free to raise an issue in this repository or reach us through other channels:

Simon DeDeo: [@LaboratoryMinds](https://twitter.com/LaboratoryMinds) sdedeo@andrew.cmu.edu
Victor Poulsen: [@vic_moeller](https://twitter.com/vic_moeller) victormoeller@gmail.com
Edward Slingerland: [@slingerland20](https://twitter.com/slingerland20) edward.slingerland@gmail.com
Rachel Spicer: [@RachelASpicer](https://twitter.com/RachelASpicer) rachelaspicer@gmail.com
Willis Monroe [@willismonroe](https://twitter.com/willismonroe) willismonroe@gmail.com

# Acknowledgements
...
