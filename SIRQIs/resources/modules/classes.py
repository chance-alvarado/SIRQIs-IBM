"""Specify classes defining within and between individual dynamics.

The following classes and function define the dynamics of infection within and
between individuals in a simulated population. Time steps are progressed and
infection dynamics are simulated through the simulate_time_step function
acting on a GeneralPopulation, Quarantine, and Isolation object. Additional
class and function information is below:

Individual:
    - Individual objects symbolize a unique person within a population.
    Individuals have flags and timers that are updated from interactions
    specified as methods within the GeneralPopulation, Quarantine, and
    Isolation classes.

GeneralPopulation:
    - The GeneralPopulation object holds a set of unique individuals and
    is responsible for infecting, testing, and tracing contacts for individuals
    based on specified parameters. Individuals are removed from general
    population due to quarantine or isolation before an inevitable return.

Quarantine:
    - The Quarantine object is responsible for holding individuals removed
    from the general population due to contact tracing. Individuals may
    or may not be infected which could result in possible transfer to
    isolation. Individuals will either transfer to isolation or return
    to the general population after a duration based on specified parameters.

Isolation:
    - The Isolation object holds individuals removed from the general
    population due to a positive test result - either through surveillance
    testing or during a quarantine stay. Individuals are returned to the
    general population after a duration based on specified parameters

simulate_time_step:
    - Dynamics specified with classes are progressed one time step (day) per
    iteration of this function. Logs of individuals within specific states
    are updated after all interaction and dynamics are simulated for the
    current time step.

More information can be found in this project's README file.

Explore this repository at:
    https://github.com/chance-alvarado/SIRQIs-IBM/

Author:
    Chance Alvarado
        LinkedIn: https://www.linkedin.com/in/chance-alvarado/
        GitHub: https://github.com/chance-alvarado/

"""
# Imports
import numpy as np


# Define necessary classes
class Individual():
    """Define class for individual-level dynamics."""

    def __init__(self, flag_set):
        """Initialize necessary attributes."""
        # Define infection timer
        self.infection_timer = 0

        # Generate predetermined viral load curve
        self.viral_load_curve = self.generate_viral_load_curve()

        # Store current viral load
        self.viral_load = 0

        # Define binary state flags
        self.susceptible = False
        self.infected = False
        self.detectable = False
        self.infectious = False
        self.recovered = False

        # Deine testing timer and flags
        self.testable = True
        self.awaiting_results = False
        self.days_till_results = 0

        # Define isolation timer and flag
        self.to_be_isolated = False
        self.using_isolation_resources = False
        self.isolation_timer = 0

        # Define quarantine timer and flags
        self.to_be_quarantined = False
        self.using_quarantine_resources = False
        self.to_be_transferred = False
        self.days_till_quarantine = 0
        self.days_till_transfer = 0
        self.quarantine_timer = 0

        # Historic timers
        self.ever_infected = False
        self.ever_isolated = False
        self.ever_quarantined = False

        # Initialize attributes with specified dictionary values
        for key in flag_set:
            setattr(self, key, flag_set[key])

    def set_flags(self, flag_dict):
        """Set all specified flags to those in dict."""
        for key in flag_dict.keys():
            setattr(self, key, flag_dict[key])

    def increment_timer(self, timer_dict):
        """Increment all timers by value specified."""
        for key in timer_dict.keys():
            current_val = getattr(self, key)
            setattr(self, key, current_val + timer_dict[key])

    def generate_viral_load_curve(self):
        """Create random viral load curve and evaluate on discrete time."""
        # Array of infection progression period
        t = np.arange(0, 28, dtype='int')

        # Array to hold viral load at day of infection
        viral_load = np.zeros(len(t), dtype='float')

        # Generate random values necessary for construction
        t_0 = np.random.uniform(2.5, 3.5)
        t_peak = t_0 + 0.2 + np.random.gamma(1.8)
        t_f = t_peak + np.random.uniform(5, 10)
        v_peak = np.random.uniform(7, 11)
        t_end = (3 - v_peak) * ((t_f - t_peak) / (6 - v_peak)) + t_peak

        # Define piecewise functions
        def viral_load_p1(t):
            return ((v_peak - 3) / (t_peak - t_0)) * (t - t_0) + 3

        def viral_load_p2(t):
            return ((6 - v_peak) / (t_f - t_peak)) * (t - t_peak) + v_peak

        # Define bounds for each piece
        bounds_p1 = ((t >= t_0) & (t < t_peak))
        bounds_p2 = ((t >= t_peak) & (t <= t_end))

        # Calculate viral load
        viral_load[bounds_p1] = viral_load_p1(t[bounds_p1])
        viral_load[bounds_p2] = viral_load_p2(t[bounds_p2])

        # Eliminate infection at last time step
        viral_load[-1] = 0

        # Return results
        return viral_load


