# Overview
Collaborative, interdisciplinary project to model the religious cultures in the Database of Religious History (DRH). We appreciate feedback and input. 

# 2026 Claude/Codex Analysis

In November 2026 the MPF code and methods used for this project were re-examined by Claude (Anthropic), with an independent review by Codex (OpenAI). The full account is [CLAUDE_IMPROVEMENTS_SUMMARY.md](https://github.com/victor-m-p/cultural-landscapes/blob/main/CLAUDE_IMPROVEMENTS_SUMMARY.md) in the [cultural-landscapes](https://github.com/victor-m-p/cultural-landscapes) repository, which also holds the revised program (`MPF_CMU/src`: self-contained C sources, Makefile and tests, with no external libraries). This repository contains no MPF code (the `MPF/` folder described below is not here), only parameter files fitted with a 2023 version of it. Two findings bear on those files (`data/mdl_output`):

* **The fits with 38 questions should not be used.** The 2023 code mishandles models with more than 31 nodes (states were built with 32-bit shifts, so the wrong configurations were used). The fits with 20 questions are not affected by this.
* **The treatment of missing answers was biased.** These data have up to 10 missing answers per row, and the 2023 objective for rows with missing answers ("Partial-MPF") does not converge on the right parameters even with unlimited data. The revised program has two corrected versions. For the 455-row data of the paper the correction made little practical difference; it has not been checked for the data here.

The fits here also used an L1 penalty (`PNORM1`), which the revised program does not have, so they cannot be repeated with it exactly.

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
1. Clone the repo
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
