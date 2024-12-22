import json
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
            "base": "https://api.chatfire.cn/v1/",
            "key": "sk-0XHqwY0ob7ZB6jSy4227555b3e7647F9A40eC3080556E293"
        },
        "ggb": {
            "base": "https://noapi.ggb.today/v1/",
            "key": "sk-zOyNWjCI7Q9cbvlIC9072115B85a4130A2E870895f7cCdCc"
        },
        "rikka": {
            "base": "https://api.rikka.love/v1/",
            "key": "sk-9nrJyr2eXLhhmUvr35780c2b4fEf4aC18958E6FfD37c2eE7"
        },
        "openrouter": {
            "base": "https://openrouter.ai/api/v1/",
            "key": "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"
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
        criteria="Determine whether the result content in actual output is factually correct and it and reason content  in ACTUAL OUTPUT   meets the comprehensive criteria:Accuracy,Detail,Logical, terms use, risk awareness, problem relevance, brevity  based on the expected output and input.",
        evaluation_steps=[  # 准确性和信息准确性 (评价ACTUAL_OUTPUT中的result content)
            "1. Check whether the result content in the ACTUAL_OUTPUT matches the EXPECTED_OUTPUT. Total score: 80 points.",
            "2. If the EXPECTED_OUTPUT can be broken down into points, split it into `n` points starting from a base score of 10 points, with the remaining 70 points evenly distributed among all points.",
            "3. Deduct 2.5 points for each point in the result content that conflicts with the EXPECTED_OUTPUT.",
            "4. If any point in the result content partially matches a point in the EXPECTED_OUTPUT, deduct 2.5 points from the added points. If added points are less than deducted points, no points are added.",
            "5. If the EXPECTED_OUTPUT is short, break it down into multiple points for scoring.",

            # 详尽性和详细程度和解释 (评价ACTUAL_OUTPUT中的reasoning content)
            "6. Assess the reasoning content in ACTUAL_OUTPUT  based on personal knowledge for thoroughness and explanation, total score: 10 points.",
            "7. Each INPUT needs `n` points of explanation in the reasoning content in ACTUAL_OUTPUT  , evenly distributing 10 points among all points.",
            "8. Incorrect explanations in the reasoning content in ACTUAL_OUTPUT  do not count towards the score.",
            "9. Logical explanations in the reasoning content in ACTUAL_OUTPUT  count towards the score, mere explanations of terms do not.",

            # 逻辑性和诊断推理 (评价ACTUAL_OUTPUT中的result content)
            "10. Evaluate the logical consistency and diagnostic reasoning in the result content and reasoning content in ACTUAL_OUTPUT , with a maximum deduction of 10 points.",
            "11. Deduct 5 points for each instance of logical inconsistency.",

            # 精确性和医学术语使用 (评价ACTUAL_OUTPUT中的result content)
            "12. Evaluate the precision and use of medical terminology in the result content in ACTUAL_OUTPUT , total score: 5 points.",

            # 风险意识 (评价ACTUAL_OUTPUT中的result content)
            "13. Assess the awareness of potential risks or uncertainties in the result content in ACTUAL_OUTPUT , total score: 5 points.",
            "14. If the INPUT does not involve safety or pathological determination and is just a medical knowledge question, this criterion is not needed.",

            # 问题相关性 (评价ACTUAL_OUTPUT中的result content)
            "15. Evaluate the relevance of the result content in ACTUAL_OUTPUT  to the INPUT, total score: 100 points.",
            "16. Results that are off-topic score 0 points.",
            "17. Partially relevant results score proportionally based on how well they address the specific area indicated in the INPUT.",

            # 简洁和效率 (评价ACTUAL_OUTPUT中的reasoning content)
            "18. Assess the conciseness and efficiency of the reasoning content in ACTUAL_OUTPUT , total score: 10 points.",
            "19. Compare the number of irrelevant details in each model's reasoning content in ACTUAL_OUTPUT .",
            "20. Compare the length of each sentence in the reasoning content in ACTUAL_OUTPUT , shorter is better.",
            "21. Rank the reasonings, with the first place scoring 10 points, the second place scoring 6 points, and the third place scoring 2 points."
        ],
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT,
        ],
        # verbose_mode="True",
        model="gpt-4o-2024-08-06",
    )
    return correctness_metric


def read_josnl(json_path):
    with open(json_path, 'r', encoding='utf-8') as file:
        data = [json.loads(line.strip()) for line in file]
    return data


