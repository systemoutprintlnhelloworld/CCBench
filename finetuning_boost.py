import os
import argparse
import numpy as np
import seaborn as sns
import pingouin as pg
from scipy import stats
import matplotlib.pyplot as plt

from utils import scorer
from utils import model_list
from utils import argparse_helper

plt.rcParams.update({"font.size": 16, "font.weight": "bold"})

def get_llm_accuracies(use_human_abstract):
    llms = model_list.mistral_finetunes
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

            llms[llm_family][llm]["acc"] = scorer.acc(PPL_A_and_B, labels)
            llms[llm_family][llm]["sem"] = scorer.sem(PPL_A_and_B, labels)
    return llms


def plot_acc_boost(ax, use_human_abstract):
    """
    fig1: barplot of pretrained vs finetuned
    """
    llms = get_llm_accuracies(use_human_abstract)

    # llms
    all_llm_params = []
    for llm_family in llms.keys():
        for llm in llms[llm_family]:
            all_llm_params.append(llms[llm_family][llm]["n_params"])
    max_n_params = max(all_llm_params)

    all_llm_accuracies = []
    all_llm_sems = []
    all_llm_names = []
    all_llm_colors = []
    all_llm_radius = []
    all_llm_xticks = [1, 2]

    for family_index, llm_family in enumerate(llms.keys()):
        for llm in llms[llm_family]:
            all_llm_accuracies.append(llms[llm_family][llm]["acc"])
            all_llm_sems.append(llms[llm_family][llm]["sem"])
            all_llm_names.append(llms[llm_family][llm]["llm"])
            all_llm_colors.append(llms[llm_family][llm]["color"])
            all_llm_radius.append(
                500 * \
                plt.rcParams['lines.markersize'] / max_n_params * llms[llm_family][llm]["n_params"]
            )

    # Barplot
    ax.bar(
        all_llm_xticks, all_llm_accuracies,
        # yerr=all_llm_sems,
        color=all_llm_colors,
        hatch=['/', '*'],
        alpha=0.4,
        width=0.5,
        capsize=3,
    )

    # Add annotations
    # Text improvement in acc (+xxx%) on the second bar
    for i, acc in enumerate(all_llm_accuracies):
        ax.annotate(
            f"{acc:.2%}",
            xy=(all_llm_xticks[i], acc),
            ha='center',
            va='bottom',
            fontsize=12,
            color='k',
        )

    ax.set_xlabel("Mistral-7B-v0.1", fontweight='normal')
    ax.set_ylabel("Accuracy", fontweight='normal')
    ax.set_xticks([0, 1, 2, 3])
    ax.set_xticklabels(["", "Pre-trained  ", "   Fine-tuned", ""])
    ax.set_ylim([0.5, 1])
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.text(
        -0.1, 1.15, "A", 
        fontsize=20, fontweight='bold', 
        transform=ax.transAxes
    )
    ax.grid(axis='y', linestyle='--', alpha=0.6)


