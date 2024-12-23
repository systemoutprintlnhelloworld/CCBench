# CCBench Reproducible Results Code (to be updated upon publication)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://www.apache.org/licenses/LICENSE-2.0)
[![Python Versions](https://img.shields.io/badge/Python-3.9--3.12-blue.svg)](#)

<div style="text-align: center; font-family: sans-serif; font-size: 60px; line-height: 1.4; color: #272a2e;">
    <p><em>"If I have seen further it is by standing on the shoulders of Giants."</em></p>
    <p><strong>Isaac Newton, 1675.</strong></p>
</div>

Raw results and plotting scripts for paper under review

### To work with this repo locally:
```
git clone git@github.com:systemoutprintlnhelloworld/CCBench.git --recursive
```
Collecting environment details

```markdown
# Paper Reproduction Code

This repository contains the code for reproducing all experiments and figures described in our paper. By running these scripts, you can replicate the datasets, evaluation procedures, and results used in the publication.
```
## Directory Structure

```bash
Repository: https://github.com/systemoutprintlnhelloworld/CCBench

(workspaces)
├─ 1.Dataset construct
│   ├─ extract image
│   │   ├─ download_image-v2.py
│   │   ├─ download_image-v3.py
│   │   └─ download&compare_img_in_excel.py
│   ├─ pipeline mainthread
│   └─ postprogress
├─ 2.Evaluation pipeline
│   ├─ QA
│   │   ├─ formatted
│   │   └─ pipeline
│   └─ VQA
├─ 3.Answer assessment
│   ├─ Close-ended
│   └─ Open-ended
├─ 4.Result statistics
│   ├─ Fig. 1
│   ├─ Fig. 4
│   ├─ Fig. 5
│   └─ Fig. 6
└─ LICENSE
   README.md
```

## Running Environment

```sh
pip install \
  pandas \
  openpyxl \
  tqdm \
  matplotlib \
  openai
```

## Dataset Construction

Before running the evaluation process, you need to construct the dataset first. Please run the following scripts:

```sh
python 1.Dataset construct/extract image/download_image-v2.py
python 1.Dataset construct/extract image/download_image-v3.py
python 1.Dataset construct/extract image/download&compare_img_in_excel.py
```

## Evaluation Process
In this section, each script corresponds to specific figures or tables in the paper. Running these scripts will generate necessary outputs to replicate the quantitative and qualitative results. Scripts may include:
- Data parsing or intermediate result generation
- Automatic metric computation
- Plot or table creation

Refer to the figure or table identifier in the paper to select the correct script to run, and confirm if additional parameters (e.g., --use_human_abstract) are required for your use case.

Run the corresponding evaluation scripts according to different figures and tables:


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

This project is licensed under the Apache License 2.0.

## Citation
If you use this repository in your work, please cite our paper:
```
[1] [Paper Title], Authors, Conference/Journal (Year).
```
