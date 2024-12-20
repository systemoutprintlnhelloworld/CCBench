import os
import copy
import argparse
import collections
import numpy as np
import pandas as pd
import seaborn as sns
import scipy.stats as stats
import matplotlib.pyplot as plt

from utils import subfields
from utils import argparse_helper


def plot_human_expertise_distributions_by_subfields(use_human_abstract):
    plt.rcParams.update({'font.size': 16, 'font.weight': 'bold'})

    df = pd.read_csv(f"{human_results_dir}/data/participant_data.csv")
    if use_human_abstract:
        who = "human"
    else:
        who = "machine"

    human_expertise_all_subfields = collections.defaultdict(list)
    for subfield in subfields.subfield_names:
        for _, row in df.iterrows():
            if row["journal_section"].startswith(who) and row["journal_section"].endswith(subfield):
                human_expertise_all_subfields[subfield].append(row["expertise"])

    # Plot five subplots, each showing the distribution of expertise for a subfield
    fig, axs = plt.subplots(5, 1, figsize=(5, 10))
    for i, subfield in enumerate(subfields.subfield_names):
        sns.kdeplot(human_expertise_all_subfields[subfield], ax=axs[i], color="skyblue")
        axs[i].set_xlabel("Expertise")
        axs[i].set_ylabel("Density")
        axs[i].set_title(f"{subfield}")

        # Plot vertical lines indicating top 20% expertise
        top_20_percentile = np.percentile(human_expertise_all_subfields[subfield], 80)
        axs[i].axvline(top_20_percentile, color="purple", linestyle="--", label="Top 20%")
        axs[i].legend(loc="lower left")
    
    plt.tight_layout()
    plt.savefig(f"{figs_dir}/expertise_by_subfields_distribution_{who}_abstracts.pdf")


def _plot_calibration_human(subfield, human_results_dir, ax, color="blue"):
    # Read data
    df = pd.read_csv(f"{human_results_dir}/data/participant_data.csv")

    # Iterate over rows based on who created the case
    # For each who, collect expertise for correct and incorrect responses
    if use_human_abstract:
        who = "human"
    else:
        who = "machine"
        
    expertises = []
    corrects_n_incorrects = []  # 1 and 0

    for _, row in df.iterrows():
        if row["journal_section"].startswith(who):
            if subfield is None:
                # get expertise and correct
                expertise = row["expertise"]
                correct = row["correct"]
                expertises.append(expertise)
                corrects_n_incorrects.append(correct)
            else:
                if row["journal_section"].endswith(subfield):
                    # get expertise and correct
                    expertise = row["expertise"]
                    correct = row["correct"]
                    expertises.append(expertise)
                    corrects_n_incorrects.append(correct)

    # Plot calibration
    expertises = stats.rankdata(expertises, method='ordinal') - 1.
    print(expertises, len(expertises))

    # Bin the expertises and compute the accuracy per bin
    bin_boundaries = np.linspace(0, len(expertises), n_bins + 1)
    bin_lowers = bin_boundaries[:-1]
    bin_uppers = bin_boundaries[1:]
    bin_heights = []  # acc in each bin
    overall_acc = []  # sanity check
    for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
        in_bin = np.logical_and(
            expertises >= bin_lower.item(), 
            expertises < bin_upper.item()
        )

        print(f"bin {bin_lower}-{bin_upper} has {np.sum(in_bin)} samples")

        prop_in_bin = in_bin.astype(float).mean()
        assert prop_in_bin == (np.sum(in_bin) / len(in_bin))

        acc_in_bin = np.mean(np.array(corrects_n_incorrects)[in_bin])
        bin_heights.append(acc_in_bin)
        overall_acc.append(acc_in_bin * prop_in_bin)
    
    print(f"[Check] {subfield} Overall Accuracy: {np.sum(overall_acc)}")
    
    # Plot bins as bar chart using bin_heights
    bin_midpoints = bin_lowers + (bin_uppers - bin_lowers) / 2
    bin_widths = (bin_uppers - bin_lowers)
    ax.bar(
        bin_midpoints, 
        bin_heights,
        width=bin_widths, 
        edgecolor='k', 
        color=color,
        alpha=0.5, 
    )
    ax.set_ylabel("Accuracy")
    ax.set_ylim(0, 1)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_xlabel("Expertise")
    ax.set_xticks([])

    # Add a regression line (fitting rank and accuracy in bin)
    x = np.array(bin_midpoints)
    y = np.array(bin_heights)
    # fit a regression line
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

    # plot the regression line
    ax.plot(
        x, intercept + slope*x, 
        'k', 
        label='fitted line',
        linewidth=plt.rcParams['lines.linewidth'] * 2,
    )


def plot_human_expertise_calibration(use_human_abstract):
    plt.rcParams.update({'font.size': 22, 'font.weight': 'bold'})
    
    if use_human_abstract:
        type_of_abstract = 'human_abstracts'
    else:
        type_of_abstract = 'llm_abstracts'

    subfield_names = subfields.subfield_names
    subfields_colors = subfields.subfield_colors
    total_subplots = len(subfield_names) + 1  # +1 for overall
    n_rows = 2 
    n_cols = total_subplots // n_rows
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 10))

    # First plot overall calibration
    _plot_calibration_human(None, human_results_dir, axes[0, 0])
    axes[0, 0].set_title("Overall", fontsize=22, fontweight='bold')

    # Plot calibration for each subfield
    for i, subfield in enumerate(subfield_names):
        row, col = (i + 1) // n_cols, (i + 1) % n_cols
        _plot_calibration_human(subfield, human_results_dir, axes[row, col], color=subfields_colors[i])
        axes[row, col].set_title(subfield, fontsize=22,)
    
    plt.tight_layout()
    plt.savefig(f"{figs_dir}/expertise_calibration_{type_of_abstract}.pdf")
    

def main():
    plot_human_expertise_distributions_by_subfields(use_human_abstract)
    plot_human_expertise_calibration(use_human_abstract)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--use_human_abstract", type=argparse_helper.str2bool, default=True)
    
    PPL_fname = "PPL_A_and_B"
    label_fname = "labels"
    n_bins = 4  # control % points a bin if xaxis is probability
    use_human_abstract = parser.parse_args().use_human_abstract
    model_results_dir = "model_results"
    human_results_dir = "human_results"
    testcases_dir = "testcases"
    figs_dir = "figs"
    main()
