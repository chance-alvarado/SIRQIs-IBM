"""Importable module for plotting specified batches of simulations.

This following module is responsible for plotting a simple representation of
all simulations within a bitch folder. Individual and averaged time series
data is plotted for each state present in the SIRQIs model (susceptible,
infected, recovered, total quarantined, quarantined using resources,
total isolated, isolated using resources). The 'figsize' parameter along with
multiple dictionaries can be modified in file to fine-tune the plots as needed.

More information can be found in this project's README file.

Explore this repository at:
    https://github.com/chance-alvarado/SIRQIs-IBM/

Author:
    Chance Alvarado
        LinkedIn: https://www.linkedin.com/in/chance-alvarado/
        GitHub: https://github.com/chance-alvarado/
"""
# Imports
import glob
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# Specified figure size
figsize = (17, 8)

# Customizable plot keyword dictionaries
individual_kws = {
    'lw': 2,
    'alpha': 0.1,
    'c': 'lightblue'
}

average_kws = {
    'lw': 2,
    'alpha': 1,
    'c': 'blue',
    'ls': '--'
}

individual_using_resources_kws = {
    'lw': 2,
    'alpha': 0.1,
    'c': 'lightgreen'
}

average_using_resources_kws = {
    'lw': 2,
    'alpha': 1,
    'c': 'green',
    'ls': '--'
}

font_kws = {
    'fontsize': 16
}


# Define plotting routine as function to call
def plot_batch(batch_dir):
    """Plot simulation results based on specified batch directory."""
    # Initialize figure and create gridspec
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(3, 2)

    # Create axes objects
    ax_s = fig.add_subplot(gs[0, 0])
    ax_i = fig.add_subplot(gs[1, 0])
    ax_r = fig.add_subplot(gs[0, 1])
    ax_inf = fig.add_subplot(gs[2, 0])
    ax_q = fig.add_subplot(gs[1, 1])
    ax_is = fig.add_subplot(gs[2, 1])

    # List of plotted axes
    axes = [ax_s, ax_i, ax_r, ax_inf, ax_q, ax_is]

    # Set grid on axes
    for ax in axes:
        ax.grid('On', alpha=0.5)

    # Set titles
    ax_s.set_title('Susceptible', **font_kws)
    ax_i.set_title('Infected', **font_kws)
    ax_r.set_title('Recovered', **font_kws)
    ax_inf.set_title('Infectious', **font_kws)
    ax_q.set_title('Total Quarantined / Quarantined Using Resources',
                   **font_kws)
    ax_is.set_title('Total Isolated / Isolated Using Resources',
                    **font_kws)

    # Set axis labels for entire figure
    fig.text(x=0.5, y=0, s='Days Since Start of Simulation', va='top',
             ha='center',
             **font_kws)
    fig.text(x=0.0, y=0.5, s='Number of Individuals Present in State',
             va='center',
             ha='right', rotation='vertical', **font_kws)

    # Find path to search with glob
    path_to_search = ''.join([batch_dir, '/run*'])

    # All files to plot
    all_simulation_files = glob.glob(path_to_search)

    # Number of simulation files in batch
    num_runs = len(all_simulation_files)

    # Number of days simulated
    num_days = len(pd.read_csv(all_simulation_files[0]))

    # Add title
    fig.suptitle(f'Simulated Progression of Infection (n={num_runs})',
                 fontsize=25, y=1.03)

    # Define list of needed columns
    applicable_columns = [
        'susceptible',
        'infected',
        'recovered',
        'infectious',
        'total_quarantined',
        'quarantined_using_resources',
        'total_isolated',
        'isolated_using_resources'
    ]

    # Create dictionary to average simulations
    averaged_dict = {}
    for col in applicable_columns:
        averaged_dict[col] = [0] * (num_days)

    # Iterate through all simulation files
    for simulation_file in all_simulation_files:
        # Create temporary DataFrame
        df_temp = pd.read_csv(simulation_file)

        # Plot current iteration
        ax_s.plot(df_temp.susceptible, **individual_kws)
        ax_i.plot(df_temp.infected, **individual_kws)
        ax_r.plot(df_temp.recovered, **individual_kws)
        ax_inf.plot(df_temp.infectious, **individual_kws)
        ax_q.plot(df_temp.total_quarantined, **individual_kws)
        ax_q.plot(df_temp.quarantined_using_resources,
                  **individual_using_resources_kws)
        ax_is.plot(df_temp.total_isolated, **individual_kws)
        ax_is.plot(df_temp.isolated_using_resources,
                   **individual_using_resources_kws)

        # Update averaging dict
        for key in averaged_dict.keys():
            # Find needed values
            current_sum = averaged_dict[key]
            new_values = list(df_temp[key].values)

            # Sum and assign to dicationary
            averaged_dict[key] = [c + n for c, n
                                  in zip(current_sum, new_values)]

    # Average simulations
    for key in averaged_dict.keys():
        averaged_dict[key] = [value / num_runs for value
                              in averaged_dict[key]]

    # Plot average of all simulations
    ax_s.plot(averaged_dict['susceptible'], **average_kws)
    ax_i.plot(averaged_dict['infected'], **average_kws)
    ax_r.plot(averaged_dict['recovered'], **average_kws)
    ax_inf.plot(averaged_dict['infectious'], **average_kws)
    line_q, = ax_q.plot(averaged_dict['total_quarantined'], **average_kws)
    line_q_r, = ax_q.plot(averaged_dict['quarantined_using_resources'],
                          **average_using_resources_kws)
    line_is, = ax_is.plot(averaged_dict['total_isolated'], **average_kws)
    line_is_r, = ax_is.plot(averaged_dict['isolated_using_resources'],
                            **average_using_resources_kws)

    # Add legend to appropriate axes
    ax_q.legend(handles=[line_q, line_q_r],
                labels=['Total', 'Using Resources'],
                loc='upper right', fontsize=12)
    ax_is.legend(handles=[line_is, line_is_r],
                 labels=['Total', 'Using Resources'],
                 loc='upper right', fontsize=12)

    # Apply tight layout
    fig.tight_layout()

    # Save figure
    fig.savefig('/'.join([batch_dir, 'summary_plot.png']),
                bbox_inches='tight')
