import os
import signal
import sys
import pandas as pd
from deepeval import evaluate
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
import colorama
from colorama import Fore, Back, Style
from tqdm import tqdm


def setup_environment(client):
    clients = {
        "chatfire": {
            "base": "",
            "key": ""
        },
        "ggb": {
            "base": "",
            "key": ""
        },
        "rikka": {
            "base": "",
            "key": ""
        },
        "openrouter": {
            "base": "",
            "key": ""
        },
    }
    while True:
        if client.lower() in clients:
            os.environ["OPENAI_API_BASE"] = clients[client.lower()]["base"]
            os.environ["openai_api_key"] = clients[client.lower()]["key"]
            break
        else:
            print(Fore.RED + "Invalid client selected!")
            print(Fore.CYAN + "若要退出,请按"+Fore.YELLOW+'Ctrl+C')
            client = input(Fore.RED + "Please select a valid client: ")



def initialize_metrics():
    correctness_metric = GEval(
        name="Correctness",
        criteria="Determine whether the actual output is factually correct and it and context  meets the comprehensive criteria:Accuracy,Detail,Logical, terms use, risk awareness, problem relevance, brevity  based on the expected output and input.",
        evaluation_steps=[ # 准确性和信息准确性
        "1. Check whether the ACTUAL OUTPUT matches the EXPECTED OUTPUT. Total score: 8 points.",
        "2. If the EXPECTED OUTPUT can be broken down into points, split it into `n` points starting from a base score of 1 point, with the remaining 7 points evenly distributed among all points.",
        "3. Deduct 0.5 points for each point in the ACTUAL OUTPUT that conflicts with the EXPECTED OUTPUT.",
        "4. If any point in the ACTUAL OUTPUT partially matches a point in the EXPECTED OUTPUT, deduct 0.5 points from the added points. If added points are less than deducted points, no points are added.",
        "5. If the EXPECTED OUTPUT requires only one line, break it down into multiple points for scoring.",
        
        # 详尽性和详细程度和解释 (衡量 context)
        "6. Assess the context based on personal knowledge for thoroughness and explanation, total score: 1 point.",
        "7. Each INPUT needs `n` points of explanation in the context, evenly distributing 1 point among all points.",
        "8. Incorrect explanations in the context do not count towards the score.",
        "9. Logical explanations in the context count towards the score, mere explanations of terms do not.",
        
        # 逻辑性和诊断推理
        "10. Evaluate the logical consistency and diagnostic reasoning in the ACTUAL OUTPUT and context, with a maximum deduction of 1 point.",
        "11. Deduct 0.5 points for each instance of logical inconsistency.",
        
        # 精确性和医学术语使用
        "12. Evaluate the precision and use of medical terminology in the ACTUAL OUTPUT, total score: 0.5 points.",
        
        # 风险意识 (衡量 ACTUAL OUTPUT)
        "13. Assess the awareness of potential risks or uncertainties in the ACTUAL OUTPUT, total score: 0.5 points.",
        "14. If the INPUT does not involve safety or pathological determination and is just a medical knowledge question, this criterion is not needed.",
        
        # 问题相关性
        "15. Evaluate the relevance of the ACTUAL OUTPUT to the INPUT, total score: 1 point.",
        "16. ACTUAL OUTPUTs that are off-topic score 0 points.",
        
        # 简洁和效率
        "17. Assess the conciseness and efficiency of the context, total score: 1 point.",
        "18. Compare the number of irrelevant details in each model's context.",
        "19. Compare the length of each sentence in the context, shorter is better.",
        "20. Rank the contexts, with the first place scoring 1 point, the second place scoring 0.6 points, and the third place scoring 0.2 points."
 ],
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT,
            LLMTestCaseParams.CONTEXT,
        ],
        # verbose_mode="True",
        model="gift-gpt-4o",
    )
    return correctness_metric


def evaluate_model(file_path, qa_df, correctness_metric, start_num=0, temp_file_result='temp_results.xlsx', temp_file_reason='temp_reasons.xlsx'):
    results_columns = ["Excel_line", "Model", "Question", "reply", "Correctness"]
    reasons_columns = ["Excel_line", "Model", "Question", "reason", "Correctness_reason"]

    results_df = pd.DataFrame(columns=results_columns)
    reasons_df = pd.DataFrame(columns=reasons_columns)

    model_name = file_path.split('\\')[-1].split('.')[0]
    model_df = pd.read_excel(file_path)

    for i in tqdm(range(start_num, len(qa_df)), desc="Evaluating Model", unit="question"):  # 修改此处
        # knowledge = qa_df.iloc[i, 1]
        question = qa_df.iloc[i, 2]
        correct_answer = qa_df.iloc[i, 3]
        model_answer = model_df.iloc[i, model_df.columns.str.contains('答案|回答')].values[0]
        model_reason = model_df.iloc[i, model_df.columns.str.contains('理由')].values[0]

        test_case = LLMTestCase(
            input=question,
            actual_output=model_answer,
            expected_output=correct_answer,
            context=list(str(model_reason)),
        )

        try:
            correctness_metric.measure(test_case)
            correctness_score = correctness_metric.score
            correctness_reason = correctness_metric.reason
        except Exception as e:
            print(f"An error occurred while measuring metric {correctness_metric.name}: {str(e)}")
            for _ in range(5):
                try:
                    correctness_metric.measure(test_case)
                    correctness_score = correctness_metric.score
                    correctness_reason = correctness_metric.reason
                    break
                except Exception as e:
                    print(f"Retrying... Error: {str(e)}")
            else:
                print(f"Failed to measure metric {correctness_metric.name} after 5 retries. Exiting.")
                # 保存文件
                results_df.to_excel(temp_file_result, index=False)
                reasons_df.to_excel(temp_file_reason, index=False)
                sys.exit(1)

        results_df = pd.concat([results_df, pd.DataFrame({
            "Excel_line": [i + 1],
            "Model": [model_name],
            "Question": [question],
            "reply": [model_answer],
            "Correctness": [correctness_score]
        })], ignore_index=True)

        reasons_df = pd.concat([reasons_df, pd.DataFrame({
            "Excel_line": [i + 1],
            "Model": [model_name],
            "Question": [question],
            "reason": [model_reason],
            "Correctness_reason": [correctness_reason]
        })], ignore_index=True)
        
        print('当前excel行数:', i + 1)
        results_df.to_excel(temp_file_result, index=False)
        reasons_df.to_excel(temp_file_reason, index=False)

    return results_df, reasons_df

