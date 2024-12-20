# brainbench_results
Raw results and plotting scripts for paper [https://www.nature.com/articles/s41562-024-02046-9](https://www.nature.com/articles/s41562-024-02046-9)

### To work with this repo locally:
```
git clone git@github.com:braingpt-lovelab/brainbench_results.git --recursive
```

### To plot figures/tables in the paper:
* Figure 3A | Figure S20: `python overall_accuracy_model_vs_human.py --use_human_abstract <True|False>`
* Figure 3B | Figure S5 | Figure S21 | Figure S23: `python accuracy_by_subfields.py --use_human_abstract <True|False>`
* Figure 3C | Figure S22: `python accuracy_by_positions.py --use_human_abstract <True|False>`
* Figure 4 | Figure S25 | Table S3: `python calibration_machine_and_human.py --use_human_abstract <True|False>`
* Figure 5: `python finetuning_boost.py`
* Figure S3: `python iso_overall_accuracy_model_vs_human.py`
* Figure S4: `python swap_overall_accuracy_model_vs_human.py`
* Figure S6 | Figure S24: `python error_correlation_human_vs_machine.py`
* Figure S7: `python eval_leakage.py`
* Figure S8: `python accuracy_correlate_pubdate.py`
* Figure S17 | Figure S18: `python expertise_analyses.py`

### To obtain human results:
Please refer to the dedicated repo - [https://github.com/braingpt-lovelab/brainbench_participant_data/tree/main](https://github.com/braingpt-lovelab/brainbench_participant_data/tree/a819a1b3766abe4817b1ef81ebe7a0a7a351aa99)

### To obtain model results:
Model perplexities on BrainBench testcases:
* For human created testcases, see `model_results/<model_name>/human_abstracts/PPL_A_and_B.npy`, which is a 2D numpy array, with shape `(num_testcases, 2)`, `PPL_A_and_B[i][0]` is the perplexity of the first abstract of the ith testcase.
* For GPT-4 created testcases, see `model_results/<model_name>/llm_abstracts/PPL_A_and_B.npy`
* For each testcase's ground truth, see `model_results/<model_name>/<human|llm_abstracts>/labels.npy`, which is a 1D numpy array, with shape `(num_testcases, )`. Specifically, `label=0` means the first abstract of this testcase is the correct answer, and `label=1` means the second abstract of the testcase is the correct answer.

### Attribution
```
@article{luo_large_2024,
	title = {Large language models surpass human experts in predicting neuroscience results},
	issn = {2397-3374},
	url = {https://www.nature.com/articles/s41562-024-02046-9},
	doi = {10.1038/s41562-024-02046-9},
	abstract = {Abstract
            Scientific discoveries often hinge on synthesizing decades of research, a task that potentially outstrips human information processing capacities. Large language models (LLMs) offer a solution. LLMs trained on the vast scientific literature could potentially integrate noisy yet interrelated findings to forecast novel results better than human experts. Here, to evaluate this possibility, we created BrainBench, a forward-looking benchmark for predicting neuroscience results. We find that LLMs surpass experts in predicting experimental outcomes. BrainGPT, an LLM we tuned on the neuroscience literature, performed better yet. Like human experts, when LLMs indicated high confidence in their predictions, their responses were more likely to be correct, which presages a future where LLMs assist humans in making discoveries. Our approach is not neuroscience specific and is transferable to other knowledge-intensive endeavours.},
	language = {en},
	urldate = {2024-11-29},
	journal = {Nature Human Behaviour},
	author = {Luo, Xiaoliang and Rechardt, Akilles and Sun, Guangzhi and Nejad, Kevin K. and Yáñez, Felipe and Yilmaz, Bati and Lee, Kangjoo and Cohen, Alexandra O. and Borghesani, Valentina and Pashkov, Anton and Marinazzo, Daniele and Nicholas, Jonathan and Salatiello, Alessandro and Sucholutsky, Ilia and Minervini, Pasquale and Razavi, Sepehr and Rocca, Roberta and Yusifov, Elkhan and Okalova, Tereza and Gu, Nianlong and Ferianc, Martin and Khona, Mikail and Patil, Kaustubh R. and Lee, Pui-Shee and Mata, Rui and Myers, Nicholas E. and Bizley, Jennifer K. and Musslick, Sebastian and Bilgin, Isil Poyraz and Niso, Guiomar and Ales, Justin M. and Gaebler, Michael and Ratan Murty, N. Apurva and Loued-Khenissi, Leyla and Behler, Anna and Hall, Chloe M. and Dafflon, Jessica and Bao, Sherry Dongqi and Love, Bradley C.},
	month = nov,
	year = {2024},
}
```
