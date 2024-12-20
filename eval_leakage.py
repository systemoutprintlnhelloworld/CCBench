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
        PPL_refinedweb=[], 
        ZLIB_refinedweb=[],
        PPL_arxiv_after=[],
        ZLIB_arxiv_after=[],
        PPL_arxiv_before=[],
        ZLIB_arxiv_before=[],
        PPL_biorxiv_after=[],
        ZLIB_biorxiv_after=[],
        PPL_biorxiv_before=[],
        ZLIB_biorxiv_before=[],
        PPL_gettysburg=[],
        ZLIB_gettysburg=[],
    ):
    """
    ref: Fig 3 (https://arxiv.org/abs/2012.07805)

    x-axis: PPL
    y-axis: zlib entropy
    """
    marker_size = plt.rcParams['lines.markersize'] * 20
    correct_PPL = _correct_ppl(PPL_A_and_B, labels)
    correct_ZLIB = _correct_zlib(ZLIB_A_and_B, labels)

    if "falcon" in llm.lower():
        ax.scatter(
            PPL_refinedweb, 
            ZLIB_refinedweb, 
            alpha=0.5, 
            label='RefinedWeb',
            color='grey',
            s=marker_size,
            edgecolor=None,
        )

    if "galactica" in llm.lower() or "llama" in llm.lower():
        ax.scatter(
            PPL_arxiv_before,
            ZLIB_arxiv_before,
            alpha=0.5,
            label='Arxiv (Jun-Dec 2021)',
            color='green',
            s=marker_size,
            edgecolor=None,
        )

        ax.scatter(
            PPL_arxiv_after,
            ZLIB_arxiv_after,
            alpha=1,
            label='Arxiv (Jun-Dec 2023)',
            color='cyan',
            s=marker_size,
            marker='x',
            edgecolor=None,
        )

        if "galactica" in llm.lower():
            ax.scatter(
                PPL_biorxiv_before, 
                ZLIB_biorxiv_before, 
                alpha=0.5, 
                label='Biorxiv (Jun-Dec 2021)',
                color='orange',
                s=marker_size,
                edgecolor=None,
            )

            ax.scatter(
                PPL_biorxiv_after, 
                ZLIB_biorxiv_after, 
                alpha=1, 
                label='Biorxiv (Jun-Dec 2023)',
                color='k',
                marker='x',
                s=marker_size,
                edgecolor=None,
            )
        # ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.4))

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

    ax.scatter(
        PPL_gettysburg, 
        ZLIB_gettysburg, 
        alpha=1, 
        label=f"Gettysburg Address",
        marker='^',
        s=marker_size*1.5,
        edgecolor=None,
        color='red'
    )

    if llm == "tiiuae/falcon-180B":
        llm_name = "Falcon-180B"
    elif llm == "meta-llama/Llama-2-70b-hf":
        llm_name = "Llama-2-70B"
    elif llm == "facebook/galactica-120b":
        llm_name = "Galactica-120B"

    ax.set_title(llm_name)
    ax.set_xlabel("PPL")
    ax.set_ylabel("ZLIB entropy")
    ax.set_xscale('log')
    ax.set_xlim(1, 200)
    ax.set_ylim(0, 1500)
    ax.legend(loc='upper right')
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

        if "falcon" in llm.lower():
            PPL_refinedweb = np.load(f"{model_results_dir}/{llm.replace('/', '--')}/refinedweb/PPL.npy")
            ZLIB_refinedweb = np.load(f"{model_results_dir}/{llm.replace('/', '--')}/refinedweb/ZLIB.npy")
        else:
            PPL_refinedweb = []
            ZLIB_refinedweb = []
        
        if "galactica" in llm.lower() or "llama" in llm.lower():
            PPL_arxiv_after = np.load(f"{model_results_dir}/{llm.replace('/', '--')}/arxiv_abstracts_20230601_20231231/PPL.npy")
            ZLIB_arxiv_after = np.load(f"{model_results_dir}/{llm.replace('/', '--')}/arxiv_abstracts_20230601_20231231/ZLIB.npy")
            PPL_arxiv_before = np.load(f"{model_results_dir}/{llm.replace('/', '--')}/arxiv_abstracts_20210601_20211231/PPL.npy")
            ZLIB_arxiv_before = np.load(f"{model_results_dir}/{llm.replace('/', '--')}/arxiv_abstracts_20210601_20211231/ZLIB.npy")
        else:
            PPL_arxiv_after = []
            ZLIB_arxiv_after = []
            PPL_arxiv_before = []
            ZLIB_arxiv_before = []

        if "galactica" in llm.lower():
            PPL_biorxiv_after = np.load(f"{model_results_dir}/{llm.replace('/', '--')}/biorxiv_abstracts_2023-06-01_2023-12-01/PPL.npy")
            ZLIB_biorxiv_after = np.load(f"{model_results_dir}/{llm.replace('/', '--')}/biorxiv_abstracts_2023-06-01_2023-12-01/ZLIB.npy")
            PPL_biorxiv_before = np.load(f"{model_results_dir}/{llm.replace('/', '--')}/biorxiv_abstracts_2021-06-01_2021-12-01/PPL.npy")
            ZLIB_biorxiv_before = np.load(f"{model_results_dir}/{llm.replace('/', '--')}/biorxiv_abstracts_2021-06-01_2021-12-01/ZLIB.npy")
        else:
            PPL_biorxiv_after = []
            ZLIB_biorxiv_after = []
            PPL_biorxiv_before = []
            ZLIB_biorxiv_before = []

        PPL_gettysburg = np.load(f"{model_results_dir}/{llm.replace('/', '--')}/gettysburg_address/PPL.npy")
        ZLIB_gettysburg = np.load(f"{model_results_dir}/{llm.replace('/', '--')}/gettysburg_address/ZLIB.npy")

        ax = axes[i]
        if i != 0:
            ax.get_yaxis().set_visible(False)

        if metric == "ppl_vs_zlib":
            _plot_correct_ppl_vs_zlib(
                PPL_A_and_B, ZLIB_A_and_B, labels, llm, ax, 
                PPL_refinedweb, ZLIB_refinedweb, 
                PPL_arxiv_after, ZLIB_arxiv_after,
                PPL_arxiv_before, ZLIB_arxiv_before,
                PPL_biorxiv_after, ZLIB_biorxiv_after,
                PPL_biorxiv_before, ZLIB_biorxiv_before,
                PPL_gettysburg, ZLIB_gettysburg,
            )
        else:
            raise NotImplementedError(f"metric={metric}")

    # Save figure
    fname = f"{fig_dir}/group_{metric}"
    fig.subplots_adjust(bottom=0.8)
    plt.tight_layout()
    plt.savefig(f"{fname}_{type_of_abstract}.pdf")


if __name__ == "__main__":
    fig_dir = f"figs"
    if not os.path.exists(fig_dir):
        os.makedirs(fig_dir)

    llms = [
        "tiiuae/falcon-180B",
        "meta-llama/Llama-2-70b-hf",
        "facebook/galactica-120b",
    ]

    use_human_abstract = True
    type_of_abstract = 'human_abstracts'
    human_abstracts_fpath = "testcases/BrainBench_Human_v0.1.csv"
    PPL_fname = "PPL_A_and_B"
    label_fname = "labels"
    model_results_dir = "model_results"

    plot("ppl_vs_zlib")