class GeneralPopulation():
    """Define class for general population dynamics."""

    def __init__(self, parameters):
        """Initialize necessary attributes."""
        # Lists to log counts of individuals in all states
        self.total_susceptible = []
        self.total_infected = []
        self.total_infectious = []
        self.total_recovered = []

        # Unpack dictionaries of parameters and assign attributes
        for key in parameters:
            setattr(self, key, parameters[key])

        # Initialize population
        self.initialize_population()

        # Log initial state
        self.log_state()

    def initialize_population(self):
        """Create population with given parameters."""
        # Generate susceptible subpopulation
        susceptible_flag_dict = {'susceptible': True}
        susceptible_subpopulation = {Individual(flag_set=susceptible_flag_dict)
                                     for n in range(self.num_susceptible)}

        # Generate infected subpopulation
        infected_flag_dict = {'infected': True}
        infected_subpopulation = {Individual(flag_set=infected_flag_dict)
                                  for n in range(self.num_infected)}

        # Shift initial infection back one day
        infection_range = list(
            range(-1, len(self.initial_infection_distribution) - 1))

        # Generate array of days infected for each infected individual
        days_infected = np.random.choice(
            a=infection_range,
            size=self.num_susceptible,
            replace=True,
            p=self.initial_infection_distribution)

        # Set days infected for each individual
        for individual, num_days_infected in zip(infected_subpopulation,
                                                 days_infected):
            setattr(individual, 'infection_timer', num_days_infected)

        # Assign individuals to members attribute
        self.members = susceptible_subpopulation.union(infected_subpopulation)

        # Progress infection to set proper flags/timers
        self.progress_infection()

    def fetch_subpopulation(self, flag_dict, from_subpopulation=False):
        """Fetch individuals with flags/timers matching passed dictionary."""
        # Subpopulation of individuals with matching flags/timers
        subpopulation = set()

        # Find specified source
        if not isinstance(from_subpopulation, bool):
            source = from_subpopulation
        else:
            source = self.members

        # Index through all members
        for individual in source:
            # Add to set if all attributes match
            if all([True if getattr(individual, key) == flag_dict[key]
                    else False for key in flag_dict.keys()]):
                subpopulation.add(individual)

        # Return subpopulation
        return subpopulation

    def add_to_population(self, individuals_to_be_added):
        """Add individuals back in to general populations."""
        self.members.update(individuals_to_be_added)

    def log_state(self):
        """Capture number of individuals in state and append to list."""
        # Get current counts
        num_susceptible = len(self.fetch_subpopulation({'susceptible': True}))
        num_infected = len(self.fetch_subpopulation({'infected': True}))
        num_infectious = len(self.fetch_subpopulation({'infectious': True}))
        num_recovered = len(self.fetch_subpopulation({'recovered': True}))

        # Append to lists
        self.total_susceptible.append(num_susceptible)
        self.total_infected.append(num_infected)
        self.total_infectious.append(num_infectious)
        self.total_recovered.append(num_recovered)

    def progress_infection(self):
        """Progress stage of infection for infected individuals."""
        # Fetch infected subpopulation
        infected_subpopulation = self.fetch_subpopulation({'infected': True})

        # Index through all infected individuals:
        for individual in infected_subpopulation:
            # Fetch previous viral load
            previous_viral_load = individual.viral_load

            # Increment infection timer
            individual.increment_timer({'infection_timer': 1})

            # Update current viral load and retrieve a copy
            individual.viral_load = individual.viral_load_curve[
                individual.infection_timer]
            viral_load = individual.viral_load

            # Check infected flag
            if (viral_load == 0) and (previous_viral_load > viral_load):
                individual.set_flags({'infected': False, 'recovered': True})

            # Check infectious flag
            if viral_load >= self.infectious_threshold:
                individual.set_flags({'infectious': True})
            else:
                individual.set_flags({'infectious': False})

            # Check detectable flag
            if viral_load >= self.detectable_threshold:
                individual.set_flags({'detectable': True})
            else:
                individual.set_flags({'detectable': False})

    def infect_susceptible(self):
        """Infect susceptible individuals based on current population state."""
        # Fetch neccessary counts
        num_susceptible = len(self.fetch_subpopulation({'susceptible': True}))
        num_infectious = len(self.fetch_subpopulation({'infectious': True}))

        # Break if no susceptible
        if (num_susceptible == 0):
            return

        # Fetch all interactable individuals
        interactable_individuals = self.members

        # Find number of infectious contacts
        num_infectious_contacts = sum(np.random.choice(
            a=list(range(len(self.daily_contacts_distribution))),
            size=num_infectious,
            replace=True,
            p=self.daily_contacts_distribution))

        # Select individuals to have contact with infectious individual
        contact_with_infectious = np.random.choice(
            a=list(interactable_individuals),
            size=num_infectious_contacts,
            replace=True
        )

        # Find susceptible individuals who had contact with infectious
        susceptible_contact_with_infectious = self.fetch_subpopulation(
            {'susceptible': True},
            from_subpopulation=set(contact_with_infectious)
        )

        # Number of susceptible who had contact with infectious
        num_susceptible_contact_with_infectious = len(
            susceptible_contact_with_infectious)

        # Determine if infection takes place for individuals
        infection_probability = min(1,
                                    self.probability_infection_given_contact)

        infection_statuses = np.random.choice(
            a=[True, False],
            size=num_susceptible_contact_with_infectious,
            replace=True,
            p=[infection_probability, 1-infection_probability]
        )

        # Assign infectious status to individuals
        for infection_status, individual in zip(
                infection_statuses, susceptible_contact_with_infectious):
            individual.set_flags(
                {'infected': infection_status,
                 'susceptible': not infection_status}
                                )

        # Fetch remaining susceptible individuals and apply outside infection
        remaining_susceptible = list(self.fetch_subpopulation(
            {'susceptible': True}))
        num_remaining_susceptible = len(remaining_susceptible)

        # Infection statuses from outside infection
        outside_infection_statuses = np.random.choice(
            a=[True, False],
            size=num_remaining_susceptible,
            replace=True,
            p=[self.probability_outside_infection,
               1-self.probability_outside_infection]
        )

        for infection_status, individual in zip(outside_infection_statuses,
                                                remaining_susceptible):
            individual.set_flags(
                {'infected': infection_status,
                 'susceptible': not infection_status}
                                )

        # Set historic infection for all individuals
        newly_infected = self.fetch_subpopulation((
            {'infected': True, 'ever_infected': False}))

        for individual in newly_infected:
            individual.set_flags({'ever_infected': True})

    def test_population(self):
        """Test eligible individuals and set appropriate flags and timers."""
        # Fetch individuals eleigible to test and not awaiting results
        subpopulation_to_be_tested = self.fetch_subpopulation(
            {'testable': True, 'awaiting_results': False})

        # Number of individuals being tested on day
        num_in_population = len(self.members)
        num_to_be_tested = min(
            [int(num_in_population * self.proportion_tested_daily),
             len(subpopulation_to_be_tested)])

        # Get testing delay for each test administered
        days_till_results_list = np.random.choice(
            a=list(range(len(self.days_till_results_distribution))),
            size=num_to_be_tested,
            replace=True,
            p=self.days_till_results_distribution)

        # Randomly select individuals to test
        tested_subpopulation = np.random.choice(a=list(
                                                subpopulation_to_be_tested),
                                                size=num_to_be_tested,
                                                replace=False)

        # Index through all tested individuals
        for individual, days_till_results in zip(tested_subpopulation,
                                                 days_till_results_list):
            # Prevent further testing until results are returned
            individual.set_flags({'awaiting_results': True,
                                  'days_till_results': days_till_results})

            if individual.detectable:
                individual.set_flags({'to_be_isolated': True})

    def progress_test_results(self):
        """Progress test and return individuals to be moved to isolation."""
        # Fetch individuals who are to be isolated
        individuals_to_be_isolated = self.fetch_subpopulation(
            {'to_be_isolated': True, 'days_till_results': 0})

        # Remove individuals to be isolated from general population
        self.members.difference_update(individuals_to_be_isolated)

        # Fetch remaining individuals to set appropriate flags
        individuals_retestable = self.fetch_subpopulation(
            {'days_till_results': 0})

        # Allow individuals to be retested
        for individual in individuals_retestable:
            individual.set_flags({'awaiting_results': False})

        # Fetch individuals awaiting test results
        subpopulation_awaiting_results = self.fetch_subpopulation(
            {'awaiting_results': True})

        # Decrease timer
        for individual in subpopulation_awaiting_results:
            individual.increment_timer({'days_till_results': -1})

        # Return individuals to be isolated
        return individuals_to_be_isolated

    def trace_contacts(self, num_individuals_to_be_isolated):
        """Trace contacts and set timer till individuals are quarantined."""
        # Get set of individuals eligible to be quarantined
        eligible_to_be_quarantined = self.fetch_subpopulation(
            {'to_be_quarantined': False, 'testable': True})

        # Trace new contacts if there are individuals eligible
        if len(eligible_to_be_quarantined) != 0:
            # Find total number of contacts from individuals to be isolated
            num_contacts = sum(
                np.random.choice(a=range(
                                 len(self.daily_contacts_distribution)),
                                 size=num_individuals_to_be_isolated,
                                 replace=True,
                                 p=self.daily_contacts_distribution))

            # Find number of contacts that will be successfully reached
            num_successful_contacts = 0
            for contact_num in range(num_contacts):
                if np.random.choice(a=[True, False],
                                    p=[self.probability_successful_contact,
                                       (1-self.probability_successful_contact)]
                                    ):
                    num_successful_contacts += 1

            # Randomly select individuals for quarantine
            new_individuals_to_be_quarantined = np.random.choice(
                a=list(eligible_to_be_quarantined),
                size=num_successful_contacts,
                replace=True)

            # Generate contact tracing delay for each individual
            days_till_quarantine = np.random.choice(
                a=range(len(self.days_till_quarantine_distribution)),
                size=len(new_individuals_to_be_quarantined),
                replace=True,
                p=self.days_till_quarantine_distribution)

            # Index through all individuals to be quarantined and set flags
            for individual, num_days in zip(new_individuals_to_be_quarantined,
                                            days_till_quarantine):
                # Set flags
                individual.set_flags({'to_be_quarantined': True,
                                      'days_till_quarantine': num_days})

        # Fetch all individuals to be quarantined and progress timers
        waiting_for_quarantine = self.fetch_subpopulation(
            {'to_be_quarantined': True})

        # Set of individuals to be quarantined
        individuals_to_be_quarantined = set()

        for individual in waiting_for_quarantine:
            individual.increment_timer({'days_till_quarantine': -1})

            if individual.days_till_quarantine == 0:
                individuals_to_be_quarantined.add(individual)

        # Remove individuals to be quarantined
        self.members.difference_update(individuals_to_be_quarantined)

        # Return individuals to be quarantined
        return individuals_to_be_quarantined


