import os
import requests
import scipy
import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
plt.rcParams.update({"font.size": 16, "font.weight": "bold"})


def get_publication_date(doi):
    api_url = f"https://api.crossref.org/works/{doi}"
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        # The publication date can be found within the 'published-print' or 'published-online' fields
        publication_info = data.get('message', {}).get('published-print') or data.get('message', {}).get('published-online')
        if publication_info:
            date_parts = publication_info['date-parts'][0]
            return "-".join(map(str, date_parts))  # Format: YYYY-MM-DD
        else:
            return "Publication date not found"
    else:
        return "Failed to retrieve data"


def ppl_incorrect_correct_by_pubdate(rank_method):
    """
    Plot the PPL difference (incorrect-correct) against publication date (earliest to latest)
    """
    # Load dataset
    df = pd.read_csv(human_abstracts_fpath)
    
    if not os.path.exists(f"data/publication_dates_{type_of_abstract}.npy"):
        dois = df["doi"].values

        pub_dates = []
        for doi in dois:
            pub_date = get_publication_date(doi)
            print(pub_date)
            pub_dates.append(pub_date)

        assert len(pub_dates) == len(dois)
        # save the publication dates to a file
        np.save(f"data/publication_dates_{type_of_abstract}.npy", pub_dates)
    else:
        pub_dates = np.load(f"data/publication_dates_{type_of_abstract}.npy")

    # pub_date follows year-month-day format, as string
    # convert to datetime object (adding zeros in order to sort properly)
    pub_dates_added_zeros = pd.to_datetime(pub_dates)

    # sort to get rank of publication date (earliest to latest)
    # ties aware method is used to handle ties
    pubdates_ranks = scipy.stats.rankdata(pub_dates_added_zeros, method=rank_method)
    
    fig, axes = plt.subplots(1, len(llms), figsize=(15, 5))
    for llm_index, llm in enumerate(llms):
        results_dir = f"{model_results_dir}/{llm.replace('/', '--')}/{type_of_abstract}"
        PPL_fname = "PPL_A_and_B"
        label_fname = "labels"
        PPL_A_and_B = np.load(f"{results_dir}/{PPL_fname}.npy")
        labels = np.load(f"{results_dir}/{label_fname}.npy")

        # iterate labels, to get the PPL difference (incorrect-correct)
        # if label=0, PPL_A is original, get PPL_B-PPL_A
        # if label=1, PPL_B is original, get PPL_A-PPL_B
        PPL_incorrect_correct = []
        indicator_colors = []
        for i, label in enumerate(labels):
            if label == 0:
                PPL_incorrect_correct.append(PPL_A_and_B[i][1] - PPL_A_and_B[i][0])
                if PPL_A_and_B[i][1] - PPL_A_and_B[i][0] > 0:
                    indicator_colors.append('b')
                else:
                    indicator_colors.append('grey')
            else:
                PPL_incorrect_correct.append(PPL_A_and_B[i][0] - PPL_A_and_B[i][1])
                if PPL_A_and_B[i][0] - PPL_A_and_B[i][1] > 0:
                    indicator_colors.append('b')
                else:
                    indicator_colors.append('grey')
        
        # Plot the PPL difference against publication date (indices)
        # set legend_labels so color g is correct, r is incorrect
        axes[llm_index].scatter(
            pubdates_ranks,
            PPL_incorrect_correct,
            c=indicator_colors,
            alpha=0.5,
            s=plt.rcParams["lines.markersize"] ** 2,
        )

        # Plot a regression line
        slope, intercept, r_value, p_value, std_err = stats.linregress(pubdates_ranks, PPL_incorrect_correct)
        y_line = slope * pubdates_ranks + intercept
        axes[llm_index].plot(
            pubdates_ranks,
            y_line,
            'k',
            label='fitted line',
            linewidth=plt.rcParams['lines.linewidth'] * 4,
        )
        axes[llm_index].plot(
            pubdates_ranks,
            y_line,
            'yellow',
            label='fitted line',
            linewidth=plt.rcParams['lines.linewidth'] * 2,
        )

        # Calculate the correlation between PPL difference and publication date
        # pub dates are ranks (earliest to latest)
        # PPL differences are ranks of the corresponding pub dates
        ppl_diff_ranks = scipy.stats.rankdata(PPL_incorrect_correct, method=rank_method)
        corr, p = stats.spearmanr(
            pubdates_ranks,
            ppl_diff_ranks
        )
        print(f"{llm}: correlation={corr:.3f}, p={p:.3f}")
        axes[llm_index].set_title(f"{llm_names[llm]}")
        axes[llm_index].set_xlabel("Publication date")
        axes[llm_index].set_ylabel("Test case difficulty\n(PPL difference)")
        axes[llm_index].spines["top"].set_visible(False)
        axes[llm_index].spines["right"].set_visible(False)
        # Set xticks to be publication date (only the first and last tick)
        axes[llm_index].set_xticks([0, len(PPL_incorrect_correct) - 1])
        axes[llm_index].set_xticklabels(["Early", "Late"])
        # Set yticks to be PPL difference (only the first and last tick)
        axes[llm_index].set_yticks([min(PPL_incorrect_correct), max(PPL_incorrect_correct)])
        axes[llm_index].set_yticklabels(["Hard", "Easy"])
    
    plt.tight_layout()
    plt.savefig(f"figs/accuracy_correlate_pubdate_{type_of_abstract}.pdf")
        

if __name__ == "__main__":
    llms = [
        "tiiuae/falcon-180B",
        "meta-llama/Llama-2-70b-hf",
        "facebook/galactica-120b",
    ]

    llm_names = {
        "tiiuae/falcon-180B": "Falcon-180B",
        "meta-llama/Llama-2-70b-hf": "Llama-2-70B",
        "facebook/galactica-120b": "Galactica-120B",
    }

    type_of_abstract = 'human_abstracts'
    human_abstracts_fpath = "testcases/BrainBench_Human_v0.1.csv"
    model_results_dir = "model_results"

    ppl_incorrect_correct_by_pubdate(rank_method="average")