def print_results(start_num, model_name, question, correctness_score,knowledge,reason,answer):
    colorama.init(autoreset=True)
    print(Fore.GREEN + "Excel_line: ", Fore.RED + str(start_num + 1))
    print(Fore.GREEN + "Model: ", Fore.RED + model_name)
    print(Fore.GREEN + "Knowledge: ", Fore.RED + knowledge)
    print(Fore.GREEN + "Question: ", Fore.RED + question)
    print(Fore.GREEN + "Answer: ", Fore.RED + answer)
    print(Fore.GREEN + "Reason: ", Fore.RED + reason)
    print(Fore.GREEN + "Correctness: ", Fore.RED + str(correctness_score))
    print(Style.RESET_ALL)


def save_final_results(results_df, reasons_df, final_file, reason_file):
    if os.path.exists(reason_file):
        final_reasons_df = pd.read_excel(reason_file)
        final_reasons_df = pd.concat(
            [final_reasons_df, reasons_df], ignore_index=True)
    else:
        final_reasons_df = reasons_df

    final_reasons_df.to_excel(reason_file, index=False)

    if os.path.exists(final_file):
        final_results_df = pd.read_excel(final_file)
        final_results_df = pd.concat(
            [final_results_df, results_df], ignore_index=True)
    else:
        final_results_df = results_df

    final_results_df.to_excel(final_file, index=False)


def signal_handler(sig, frame):
    print(Fore.RED + "Exiting...")
    # 保存当前temp_results.xlsx和temp_reasons.xlsx到final_results.xlsx和reasons.xlsx
    results_df = pd.read_excel(temp_file_result)
    reasons_df = pd.read_excel(temp_file_reason)
    save_final_results(results_df, reasons_df, final_file, reason_file)

    
    sys.exit(0)

def main():
    global temp_file_result, temp_file_reason, final_file, reason_file  # 确保全局变量在 main 中使用
    base = input(Fore.RED + "请选择Client" + Fore.GREEN +
                 "(chatfire/ggb/rikka/openrouter): ")
    setup_environment(base)

    questions_file = r"D:\研究生\任务3\题库\QA\最终题库\open\open_qa.xlsx"
    qa_df = pd.read_excel(questions_file)

    # 临时文件
    temp_file_result = r"D:\研究生\任务3\测试结果\QA\temp_results.xlsx"
    temp_file_reason = r"D:\研究生\任务3\测试结果\QA\temp_reasons.xlsx"
    
    file_paths = [
        # r"D:\研究生\任务3\测试结果\QA\open\llama2.xlsx",
        # r"D:\研究生\任务3\测试结果\QA\open\通义千问.xlsx",
        # r"D:\研究生\任务3\测试结果\QA\open\文心一言.xlsx",
        # r"D:\研究生\任务3\测试结果\QA\open\bard.xlsx",
        # r"D:\研究生\任务3\测试结果\QA\open\cluade2.xlsx",
        r"D:\研究生\任务3\测试结果\QA\open\gpt-4.xlsx"
    ]

    final_file = r'D:\研究生\任务3\测试结果\QA\评估结果.xlsx'
    reason_file = r'D:\研究生\任务3\测试结果\QA\reason.xlsx'

    correctness_metric = initialize_metrics()

    # 循环相关
    # start_num = 23
    start_num = 281
    
    first_iteration = True  # 标志位，表示是否是内圈的第一次迭代
    
    #  设置信号处理函数
    signal.signal(signal.SIGINT, signal_handler)

    for file_path in file_paths:
        if first_iteration:
           first_iteration=False
        elif not first_iteration:
            start_num = 0
            
        results_df, reasons_df = evaluate_model(
            file_path, qa_df, correctness_metric,start_num,temp_file_result,temp_file_reason)
        save_final_results(results_df, reasons_df, final_file, reason_file)


if __name__ == "__main__":
    main()
