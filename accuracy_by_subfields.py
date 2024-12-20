import os
import copy
import argparse
import collections
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from utils import subfields
from utils import model_list
from utils import argparse_helper
from utils import scorer

plt.rcParams.update({'font.size': 16, 'font.weight': 'bold'})


def get_llm_acc_subfields(use_human_abstract=True):
    if use_human_abstract:
        type_of_abstract = "human_abstracts"
        human_abstracts_fpath = f"{testcases_dir}/BrainBench_Human_v0.1.csv"
        df = pd.read_csv(human_abstracts_fpath)
        journal_column_name = "journal_section"
    else:
        type_of_abstract = "llm_abstracts"
        llm_abstracts_fpath = f"{testcases_dir}/BrainBench_GPT-4_v0.1.csv"
        df = pd.read_csv(llm_abstracts_fpath)
        journal_column_name = "journal_section"

    llms = copy.deepcopy(model_list.llms)

    # e.g.,
    # {
    #     "subfield1": {
    #         "llm1": {"acc": 0.5, "color": "red", "alpha": 0.5, "hatch": "//"},
    #         "llm2": {"acc": 0.5, "color": "red", "alpha": 0.5, "hatch": "//"},
    #         ...
    #     },
    all_subfields_llms = collections.defaultdict(
        lambda: collections.defaultdict(
            lambda: collections.defaultdict()
        )
    )
    for subfield in subfields.subfield_names:
        for llm_family in llms.keys():
            for llm in llms[llm_family]:
                results_dir = os.path.join(
                    f"{model_results_dir}/{llm.replace('/', '--')}/{type_of_abstract}"
                )
                PPL_fname = "PPL_A_and_B"
                label_fname = "labels"
                PPL_A_and_B = np.load(f"{results_dir}/{PPL_fname}.npy")
                labels = np.load(f"{results_dir}/{label_fname}.npy")

                results_by_subfield = collections.defaultdict(list)
                labels_by_subfield = collections.defaultdict(list)
                # For each sample, need to iterate through df to find their subfield
                # and record the corresponding PPL for A and B, and label.
                for j, (ppl_A, ppl_B) in enumerate(PPL_A_and_B):
                    row = df.iloc[j]
                    if row[journal_column_name] == subfield:
                        results_by_subfield[subfield].append([ppl_A, ppl_B])
                        labels_by_subfield[subfield].append(labels[j])

                # Compute acc and sem by category
                all_subfields_llms[subfield][llm]['acc'] = \
                    scorer.acc(
                        np.array(results_by_subfield[subfield]), 
                        np.array(labels_by_subfield[subfield])
                )
                all_subfields_llms[subfield][llm]['sem'] = \
                    scorer.sem(
                        np.array(results_by_subfield[subfield]), 
                        np.array(labels_by_subfield[subfield])
                )

                # Get color, alpha, hatch
                all_subfields_llms[subfield][llm]['color'] = \
                    llms[llm_family][llm]['color']
                all_subfields_llms[subfield][llm]['alpha'] = \
                    llms[llm_family][llm]['alpha']
                all_subfields_llms[subfield][llm]['hatch'] = \
                    llms[llm_family][llm]['hatch']
    
    return all_subfields_llms


def get_human_acc_subfields(use_human_abstract, top_npct_expertise=None):
    df = pd.read_csv(f"{human_results_dir}/data/participant_data.csv")
    if use_human_abstract:
        who = "human"
    else:
        who = "machine"

    all_subfields_human_acc = collections.defaultdict(
        lambda: collections.defaultdict()
    )
    all_subfields_human_sem = {}
    for subfield in subfields.subfield_names:
        correct = []
        expertise = []
        total_per_subfield = 0
        for _, row in df.iterrows():
            if row["journal_section"].startswith(who) and row["journal_section"].endswith(subfield):
                correct.append(row["correct"])
                expertise.append(row["expertise"])
                total_per_subfield += 1

        print(f"Subfield: {subfield}, human total: {total_per_subfield}")

        if top_npct_expertise:
            top_20_percentile = np.percentile(expertise, 100 - top_npct_expertise)
            correct = [c for c, e in zip(correct, expertise) if e >= top_20_percentile]

        all_subfields_human_acc[subfield] = np.mean(correct)
        all_subfields_human_sem[subfield] = np.sqrt(
            all_subfields_human_acc[subfield] * (1 - all_subfields_human_acc[subfield]) / len(correct)
        )
    return all_subfields_human_acc, all_subfields_human_sem


