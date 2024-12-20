import os
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import ttest_rel
import pingouin as pg

from utils import model_list
from utils import argparse_helper
from utils import scorer

plt.rcParams.update({'font.size': 16, 'font.weight': 'bold'})

def get_llm_accuracies(model_results_dir, use_human_abstract=True):
    llms = model_list.llms
    for llm_family in llms.keys():
        for llm in llms[llm_family]:
            if use_human_abstract:
                type_of_abstract = 'human_abstracts'
            else:
                type_of_abstract = 'llm_abstracts'

            results_dir = os.path.join(
                f"{model_results_dir}/{llm.replace('/', '--')}/{type_of_abstract}"
            )

            PPL_fname = "PPL_A_and_B"
            label_fname = "labels"
            PPL_A_and_B = np.load(f"{results_dir}/{PPL_fname}.npy")
            labels = np.load(f"{results_dir}/{label_fname}.npy")

            acc = scorer.acc(PPL_A_and_B, labels)
            sem = scorer.sem(PPL_A_and_B, labels)
            llms[llm_family][llm]["acc"] = acc
            llms[llm_family][llm]["sem"] = sem
    return llms


def get_human_accuracies(use_human_abstract):
    """
    Overall accuracy (based on `correct` column) for `human` created cases
    """
    # Read data
    df = pd.read_csv(f"{human_results_dir}/data/participant_data.csv")
    if use_human_abstract:
        who = "human"
    else:
        who = "machine"

    correct = 0
    total = 0
    for _, row in df.iterrows():
        if row["journal_section"].startswith(who):
            correct += row["correct"]
            total += 1
    acc = correct / total
    sem = np.sqrt(acc * (1 - acc) / total)
    print(f"correct: {correct}, total: {total}")
    return acc, sem


def get_human_accuracies_top_expertise(use_human_abstract, top_pct=0.2):
    """
    Overall accuracy (based on `correct` column) for `human` created cases,
    but for each abstract_id, only uses experts with top 20% rated expertise
    """
    # Read data
    df = pd.read_csv(f"{human_results_dir}/data/participant_data.csv")
    
    if use_human_abstract:
        who = "human"
    else:
        who = "machine"

    # Group by abstract_id and journal_section that starts with `who`
    # Then, for each abstract_id, only use experts with top 20% rated expertise
    df_grouped = df[df["journal_section"].str.startswith(who)].groupby("abstract_id")
    df_grouped = df_grouped.apply(
        lambda x: x.nlargest(int(len(x)*top_pct), "expertise")
    )
    df_grouped = df_grouped.reset_index(drop=True)

    correct = 0
    total = 0
    for _, row in df_grouped.iterrows():
        correct += row["correct"]
        total += 1
    acc = correct / total
    sem = np.sqrt(acc * (1 - acc) / total)
    return acc, sem


def plot(use_human_abstract):
    """
    Plot LLMs vs human experts.

    1) Plot accuracy of each llm as a bar. 
    Bar height is accuracy, bar groups by llm family.
    Bar color and hatch follow keys in `llms` dict.

    2) Plot human experts as a horizontal line
    """
    llms = get_llm_accuracies(model_results_dir, use_human_abstract)

    fig, ax = plt.subplots(figsize=(8, 6))

    # llms
    all_llm_accuracies = []
    all_llm_sems = []
    all_llm_names = []
    all_llm_colors = []
    all_llm_hatches = []
    all_llm_xticks = []

    for family_index, llm_family in enumerate(llms.keys()):
        for llm in llms[llm_family]:
            all_llm_accuracies.append(llms[llm_family][llm]["acc"])
            all_llm_sems.append(llms[llm_family][llm]["sem"])
            all_llm_names.append(llms[llm_family][llm]["llm"])
            all_llm_colors.append(llms[llm_family][llm]["color"])
            all_llm_hatches.append(llms[llm_family][llm]["hatch"])
            # Anchor on `family_index`
            # llm within a family should be spaced out smaller than between families
            all_llm_xticks.append(family_index*3 + len(all_llm_xticks))
    
    # Bar
    ax.bar(
        all_llm_xticks, all_llm_accuracies,
        yerr=all_llm_sems,
        color=all_llm_colors,
        hatch=all_llm_hatches,
        alpha=0.7,
        label=all_llm_names,
        edgecolor='k',
        capsize=3
    )

    # human
    # plot as horizontal line
    human_acc, human_sem = get_human_accuracies(use_human_abstract)
    ax.axhline(
        xmin=all_llm_xticks[0], 
        xmax=all_llm_xticks[-1]+1,
        y=human_acc, 
        color='b', 
        linestyle='--', 
        lw=3
    )
    ax.fill_between(
        [all_llm_xticks[0], all_llm_xticks[-1]+1],
        human_acc-human_sem,
        human_acc+human_sem,
        color='b',
        alpha=0.2
    )


    print('human_acc:', human_acc)
    human_acc_top_expertise, human_sem_top_expertise = get_human_accuracies_top_expertise(use_human_abstract)
    print('human_acc_top_expertise:', human_acc_top_expertise)

    # Add annotations (Human expert)
    # In the middle of the plot, below the horizontal line
    ax.text(
        (all_llm_xticks[-1])-7,
        human_acc-0.024,
        "Human experts",
        fontsize=16,
        color='k'
    )

    ax.set_ylabel("Accuracy")
    ax.set_ylim([0.5, 1])
    ax.set_xlim([None, all_llm_xticks[-1]+1])
    ax.set_xticks([])
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    plt.legend(all_llm_names, loc='upper left', ncol=2, bbox_to_anchor=(-0.2, 1.2))
    plt.tight_layout()
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    if use_human_abstract:
        plt.savefig(f"{base_fname}_human_abstract.svg")
    else:
        plt.savefig(f"{base_fname}_llm_abstract.svg")


    # stats
    # ttest, p value, ci cohen's d etc.
    # ttest between human and llm
    all_llm_accuracies = np.array(all_llm_accuracies)
    human_acc = np.array([human_acc] * len(all_llm_accuracies))
    results = pg.ttest(all_llm_accuracies, human_acc, paired=True)
    print(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--use_human_abstract", type=argparse_helper.str2bool, default=True)

    model_results_dir = "model_results"
    human_results_dir = "human_results"
    base_fname = "figs/overall_accuracy_model_vs_human"
    plot(parser.parse_args().use_human_abstract)