class Isolation():
    """Define class for isolation dynamics."""

    def __init__(self, parameters):
        """Initialize necessary attributes."""
        # Set of individuals currently in isolation
        self.members = set()

        # List for log of total isolated
        self.total_isolated = []

        # List for log of individuals isolated and using resources
        self.isolated_using_resources = []

        # Unpack dictionaries of parameters and assign attributes
        for key in parameters:
            setattr(self, key, parameters[key])

        # Log initial state
        self.log_state()

    def fetch_subpopulation(self, flag_dict):
        """Fetch individuals with flags/timers matching passed dictionary."""
        # Subpopulation of individuals with matching flags/timers
        subpopulation = set()

        # Index through all members
        for individual in self.members:
            # Add to set if all attributes match
            if all([True if getattr(individual, key) == flag_dict[key]
                    else False for key in flag_dict.keys()]):
                subpopulation.add(individual)

        # Return fetched subpopulation
        return subpopulation

    def log_state(self):
        """Capture number of individuals in isolation and append to list."""
        # Append current count of members
        self.total_isolated.append(len(self.members))

        # Fetch and append current count of individuals using resources
        num_using_resources = len(self.fetch_subpopulation(
            {'using_isolation_resources': True}))
        self.isolated_using_resources.append(num_using_resources)

    def admit_to_isolation(self, individuals_to_be_isolated):
        """Set appropriate flags and timers for individuals being admitted."""
        # Dictionary of flags and timers for isolated individuals
        isolated_dict = {
            'infected': False,
            'infectious': False,
            'recovered': True,
            'testable': self.eligible_for_retesting,
            'awaiting_results': False,
            'to_be_isolated': False,
            'isolation_timer': self.days_in_isolation,
            'ever_isolated': True
            }

        # Determine which individuals will use isolation resources
        using_resources_list = np.random.choice(
            a=[True, False],
            size=len(individuals_to_be_isolated),
            p=[self.probability_using_isolation_resources,
               (1-self.probability_using_isolation_resources)])

        # Iterate through individuals and set flags/timers
        for individual, using_resources in zip(individuals_to_be_isolated,
                                               using_resources_list):
            # Set appropriate flags and timers
            individual.set_flags(isolated_dict)
            individual.set_flags(
                {'using_isolation_resources': using_resources})

        # Include admitted individuals in set of all members
        self.members.update(individuals_to_be_isolated)

    def progress_isolation(self):
        """Progress isolation timers and find individuals to be discharged."""
        # Set of individuals to be discharged
        individuals_to_be_discharged = set()

        # Index through all isolated individuals
        for individual in self.members:
            # Decrease timer by one time step
            individual.increment_timer({'isolation_timer': -1})

            #  individuals to be discharged
            if individual.isolation_timer == 0:
                individuals_to_be_discharged.add(individual)

        # Remove individuals to be discharged
        self.members.difference_update(individuals_to_be_discharged)

        # Return individuals to be discharged
        return individuals_to_be_discharged


