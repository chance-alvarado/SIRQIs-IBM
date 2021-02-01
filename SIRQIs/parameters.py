"""Specify simulation parameters for the SIRQIs individual based model.
This module constructs dictionaries of parameters used to change simulation
dynamics. Parameter explanations and expectations are below:
Results Parameters:
    - main_results_dir (str): Directory to store model results. Will be
        created if the specified location does not exist.
    - batch_dir (str): Directory relative to 'main_results_dir' for a batch
        simulations to be stored. Will attempt to be index equally named
        batch directories.
Simulation Parameters:
    - num_runs (int): Number of individual simulations using
        defined parameters.
    - num_days (int): Number of days to simulate for each run.
Population Parameters:
    - num_susceptible (int): Number of initial susceptible in simulation.
    - num_infected (int): Number of initial infected in simulation.
    - initial_infection_distribution (list of int/float): Zero-indexed
        discrete probability distribution of days since infection for initial
        infected. Elements of initial_infection_distribution should sum to 1.
Infection Parameters:
    - infectious_threshold (int/float): Minimum log 10 of viral load needed
        for an individual to be infectious.
    - probability_infection_given_contact: (float): Probability of an
        individual being infected given contact with an infectious individual.
    - probability_outside_infection (float): Probability of an individual
        being infected from outside the population.
    - daily_contacts_distributions (list of int/float): Zero-indexed discrete
        probability distribution of number of contacts and individual has
        per day. Elements of daily_contacts_distribution should sum to 1.
Testing Parameters:
    - proportion_tested_daily (float): Fraction of eligible individuals to be
        randomly selected for testing per day.
    - detectable_threshold (int/float): Minimum log 10 of viral load need for
        an individual to be detected positive.
    - days_till_results (list of float/int): Zero-indexed discrete probability
        distribution of days between testing and receiving results (i.e being
        eligible for retesting or being moved to isolation).
Isolation Parameters:
    - days_in_isolation (int): Number of days until an individual is released
        from isolation.
    - eligible_for_retesting (bool): Determines if individuals leaving
        isolation are eligible to be retested.
    - probability_using_isolation_resources (float): Probability of an
        individual occupying an isolation bed compared to individually
        isolating at a private residence.
Quarantine Parameters:
    - days_in_quarantine (int): Number of days until and individual is released
        from quarantine.
    - days_till_quarantine_distribution (list of int/float): Zero-indexed
        discrete probability distribution of days from an individual being
        isolated to a contact being quarantined.
    - probability_successful_contact (float): Probability of an individual
        being successfully reached for quarantine.
    - probability_using_isolation_resources (float): Probability of an
        individual occupying a quarantine bed compared to individually
        isolating at a private residence.
More information can be found in this project's README file.
Explore this repository at:
    https://github.com/chance-alvarado/SIRQIs-IBM/
Author:
    Chance Alvarado
        LinkedIn: https://www.linkedin.com/in/chance-alvarado/
        GitHub: https://github.com/chance-alvarado/
"""

# Results parameters
main_results_dir = 'results'
batch_dir = 'batch'

# Simulation parameters
num_runs = 100
num_days = 100

# Population parameters
num_susceptible = 950
num_infected = 50
initial_infection_distribution = [0, 1/7, 1/7, 1/7, 1/7, 1/7, 1/7, 1/7]

# Infection parameters
infectious_threshold = 6
probability_infection_given_contact = 0.1
probability_outside_infection = 0.001
daily_contacts_distribution = [0, 0.5, 0.5]

# Testing parameters
proportion_tested_daily = 1 / 14
detectable_threshold = 4
days_till_results_distribution = [0, 1]

# Isolation parameters
days_in_isolation = 8
eligible_for_retesting = False
probability_using_isolation_resources = 1 / 2

# Quarantine parameters
days_in_quarantine = 12
days_till_quarantine_distribution = [0, 0.5, 0.5]
probability_successful_contact = 0.75
probability_using_quarantine_resources = 1 / 2

# ----------------------------------------------------------------------------

# Construct parameter dict to be passed to ResultsWriter class
results_dict = {
    'main_results_dir': main_results_dir,
    'batch_dir': batch_dir
    }

# Construct parameter dict to be passed to GeneralPopulation class
general_population_dict = {
    'num_susceptible': num_susceptible,
    'num_infected': num_infected,
    'initial_infection_distribution': initial_infection_distribution,
    'infectious_threshold': infectious_threshold,
    'detectable_threshold': detectable_threshold,
    'daily_contacts_distribution': daily_contacts_distribution,
    'probability_outside_infection': probability_outside_infection,
    'probability_infection_given_contact': probability_infection_given_contact,
    'proportion_tested_daily': proportion_tested_daily,
    'days_till_results_distribution': days_till_results_distribution,
    'days_till_quarantine_distribution': days_till_quarantine_distribution,
    'probability_successful_contact': probability_successful_contact
    }

# Construct parameter dict to be passed to Quarantine class
quarantine_dict = {
    'days_in_quarantine': days_in_quarantine,
    'detectable_threshold': detectable_threshold,
    'days_till_results_distribution': days_till_results_distribution,
    'detectable_threshold': detectable_threshold,
    'probability_using_quarantine_resources':
        probability_using_quarantine_resources
    }

# Construct parameter dict to be passed to Isolation class
isolation_dict = {
    'days_in_isolation': days_in_isolation,
    'eligible_for_retesting': eligible_for_retesting,
    'probability_using_isolation_resources':
        probability_using_isolation_resources
    }
