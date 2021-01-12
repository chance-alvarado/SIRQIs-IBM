"""Write results from simulations to a specified or generic location.

Results for a batch of simulations are written to a a user-specified or
generic indexed directory. Each individual simulation for the run is
stored as an indexed CSV file. A copy of the parameters used for simulations
is also stored.

More information can be found in this project's README file.

Explore this repository at:
    https://github.com/chance-alvarado/SIRQIs-IBM/

Author:
    Chance Alvarado
        LinkedIn: https://www.linkedin.com/in/chance-alvarado/
        GitHub: https://github.com/chance-alvarado/

"""
# Imports
import csv
import os
from glob import glob
from shutil import copyfile


# Define ResultsWriter class
class ResultsWriter():
    """Define class for writing results to file."""

    def __init__(self, main_results_dir='results', batch_dir='batch',
                 run_filename='run'):
        """Initialize attributes and ensure proper directories are presenet."""
        # Main directory for results
        self.main_results_dir = main_results_dir

        # Directory handle for batch
        self.batch_dir = '/'.join([main_results_dir, batch_dir])

        # Run filename handle
        self.run_filename = run_filename

        # Count files written to suffix files
        self.num_runs = 0

        # Suffix padding
        self._suffix_pad = 5

        # Set directories
        self.set_directories()

    def set_directories(self):
        """Ensure proper directories are present."""
        # Ensure a results directory exists
        if not os.path.isdir(self.main_results_dir):
            os.mkdir(self.main_results_dir)

        # Find number of batch directories matching current
        num_matches = len(glob(''.join([self.batch_dir, '*'])))

        # Pad number of matches and append as suffix
        matches_suffix = ''.join(['_',
                                  str(num_matches).zfill(self._suffix_pad)])

        # Update batch dir
        batch_dir = ''.join([self.batch_dir, matches_suffix])
        self.batch_dir = batch_dir

        # Try to make batch directory
        try:
            os.mkdir(batch_dir)

        # Raise error if user deleting file messes with indexing
        except FileExistsError:
            raise FileExistsError(
                "Cannot create file due to possible batch file deletion. "
                "Please save results to a different 'batch' directory "
                "or replace the missing indexed file."
                )

    def parameters_copy(self, fetch_path='default'):
        """Generate a copy of the simulation parameters for reference."""
        # Fetch path
        if fetch_path == 'default':
            fetch_path = 'parameters.py'

        # Copy path
        copy_path = ''.join([self.batch_dir, '/parameters_copy.py'])

        # Copy file
        copyfile(fetch_path, copy_path)

    def write_to_file(self,
                      susceptible, infected, recovered,
                      total_quarantined, quarantined_using_resources,
                      total_isolated, isolated_using_resources):
        """Write current simulation results to file as a CSV."""
        # Construct unique run path
        run_path = ''.join([self.batch_dir, '/',
                            self.run_filename,
                            '_', str(self.num_runs).zfill(self._suffix_pad),
                            '.csv'])

        # Update run counter
        self.num_runs = self.num_runs + 1

        # Construct rows of data
        index = list(range(len(susceptible)))
        rows = [row for row in zip(index,
                                   susceptible, infected, recovered,
                                   total_quarantined,
                                   quarantined_using_resources,
                                   total_isolated,
                                   isolated_using_resources)]

        # Column headers
        headers = ['days',
                   'susceptible', 'infected', 'recovered',
                   'total_quarantined', 'quarantined_using_resources',
                   'total_isolated', 'isolated_using_resources']

        # Open file
        with open(run_path, mode='x') as file:
            # Define writer
            writer = csv.writer(file)

            # Write header to file
            writer.writerow(headers)

            # Write all rows to file
            for row in rows:
                writer.writerow(row)
