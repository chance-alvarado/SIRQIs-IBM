# SIRQIs Individual-based Model of Disease

### An model for the spread of COVID-19 in a closed, fully-mixed population where surveillance testing, quarantine, and isolation are the primary sources of mitigation. 

##### Written by Chance Alvarado: [LinkedIn](https://www.linkedin.com/in/chance-alvarado/), [GitHub](https://github.com/chance-alvarado)

##### Explore the full repository [here](https://github.com/chance-alvarado/SIRQIs-IBM).
![Case Map](/resources/media/header.jpg)

Image courtesy of [Unsplash](https://unsplash.com/photos/gf6UDwpl0ac).

--- 

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)

### Table of Contents
- [How SIRQIs Works](#introduction)
- [Installation/ Requirements](#setup)
- [Selecting Parameters](#parameters)
- [Running Simulations](#run)
- [Understanding the Results](#results)

---

### How SIRQIs Works <a name="introduction"></a>




---

### Installation/ Requirements <a name="setup"></a>

SIRQIs is an individual-based model of disease developed completely in [Python](https://www.python.org/). Since disease and interaction dynamics are enacted at the individual-level across large batches of simulations **ensure you have proper computational resources and time**. SIRQIs will also automatically produce many results files when run. **Be sure to have ample storage on your device to store simulation results**. Download or clone this repository [here](https://github.com/chance-alvarado/SIRQIs-IBM).

The contents of this repository were written and have been tested with [Python 3.7.4](https://www.python.org/). SIRQIs makes used of the follwoing standard libraries:

Library | 
--------|
[csv](https://docs.python.org/3/library/csv.html) | 
[glob](https://docs.python.org/3/library/glob.html) | 
[os](https://docs.python.org/3/library/os.html) |
[shutil](https://docs.python.org/3/library/shutil.html) |
[sys](https://docs.python.org/3/library/sys.html) | 
[importlib](https://docs.python.org/3/library/importlib.html) |

Additional modules needed for proper function are listed below:

Requirement | Version |
------------|---------|
[Matplotlib](https://matplotlib.org/) | 3.1.3
[NumPy](https://numpy.org/) | 1.18.1 | 
[Pandas](https://pandas.pydata.org/) | 1.0.1
[SciPy](https://www.scipy.org/) | 1.4.1

---

### Selecting Parameters <a name="parameters"></a>

The population, infection, and testing dynamics can be modified to represent a plethora of different examples by editing the `SIRQIs/parameters.py` file with any text editor or IDE. A description of each parameter follows:

#### Results Parameters
| Parameter | Type | Example | Description |
|-----------|------|---------|-------------|
|main_results_dir|str|'results'|Directory to store model results. Will be created if the specified location does not exist.
|batch_dir|str|'batch'|Directory relative to `main_results_dir` for a batch simulations to be stored. Will attempt to be index equally named batch directories.

#### Simulation Parameters
| Parameter | Type | Example | Description |
|-----------|------|---------|-------------|
|num_runs|int|100|Number of individual simulations using defined parameters.
|num_days|int|100|Number of days to simulate for each run.

#### Population Parameters
| Parameter | Type | Example | Description |
|-----------|------|---------|-------------|
|num_susceptible|int|950|Number of initial susceptible in simulation.
|num_infected|int|50|Number of initial infected in simulation.
|initial_infection_distribution|list of int/float|[0, 0, 1]|Zero-indexed discrete probability distribution of days since infection for initial infected. Elements of initial_infection_distribution should sum to 1.

#### Infection Parameters
| Parameter | Type | Example | Description |
|-----------|------|---------|-------------|
|infectious_threshold|int/float|6|Minimum log 10 of viral load needed for an individual to be infectious.
|probability_infection_given_contact|float|0.5|probability of an individual being infected given contact with an infectious individual.
|probability_outside_infection|float|0.001|Probability of an individual being infected from outside the population.
|daily_contacts_distributions|list of int/float|[0, 0.5, 0.5]|Zero-indexed discrete probability distribution of number of contacts and individual has per day. Elemenets of daily_contacts_distribution should sum to 1.

#### Testing Parameters
| Parameter | Type | Example | Description |
|-----------|------|---------|-------------|
|proportion_tested_daily|float|1/14|Fraction of eligible individuals to be randomly selected for testing per day.
|detectable_threshold|int/float|4| Minimum log 10 of viral load need for an individual to be detected positivie.
|days_till_results|list of float/int|[0, 1]|Zero-indexed discrete probability distribution of days between testing and receiving results (i.e being eligible for retesting or being moved to isolation).


#### Isolation Parameers
| Parameter | Type | Example | Description |
|-----------|------|---------|-------------|
|days_in_isolation|int|8|Number of days until an individual is released from isolation.
|eligible_for_retesting|bool|False| Determines if individuals leaving isolation are eligible to be retested.
|probability_using_isolation_resources|float|1/2|Probability of an individual occupying an isolation bed compared to individually isolating at a private residence.


#### Quarantine Parameters
| Parameter | Type | Example | Description |
|-----------|------|---------|-------------|
|days_in_quarantine|int|12|Number of days until and individual is released from quarantine.
|days_till_quarantine_distribution|list of int/float|[0, 0.5, 0.5]|Zero-index discrete probabiliy distribution of days from an individual being isolated to a contact being quarantined.
|probability_successful_contact|float|0.75|Probability of an individual being succesfully reached for quarantine.
|probability_using_quarantine_resources|float|1/2|Probability of an individual occupying a quarantine bed compared to individually isolating at a private residence.

Once parameters are tuned to your scenario save `parameters.py` in its original location. **Do not delete or rename `parameters.py`.**

---

### Running a Simulation <a name="run"></a>

Once parameters have been specified in the `SIRQIs/parameters.py` file, simulations can be run by doing the following:

<p align="center">
  <img src="/resources/media/terminal.gif"><br>
  <b>Running SIRQIs in terminal</b><br>
</p>

1. Open a terminal window at the `SIRQIs` folder.
2. Run the `main_run.py` file by executing `python main_run.py` in the terminal.
3. If your terminal is detected, a status bar will display simulation progress.

---

### Understanding the Results <a name="results"></a>

---

### License
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)

---