class Quarantine():
    """Define class for quarantine dynamics."""

    def __init__(self, parameters):
        """Initialize necessary attributes."""
        # Set of individuals currently in isolation
        self.members = set()

        # List for log of total quarantined
        self.total_quarantined = []

        # List for log of individuals isolated and using resources
        self.quarantined_using_resources = []

        # Unpack dictionaries of parameters and assign attributes
        for key in parameters:
            setattr(self, key, parameters[key])

        # Log initial state
        self.log_state()

    def fetch_subpopulation(self, flag_dict, from_subpopulation=False):
        """Fetch individuals with flags/timers matching passed dictionary."""
        # Subpopulation of individuals with matching flags/timers
        subpopulation = set()

        # Find specified source
        if not isinstance(from_subpopulation, bool):
            source = from_subpopulation
        else:
            source = self.members

        # Index through all members
        for individual in source:
            # Add to set if all attributes match
            if all([True if getattr(individual, key) == flag_dict[key]
                    else False for key in flag_dict.keys()]):
                subpopulation.add(individual)

        return subpopulation

    def log_state(self):
        """Log number of individuals currently in quarantine."""
        # Append current count of members
        self.total_quarantined.append(len(self.members))

        # Fetch and append current count of individuals using resources
        num_using_resources = len(self.fetch_subpopulation(
            {'using_quarantine_resources': True}))
        self.quarantined_using_resources.append(num_using_resources)

    def admit_to_quarantine(self, individuals_to_be_quarantined):
        """Admit individuals to quarantine and set appropriate flags/timers."""
        # Dictionary of flags for varying quarantined members
        isolated_dict = {'infected': False,
                         'recovered': True,
                         'testable': True,
                         'awaiting_results': False,
                         'to_be_quarantined': False,
                         'to_be_transferred': True,
                         'quarantine_timer': self.days_in_quarantine,
                         'ever_quarantined': True
                         }
        infected_not_detected_dict = {'infected': False,
                                      'recovered': True,
                                      'testable': True,
                                      'awaiting_results': False,
                                      'days_till_results': 0,
                                      'to_be_quarantined': False,
                                      'quarantine_timer':
                                          self.days_in_quarantine,
                                      'ever_quarantined': True
                                      }
        remaining_individuals_dict = {'awaiting_results': False,
                                      'days_till_results': 0,
                                      'to_be_quarantined': False,
                                      'quarantine_timer':
                                          self.days_in_quarantine,
                                      'ever_quarantined': True
                                      }

        # Admit all individuals
        self.members.update(individuals_to_be_quarantined)

        # Determine which individuals will use quarantine resources
        using_resources_list = np.random.choice(
            a=[True, False],
            size=len(individuals_to_be_quarantined),
            p=[self.probability_using_quarantine_resources,
               (1-self.probability_using_quarantine_resources)])

        # Iterate through individuals and set flag
        for individual, using_resources in zip(individuals_to_be_quarantined,
                                               using_resources_list):
            individual.set_flags(
                {'using_quarantine_resources': using_resources})

        # Fetch individuals already scheduled for isolation
        individuals_eventually_isolated = self.fetch_subpopulation(
            {'to_be_isolated': True},
            from_subpopulation=individuals_to_be_quarantined)

        # Set appropriate flags/timers for individuals being transferred
        for individual in individuals_eventually_isolated:
            individual.set_flags(isolated_dict)

            # Find days till transfer
            days_till_transfer = max(1, individual.days_till_results)

            # Set transfer date
            individual.set_flags({
                'days_till_transfer': days_till_transfer,
                'days_till_results': 0})

        # Fetch individuals who may be eligible to transfer
        individuals_to_check_for_transfer = self.fetch_subpopulation(
            {'to_be_isolated': False, 'infected': True},
            from_subpopulation=individuals_to_be_quarantined
            )

        # Index through all individuals and check for potential transfer
        for individual in individuals_to_check_for_transfer:
            # Check if ever detectable
            if self.ever_detectable(individual):

                # Find days till transfer
                individual.days_till_transfer = self.find_days_till_transfer(
                    individual)

                # Set appropriate flags/timers
                individual.set_flags(isolated_dict)

            # Set flags/timers for infected  who will not be detected
            else:
                individual.set_flags(infected_not_detected_dict)

        # Remove already admitted individuals from set of new admissions
        individuals_to_be_quarantined.difference_update(
            individuals_eventually_isolated,
            individuals_to_check_for_transfer)

        # Set appropriate flags/timers for remaining admissions
        for individual in individuals_to_be_quarantined:
            individual.set_flags(remaining_individuals_dict)

    def ever_detectable(self, individual):
        """Determine if an individual will be detected while quarantined."""
        # Fetch viral load info
        days_infected = individual.infection_timer
        current_viral_load = individual.viral_load
        previous_viral_load = individual.viral_load_curve[days_infected - 1]

        # Determine if they will ever become detectable
        if (current_viral_load > previous_viral_load):
            return True

        # Determine infected will not be detected during quarantine
        else:
            return False

    def find_days_till_transfer(self, individual):
        """Find day until transfer from quarantine."""
        # Fetch days infected
        days_infected = individual.infection_timer

        # Find first detectable viral load
        first_detectable_viral_load = list(
            filter(lambda viral_load: viral_load > self.detectable_threshold,
                   individual.viral_load_curve))[0]

        # Find first day detectable
        first_day_detectable = list(individual.viral_load_curve).index(
            first_detectable_viral_load)

        # Add testing lag into days till transfer
        num_days_till_transfer = first_day_detectable - days_infected \
            + np.random.choice(a=list(range(len(
                self.days_till_results_distribution))),
                p=self.days_till_results_distribution)

        # Return days till transfer
        return num_days_till_transfer

    def progress_quarantine(self):
        """Progress timer and find individuals to be discharged/transferred."""
        # Find individuals being transferred to isolation
        individuals_to_be_transferred = self.fetch_subpopulation(
            {'to_be_transferred': True, 'days_till_transfer': 0})

        # Remove those to be isolated from members
        self.members.difference_update(individuals_to_be_transferred)

        # Fetch individuals being discharged
        individuals_to_be_discharged = self.fetch_subpopulation(
            {'quarantine_timer': 0})

        # Remove those being discharged from members
        self.members.difference_update(individuals_to_be_discharged)

        # Increment quaratine timer for remaining members
        for individual in self.members:
            individual.increment_timer({'quarantine_timer': -1})

        # Find individuals who will eventually be isolated
        individuals_eventually_isolated = self.fetch_subpopulation(
            {'to_be_transferred': True})

        for individual in individuals_eventually_isolated:
            individual.increment_timer({'days_till_transfer': -1})

        # Return sets of individuals being transferred/discharged
        return individuals_to_be_transferred, individuals_to_be_discharged


