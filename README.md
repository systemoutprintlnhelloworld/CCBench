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
Collecting workspace information

```markdown
# Paper Reproduction Code

This is the reproduction code repository for the paper, including code for dataset construction, evaluation process, answer assessment, and result statistics. By running these codes, you can reproduce the conclusions and charts in the paper.

## Directory Structure

```
.gitignore
.vscode/
	settings.json
1.Dataset construct/
	extract image/
		download_image-v2.py
		download_image-v3.py
		download&compare_img_in_excel.py
	pipeline mainthread/
		

assistgram_qa.py


		

assistgram.py


		

ChimeraGPT-qa.py


		

ChimeraGPT-vqa.py


	postprogress/
		excel-rename.py
		rename-v2-webexclusive.py
		...
2.Evaluation pipeline/
	QA/
		formatted/
		pipeline/
	VQA/
3.Answer assessment/
	Close-ended/
	Open-ended/
4.Result statistics/
	Fig. 1/
	Fig. 4/
	Fig. 5/
	Fig. 6/
LICENSE


README.md


```

## Running Environment

Please ensure that the following dependencies are installed in your environment:

- Python 3.x
- pandas
- openpyxl
- tqdm
- matplotlib
- openai

You can install the required dependencies using the following command:

```sh
pip install pandas openpyxl tqdm matplotlib openai
```

## Dataset Construction

Before running the evaluation process, you need to construct the dataset first. Please run the following scripts:

```sh
python 1.Dataset construct/extract image/download_image-v2.py
python 1.Dataset construct/extract image/download_image-v3.py
python 1.Dataset construct/extract image/download&compare_img_in_excel.py
```

## Evaluation Process

Run the corresponding evaluation scripts according to different figures and tables:

- Figure 3A | Figure S20: `python 2.Evaluation 

test-gpt4.py

 --use_human_abstract <True|False>`
- Figure 3B | Figure S5 | Figure S21 | Figure S23: `python 2.Evaluation 

test-bard.py

 --use_human_abstract <True|False>`
- Figure 3C | Figure S22: `python 2.Evaluation 

test-llama2.py

 --use_human_abstract <True|False>`
- Figure 4 | Figure S25 | Table S3: `python 2.Evaluation 

test-claude2.py

 --use_human_abstract <True|False>`
- Figure 5: `python 4.Result statistics/Fig. 5/create_diff_table_is-qa.py`
- Figure S3: `python 2.Evaluation pipeline/QA/pipeline/test-qianwen.py`
- Figure S4: `python 2.Evaluation pipeline/QA/pipeline/test-wenxin.py`
- Figure S6 | Figure S24: `python 2.Evaluation pipeline/QA/pipeline/test-gpt4.py`
- Figure S7: `python 2.Evaluation pipeline/QA/pipeline/test-bard.py`
- Figure S8: `python 2.Evaluation pipeline/QA/pipeline/test-llama2.py`
- Figure S17 | Figure S18: `python 2.Evaluation pipeline/QA/pipeline/test-claude2.py`

## Answer Assessment

Run the following scripts for answer assessment:

```sh
python 3.Answer assessment/Close-ended/evaluate_close_ended.py
python 3.Answer assessment/Open-ended/evaluate_open_ended.py
```

## Result Statistics

Run the corresponding result statistics scripts according to different figures and tables:

```sh
python 4.Result statistics/Fig. 1/plot_fig1.py
python 4.Result statistics/Fig. 4/plot_fig4.py
python 4.Result statistics/Fig. 5/plot_fig5.py
python 4.Result statistics/Fig. 6/plot_fig6.py
```

## License

This project is licensed under the MIT License.
```

### Attribution(fix after publish)
```
```