def plot_ppl_diff(
        ax,
        pretrained_dir,
        finetuned_dir,
        use_human_abstract,
    ):
    """
    Plot:
        Histogram of pretrained correct PPL and fineutned correct PPL
    """
    if use_human_abstract:
        pretrained_dir += "/human_abstracts"
        finetuned_dir += "/human_abstracts"
    else:
        pretrained_dir += "/llm_abstracts"
        finetuned_dir += "/llm_abstracts"

    pretrained_ppl_fpath = pretrained_dir + "/PPL_A_and_B.npy"
    finetuned_ppl_fpath = finetuned_dir + "/PPL_A_and_B.npy"
    
    pretrained_labels_fpath = pretrained_dir + "/labels.npy"
    finetuned_labels_fpath = finetuned_dir + "/labels.npy"

    pretrained_PPL_A_and_B = np.load(pretrained_ppl_fpath)
    finetuned_PPL_A_and_B = np.load(finetuned_ppl_fpath)
    pretrained_labels = np.load(pretrained_labels_fpath)
    finetuned_labels = np.load(finetuned_labels_fpath)

    pretrained_PPL_A = pretrained_PPL_A_and_B[:, 0]
    pretrained_PPL_B = pretrained_PPL_A_and_B[:, 1]

    finetuned_PPL_A = finetuned_PPL_A_and_B[:, 0]
    finetuned_PPL_B = finetuned_PPL_A_and_B[:, 1]

    # plot
    pretrained_diff = []
    finetuned_diff = []
    pretrained_correct_PPL = []
    finetuned_correct_PPL = []
    for i in range(len(pretrained_labels)):
        if pretrained_labels[i] == 1:
            pretrained_diff.append(pretrained_PPL_B[i] - pretrained_PPL_A[i])
            pretrained_correct_PPL.append(pretrained_PPL_B[i])
        else:
            pretrained_diff.append(pretrained_PPL_A[i] - pretrained_PPL_B[i])
            pretrained_correct_PPL.append(pretrained_PPL_A[i])

        if finetuned_labels[i] == 1:
            finetuned_diff.append(finetuned_PPL_B[i] - finetuned_PPL_A[i])
            finetuned_correct_PPL.append(finetuned_PPL_B[i])
        else:
            finetuned_diff.append(finetuned_PPL_A[i] - finetuned_PPL_B[i])
            finetuned_correct_PPL.append(finetuned_PPL_A[i])

    pretrained_diff = np.array(pretrained_diff)
    finetuned_diff = np.array(finetuned_diff)
    pretrained_correct_PPL = np.array(pretrained_correct_PPL)
    finetuned_correct_PPL = np.array(finetuned_correct_PPL)

    # Sanity check, see if diff converts to accuracy correctly
    pretrained_acc = np.mean(pretrained_diff < 0)
    finetuned_acc = np.mean(finetuned_diff < 0)
    print(f"pretrained_acc: {pretrained_acc}, finetuned_acc: {finetuned_acc}")

    # paired t-test
    t_diff, p_diff = stats.ttest_rel(pretrained_diff, finetuned_diff)
    print(f"t_diff: {t_diff}, p_diff: {p_diff}")

    results = pg.ttest(pretrained_correct_PPL, finetuned_correct_PPL, paired=True)
    print(results)

    # Plot
    # Histogram of pretrained correct PPL and fineutned correct PPL
    sns.kdeplot(pretrained_correct_PPL, ax=ax, color='#8B9FC5', label='Pre-trained')
    sns.kdeplot(finetuned_correct_PPL, ax=ax, color='#5874DC', label='Fine-tuned')
    sns.histplot(
        pretrained_correct_PPL, 
        bins=20, 
        stat='density',
        ax=ax, 
        color='#8B9FC5', 
        alpha=0.3,
        linewidth=0.
    )
    sns.histplot(
        finetuned_correct_PPL, 
        bins=20, 
        stat='density',
        ax=ax, 
        color='#5874DC', 
        alpha=0.3,
        linewidth=0.
    )
    ax.set_xlabel("PPL of correct answer", fontweight='normal')
    ax.set_ylabel("Density", fontweight='normal')
    ax.legend(loc='upper right')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_major_locator(plt.MaxNLocator(3))
    ax.text(
        -0.1, 1.15, "B", 
        fontsize=20, fontweight='bold', 
        transform=ax.transAxes
    )


def plot(use_human_abstract):
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    # ax1: barplot of pretrained vs finetuned (acc boost)
    plot_acc_boost(
        ax=axes[0], 
        use_human_abstract=use_human_abstract
    )

    # ax2: histogram of pretrained correct PPL and fineutned correct PPL
    plot_ppl_diff(
        ax=axes[1],
        pretrained_dir=f"{model_results_dir}/mistralai--Mistral-7B-v0.1",
        finetuned_dir=f"{model_results_dir}/lora_r256_a512_finetune_mistral_7b_v01",
        use_human_abstract=use_human_abstract,
    )

    plt.tight_layout()
    plt.savefig("figs/finetuning_boost.pdf")

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--use_human_abstract", type=argparse_helper.str2bool, default=True)

    model_results_dir = "model_results"
    plot(use_human_abstract=parser.parse_args().use_human_abstract)