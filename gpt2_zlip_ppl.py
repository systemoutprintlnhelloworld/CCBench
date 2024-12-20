import os
import zlib
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 16, 'font.weight': 'bold'})


def _correct_zlib(ZLIB_A_and_B, labels):
    """
    Collect the zlib scores for the correct answer.
    If labels[i] == 0, then we collect ZLIB_A_and_B[i, 0]
    If labels[i] == 1, then we collect ZLIB_A_and_B[i, 1]

    Args:
        ZLIB_A_and_B (np.ndarray): shape (num_samples, 2)
        labels (np.ndarray): shape (num_samples,)
    """
    correct_ZLIB = []
    for i, label in enumerate(labels):
        if label == 0:
            correct_ZLIB.append(ZLIB_A_and_B[i, 0])
        elif label == 1:
            correct_ZLIB.append(ZLIB_A_and_B[i, 1])
        else:
            raise ValueError(f"Unexpected label: {label}")
    return np.array(correct_ZLIB)


def _correct_ppl(PPL_A_and_B, labels):
    """
    Collect the perplexity scores for the correct answer.
    If labels[i] == 0, then we collect PPL_A_and_B[i, 0]
    If labels[i] == 1, then we collect PPL_A_and_B[i, 1]

    Args:
        PPL_A_and_B (np.ndarray): shape (num_samples, 2)
        labels (np.ndarray): shape (num_samples,)
    """
    correct_PPL = []
    for i, label in enumerate(labels):
        if label == 0:
            correct_PPL.append(PPL_A_and_B[i, 0])
        elif label == 1:
            correct_PPL.append(PPL_A_and_B[i, 1])
        else:
            raise ValueError(f"Unexpected label: {label}")
    return np.array(correct_PPL)


def _plot_correct_ppl_vs_zlib(
        PPL_A_and_B, ZLIB_A_and_B, labels, llm, ax, 
        PPL_j_of_neuro, ZLIB_j_of_neuro
    ):
    """
    x-axis: PPL
    y-axis: zlib entropy
    """
    marker_size = plt.rcParams['lines.markersize'] * 20
    correct_PPL = _correct_ppl(PPL_A_and_B, labels)
    correct_ZLIB = _correct_zlib(ZLIB_A_and_B, labels)

    ax.scatter(
        PPL_j_of_neuro,
        ZLIB_j_of_neuro,
        alpha=0.5,
        label='Journal of Neuroscience\n(2017-2022)',
        color='green',
        s=marker_size,
        edgecolor=None,
    )
    
    ax.scatter(
        correct_PPL, 
        correct_ZLIB, 
        alpha=1, 
        label=f"BrainBench",
        marker='^',
        s=marker_size,
        edgecolor=None,
        color='purple'
    )

    if llm == "gpt2":
        llm_name = "GPT-2 (pretrained)"

    elif llm == "finetune_gpt2":
        llm_name = "GPT-2 (finetuned)"

    elif llm == "gpt2_scratch_neuro_tokenizer":
        llm_name = "GPT-2 (scratch + neuro tokenizer)"

    ax.set_title(llm_name)
    ax.set_xlabel("PPL")
    ax.set_ylabel("ZLIB entropy")
    ax.set_xscale('log')
    ax.set_xlim(1, 200)
    ax.set_ylim(0, 1500)
    ax.legend(loc='lower left')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    

def plot(metric):
    n_rows = 1
    n_cols = len(llms) // n_rows
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 8))
    for i, llm in enumerate(llms):
        print(f'llm={llm}')
        results_dir = f"{model_results_dir}/{llm.replace('/', '--')}/{type_of_abstract}"
        PPL_A_and_B = np.load(f"{results_dir}/{PPL_fname}.npy")
        ZLIB_A_and_B = np.load(f"{results_dir}/ZLIB_A_and_B.npy")
        labels = np.load(f"{results_dir}/{label_fname}.npy")

        PPL_j_of_neuro = np.load(f"{model_results_dir}/{llm.replace('/', '--')}/j_of_neuro/PPL.npy")
        ZLIB_j_of_neuro = np.load(f"{model_results_dir}/{llm.replace('/', '--')}/j_of_neuro/ZLIB.npy")

        ax = axes[i]
        if i != 0:
            ax.get_yaxis().set_visible(False)

        if metric == "ppl_vs_zlib":
            _plot_correct_ppl_vs_zlib(
                PPL_A_and_B, ZLIB_A_and_B, labels, llm, ax,
                PPL_j_of_neuro, ZLIB_j_of_neuro
            )
        else:
            raise NotImplementedError(f"metric={metric}")

    # Save figure
    fname = f"{fig_dir}/gpt2_{metric}"
    fig.subplots_adjust(bottom=0.8)
    plt.tight_layout()
    plt.savefig(f"{fname}_{type_of_abstract}.pdf")


if __name__ == "__main__":
    fig_dir = f"figs"
    if not os.path.exists(fig_dir):
        os.makedirs(fig_dir)

    llms = [
        "gpt2",
        "finetune_gpt2",
        "gpt2_scratch_neuro_tokenizer"
    ]

    use_human_abstract = True
    type_of_abstract = 'human_abstracts'
    human_abstracts_fpath = "testcases/BrainBench_Human_v0.1.csv"
    PPL_fname = "PPL_A_and_B"
    label_fname = "labels"
    model_results_dir = "model_results"

    plot("ppl_vs_zlib")

