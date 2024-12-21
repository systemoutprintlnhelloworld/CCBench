# CCBench reproducible results code(fix after publish)
<div style="text-align: center; font-family: sans-serif; font-size: 60px; line-height: 1.4; color: #272a2e;">
    <p><em>"If I have seen further it is by standing on the shoulders of Giants."</em></p>
    <p><strong>Isaac Newton, 1675.</strong></p>
</div>


Raw results and plotting scripts for paper under review

### To work with this repo locally:
```
git clone git@github.com:systemoutprintlnhelloworld/CCBench.git --recursive
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
Please refer to this location - [https://github.com/systemoutprintlnhelloworld/CCBench/](https://github.com/systemoutprintlnhelloworld/CCBench/)
### To obtain model results:
Model perplexities on BrainBench testcases:
* For human created testcases, see `model_results/<model_name>/human_abstracts/PPL_A_and_B.npy`, which is a 2D numpy array, with shape `(num_testcases, 2)`, `PPL_A_and_B[i][0]` is the perplexity of the first abstract of the ith testcase.
* For GPT-4 created testcases, see `model_results/<model_name>/llm_abstracts/PPL_A_and_B.npy`
* For each testcase's ground truth, see `model_results/<model_name>/<human|llm_abstracts>/labels.npy`, which is a 1D numpy array, with shape `(num_testcases, )`. Specifically, `label=0` means the first abstract of this testcase is the correct answer, and `label=1` means the second abstract of the testcase is the correct answer.

### Attribution(fix after publish)
```
```