# Define function to simulate the progression of a single time step
def simulate_time_step(general_population, quarantine, isolation):
    """Simulate a discrete time step for the passed components."""
    # Progress infection
    general_population.progress_infection()

    # Infect susceptible
    general_population.infect_susceptible()

    # Test individuals
    general_population.test_population()

    # Progress test results and fetch individuals to be isolated
    individuals_to_be_isolated = general_population.progress_test_results()

    # Trace contacts and find individuals to be quarantined
    individuals_to_be_quarantined = general_population.trace_contacts(
        len(individuals_to_be_isolated))

    # Admit individuals to quarantine
    quarantine.admit_to_quarantine(individuals_to_be_quarantined)

    # Progress quarantine
    (individuals_to_be_transferred,
     individuals_discharged_from_quarantine) = quarantine.progress_quarantine()

    # Progress isolation
    individuals_discharged_from_isolation = isolation.progress_isolation()

    # Find all individuals being admitted to isolation
    all_individuals_being_isolated = individuals_to_be_isolated.union(
        individuals_to_be_transferred)

    # Admit individuals to isolation
    isolation.admit_to_isolation(all_individuals_being_isolated)

    # All individuals being readmitted back in to general population
    all_individuals_discharged = individuals_discharged_from_isolation.\
        union(individuals_discharged_from_quarantine)

    # Readmit individuals
    general_population.add_to_population(all_individuals_discharged)

    # Update logs of number of individuals in different states
    general_population.log_state()
    quarantine.log_state()
    isolation.log_state()