def evaluate_model(file_path, qa_df, correctness_metric, start_num=0, end_num=None, temp_file_result='temp_results_sx.xlsx', temp_file_reason='temp_reasons_sx.xlsx'):
    results_columns = ["Excel_line", "image", "Model",
                       "Question", "reply", "Correctness"]
    reasons_columns = ["Excel_line", "Model", "Question", "Correctness_reason"]

    results_df = pd.DataFrame(columns=results_columns)
    reasons_df = pd.DataFrame(columns=reasons_columns) 
    
    # 读取JSONL文件，获取图片名称
    jsonl_list = read_josnl(file_path)

    model_name = file_path.split('\\')[-1].split('-')[0]
    # 如果没有输入end_num参数，则默认为文件的行数
    if end_num is None:
        end_num = int(len(jsonl_list))
        print(Fore.GREEN + "end_num: ", Fore.RED + str(end_num))

    for i in tqdm(range(start_num, end_num), desc="Evaluating Model", unit="question"):
        # 进度跟踪
        print(Fore.GREEN + "进度: ", Fore.RED +
              str(i + 1) + "/" + str(end_num), end="\r")

        question = jsonl_list[i]["question"]
        correct_answer = jsonl_list[i]["GT"]
        model_answer = jsonl_list[i]["model_answer"]
        image = jsonl_list[i]["image"]
        print(Fore.GREEN + "问题: ", Fore.RED + question)
        print(Fore.GREEN + "正确答案: ", Fore.RED + correct_answer)
        print(Fore.GREEN + "模型回答: ", Fore.RED + model_answer)
        print(Fore.GREEN + "图片名称: ", Fore.RED + image)

        test_case = LLMTestCase(
            input=question,
            actual_output=model_answer,
            expected_output=correct_answer,
        )

        try:
            correctness_metric.measure(test_case)
            correctness_score = correctness_metric.score
            correctness_reason = correctness_metric.reason
        except Exception as e:
            print(
                f"在评估指标 {correctness_metric.name} 时发生错误: {str(e)}")
            for _ in range(5):
                try:
                    correctness_metric.measure(test_case)
                    correctness_score = correctness_metric.score
                    correctness_reason = correctness_metric.reason
                    break
                except Exception as e:
                    print(f"重试中... 错误: {str(e)}")
            else:
                print(
                    f"在5次重试后仍无法评估指标 {correctness_metric.name}。退出程序。")
                # 保存文件
                results_df.to_excel(temp_file_result, index=False)
                reasons_df.to_excel(temp_file_reason, index=False)
                sys.exit(1)

        # 使用ignore_index=True避免因重新索引导致的InvalidIndexError
        results_df = pd.concat([results_df, pd.DataFrame({
            "Excel_line": [i + 1],
            "image": [image],
            "Model": [model_name],
            "Question": [question],
            "reply": [model_answer],
            "Correctness": [correctness_score]
        })], ignore_index=True)

        reasons_df = pd.concat([reasons_df, pd.DataFrame({
            "Excel_line": [i + 1],
            "image": [image],
            "Model": [model_name],
            "Question": [question],
            "Correctness_reason": [correctness_reason]
        })], ignore_index=True)

        # 保存中间结果
        results_df.to_excel(temp_file_result, index=False)
        reasons_df.to_excel(temp_file_reason, index=False)

    return results_df, reasons_df



def print_results(start_num, model_name, question, correctness_score, answer):
    colorama.init(autoreset=True)
    print(Fore.GREEN + "Excel_line: ", Fore.RED + str(start_num + 1))
    print(Fore.GREEN + "Model: ", Fore.RED + model_name)
    # # print(Fore.GREEN + "Knowledge: ", Fore.RED + knowledge)
    print(Fore.GREEN + "Question: ", Fore.RED + question)
    print(Fore.GREEN + "Answer: ", Fore.RED + answer)
    # print(Fore.GREEN + "Reason: ", Fore.RED + reason)
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

    questions_file = r"D:\研究生\任务3\题库\VQA\最终题库\open\open_vqa.xlsx"
    qa_df = pd.read_excel(questions_file)

    # 临时文件
    temp_file_result = r"D:\研究生\帮师兄评测模型\师兄的会议\results_add.xlsx"
    temp_file_reason = r"D:\研究生\帮师兄评测模型\师兄的会议\reasons_add.xlsx"

    file_paths = [
        # r"D:\研究生\任务3\测试结果\VQA\open\bard.xlsx",
        r"D:\研究生\任务3\测试结果\VQA\open\gpt-4.xlsx",
        r"D:\研究生\任务3\测试结果\VQA\open\llava.xlsx",
        r"D:\研究生\任务3\测试结果\VQA\open\qwen-vl-max.xlsx",
        r"D:\研究生\任务3\测试结果\VQA\open\vilt.xlsx",
    ]

    final_file = r'D:\研究生\帮师兄评测模型\师兄的会议\评估结果_add.xlsx'
    reason_file = r'D:\研究生\帮师兄评测模型\师兄的会议\reason_add.xlsx'

    correctness_metric = initialize_metrics()

    start_num = 0
    # end_num = 1 断点续传才用

    # 设置信号处理函数,当退出时保存当前进度
    signal.signal(signal.SIGINT, signal_handler)

    #! for file_path in file_paths: 暂时不需要
    # 将结果保存到final_results.xlsx和reasons.xlsx
    results_df, reasons_df = evaluate_model(
        "D:\研究生\帮师兄评测模型\师兄的会议\LLaVA-Q_A_GT-new.jsonl", qa_df=qa_df, correctness_metric=correctness_metric, start_num=start_num, end_num=None, temp_file_result=temp_file_result, temp_file_reason=temp_file_reason)


if __name__ == "__main__":
    main()