def get_subfield_proportions(use_human_abstract):
    if use_human_abstract:
        human_abstracts_fpath = f"{testcases_dir}/BrainBench_Human_v0.1.csv"
        df = pd.read_csv(human_abstracts_fpath)
        journal_column_name = "journal_section"
    else:
        llm_abstracts_fpath = f"{testcases_dir}/BrainBench_GPT-4_v0.1.csv"
        df = pd.read_csv(llm_abstracts_fpath)
        journal_column_name = "journal_section"
    
    subfield_proportions = collections.defaultdict(
        lambda: collections.defaultdict()
    )
    for subfield in subfields.subfield_names:
        total = 0
        for _, row in df.iterrows():
            if row[journal_column_name] == subfield:
                total += 1
        print(f"Subfield: {subfield}, total: {total}")
        subfield_proportions[subfield] = total / len(df)
    return subfield_proportions


def bar_plot(use_human_abstract, top_npct_expertise=None):
    fig, axes = plt.subplots(3, 2, figsize=(15, 15))  # Create a 3x2 subplot grid
    axes = axes.flatten()  # Flatten the axes array for easier indexing
    all_subfields_human, all_subfields_human_sem = get_human_acc_subfields(use_human_abstract, top_npct_expertise)
    all_subfields_llms = get_llm_acc_subfields(use_human_abstract)

    subfield_idx = 0  # Track the current subfield being processed
    for subfield in subfields.subfield_names:
        ax = axes[subfield_idx]
        subfield_idx += 1

        # Plot human accuracy
        ax.bar(
            0,
            all_subfields_human[subfield],
            yerr=all_subfields_human_sem[subfield],
            color="blue", alpha=0.5,
            label="Human experts",
            edgecolor="black",
            capsize=3
        )

        # Plot llm accuracy
        llm_i = 1
        for llm_family in model_list.llms.keys():
            for llm in model_list.llms[llm_family]:
                llm_legend = model_list.llms[llm_family][llm]['llm']
                if llm_legend == "Falcon-180B\n  (chat)":
                    llm_legend = "Falcon-180B (chat)"
                ax.bar(
                    llm_i,
                    all_subfields_llms[subfield][llm]['acc'],
                    yerr=all_subfields_llms[subfield][llm]['sem'],
                    color=all_subfields_llms[subfield][llm]['color'],
                    alpha=all_subfields_llms[subfield][llm]['alpha'],
                    hatch=all_subfields_llms[subfield][llm]['hatch'],
                    label=llm_legend,
                    edgecolor="black",
                    capsize=3
                )
                llm_i += 1

        if subfield == "Development/Plasticity/Repair":
            subfield_title = "Development/Plasticity/Repair"
        else:
            subfield_title = subfield
        ax.set_title(f"{subfield_title}")
        ax.set_xticks([])
        ax.set_ylim(0, 1)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.set_ylabel("Accuracy")
    
    # Remove the plot subplot to be empty and 
    # be able to place the legend in the last subplot
    fig.delaxes(axes[-1])

    # Place the legend in the last subplot (bottom right)
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(
        handles, labels, loc='lower right', ncol=2,
        bbox_to_anchor=(.95, .22)
    )

    # Adjust layout and spacing
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.2, right=0.85)

    # Save figure
    base_fname = "figs/accuracy_all_subfields"
    if use_human_abstract:
        plt.savefig(f"{base_fname}_human_abstract.pdf")
    else:
        plt.savefig(f"{base_fname}_llm_abstract.pdf")
    plt.close(fig)


