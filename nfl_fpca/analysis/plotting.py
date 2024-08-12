import matplotlib.pyplot as plt
import numpy as np


def plot_player_av(player):
    # Raw AV curves
    raw_stats, time = player.get_stats_array('av')
    time -= player.start_year

    # Adjust for injuries
    player.adjust_for_injuries(threshold=5)
    adj_stats, adj_time = player.get_stats_array('av')
    adj_time -= player.start_year

    plt.clf()

    plt.scatter(time, raw_stats['av'], color='red')
    plt.scatter(adj_time, adj_stats['av'], color='blue', marker='x')

    # Axis limits
    plt.xlim([0, time[-1]+1])
    plt.ylim([0, raw_stats['av'].max()+1])

    plt.grid()

    # Labels and title
    first_name = player.first_name.replace('.', '')
    last_name = player.last_name.replace('.', '')

    plt.title(f"AV curve - {first_name} {last_name}, {player.position}")
    plt.xlabel("Years of experience")
    plt.ylabel("Approximate Value")

    plt.savefig(f"imgs/players/AV_{first_name}_{last_name}_{player.position}.pdf", dpi=300)