def radar_plot(use_human_abstract, top_npct_expertise=None):
    from math import pi

    subfield_abbreviations = {
        "Development/Plasticity/Repair": "Dev/Plast/Rep",
        "Behavioral/Cognitive": "Behav/Cog",
        "Cellular/Molecular": "Cell/Mol",
        "Neurobiology of Disease": "Neuro Dis",
        "Systems/Circuits": "Sys/Circ"
    }
    
    all_subfields_human, _ = get_human_acc_subfields(use_human_abstract, top_npct_expertise)
    all_subfields_llms = get_llm_acc_subfields(use_human_abstract)

    # Initialize figure for comparing human and average LLM accuracy
    fig = plt.figure(figsize=(12, 6))
    ax1 = fig.add_subplot(121)
    
    # Radar chart setup
    num_variables = len(subfield_abbreviations)
    angles = [n / float(num_variables) * 2 * pi for n in range(num_variables)]
    angles += angles[:1]  # Complete the loop
    
    # Data for radar chart
    llm_accuracies = []
    human_accuracies = []
    
    # for subfield in subfield_abbreviations.keys():
    for subfield in subfields.subfield_names:
        llm_accuracies.append(np.mean([all_subfields_llms[subfield][llm]['acc'] for llm_family in model_list.llms for llm in model_list.llms[llm_family]]))
        human_accuracies.append(all_subfields_human[subfield])
    
    # Complete the loop for plotting
    llm_accuracies += llm_accuracies[:1]
    human_accuracies += human_accuracies[:1]

    # Plotting the subfield proportion figure as pie chart
    subfield_proportions = get_subfield_proportions(use_human_abstract)

    ax1.pie(
        [subfield_proportions[sf] for sf in subfields.subfield_names], 
        labels=[subfield_abbreviations[sf] for sf in subfields.subfield_names],
        autopct='%1.1f%%',
        startangle=90,
        colors=subfields.subfield_colors,
        textprops={'fontsize': 16},
        wedgeprops={"edgecolor": "black", "linewidth": 0.5}
    )

    # Second subplot: Radar chart
    ax2 = fig.add_subplot(122, polar=True)
    ax2.set_ylim(0.5, 1)
    ax2.set_theta_offset(pi*.9)
    ax2.set_theta_direction(1)
    
    plt.xticks(angles[:-1], [subfield_abbreviations[sf] for sf in subfields.subfield_names], color='k', size=16)
    
    ax2.plot(angles, llm_accuracies, linewidth=1, linestyle='solid')
    ax2.fill(angles, llm_accuracies, 'o', alpha=0.3, label='Average LLM')
    
    ax2.plot(angles, human_accuracies, linewidth=1, linestyle='solid')
    ax2.fill(angles, human_accuracies, 'b', alpha=0.3, label='Human')
    
    plt.legend(loc='upper right', bbox_to_anchor=(0.8, -0.05))
    
    plt.tight_layout()

    # Save the comparison figure
    fname = "figs/comparison_human_llm_accuracy_subfields"
    if use_human_abstract:
        plt.savefig(f"{fname}_human_abstract.pdf")
        if top_npct_expertise:
            plt.savefig(f"{fname}_human_abstract_top{top_npct_expertise}.pdf")
    else:
        plt.savefig(f"{fname}_llm_abstract.pdf")
        if top_npct_expertise:
            plt.savefig(f"{fname}_llm_abstract_top{top_npct_expertise}.pdf")
    plt.close(fig)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--use_human_abstract",
        type=argparse_helper.str2bool,
        default=True
    )
    parser.add_argument(
        "--top_npct_expertise",
        type=int,
        default=None
    )

    model_results_dir = "model_results"
    human_results_dir = "human_results"
    testcases_dir = "testcases"
    radar_plot(
        use_human_abstract=parser.parse_args().use_human_abstract, 
        top_npct_expertise=parser.parse_args().top_npct_expertise
    )
    bar_plot(use_human_abstract=parser.parse_args().use_human_abstract)
