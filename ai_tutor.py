import functools
import json
import logging
import pathlib
import time

from typing import Dict, List, Tuple

import requests


HEADER = Dict[str, str]


logging.basicConfig(level=logging.INFO)


RESOURCE_EXHAUSTED = 429


@functools.lru_cache
def url(api_key:str) -> str:
    return f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}'


@functools.lru_cache
def header() -> HEADER:
    return {'Content-Type': 'application/json'}


def ask_gemini(
            question: str,
            api_key:str,
            header:HEADER=header(),
            retry_delay_sec: float = 5.0,
            max_retry_attempt: int = 3,
            timeout_sec: int = 60
    ) -> str:
    """
    Asks a question to Gemini with rate limiting, retry logic, and timeout.

    Args:
        question: The question to ask.
        url: The Gemini API URL.
        header: The request headers.
        retry_delay_sec: The initial delay in seconds between retries.
        max_retry_attempt: The maximum number of retry attempts.
        timeout_sec: The maximum time in seconds allowed for retries.

    Returns:
        The answer from Gemini or None if all retries fail or timeout is reached.
    """

    data = {'contents': [{'parts': [{'text': question}]}]}
    start_time = time.monotonic()
    answer = None  # Initialize the answer variable

    for attempt in range(max_retry_attempt + 1):
        if time.monotonic() - start_time > timeout_sec:
            logging.error(f"Timeout exceeded for question: {question}")
            break  # Exit the loop on timeout

        response = requests.post(url(api_key), headers=header, json=data)

        if response.status_code == 200:
            result = response.json()
            results = [part['text'] for part in result['candidates'][0]['content']['parts']]
            answer = '\n'.join(results)
            break  # Exit the loop on success

        elif response.status_code == RESOURCE_EXHAUSTED:
            if attempt < max_retry_attempt:
                delay = retry_delay_sec * (2 ** attempt)
                logging.warning(f"Rate limit exceeded. Retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retry_attempt})")
                time.sleep(delay)
            else:
                logging.error(f"Max retries exceeded for RESOURCE_EXHAUSTED error. Question: {question}")

        else:
            logging.error(f"API request failed with status code {response.status_code}: {response.text}")

    return answer  # Return the answer (or None if unsuccessful) at the end


def gemini_qna(
        report_paths:List[pathlib.Path],
        student_files:List[pathlib.Path],
        readme_file:pathlib.Path,
        api_key:str,
        human_language:str='Korean',
    ) -> str:
    '''
    Queries the Gemini API to provide explanations for failed pytest test cases.

    Args:
        report_paths: A list of pathlib.Path objects representing the paths to JSON pytest report files.
        student_files: A list of pathlib.Path objects representing the paths to student's Python files.
        readme_file: A pathlib.Path object representing the path to the assignment instruction file.

    Returns:
        A string containing the feedback from Gemini.
    '''
    logging.info("Starting Gemini Q&A process...")
    logging.info(f"Report paths: {report_paths}")
    logging.info(f"Student files: {student_files}")
    logging.info(f"Readme file: {readme_file}")

    consolidated_question = get_the_question(
        report_paths,
        student_files,
        readme_file,
        human_language
    )

    answers = ask_gemini(consolidated_question, api_key)

    return answers


def get_the_question(
        report_paths:Tuple[pathlib.Path],
        student_files:Tuple[pathlib.Path],
        readme_file:pathlib.Path,
        human_language:str,
    ) -> str:
    questions = []

    # Process each report file
    for report_path in report_paths:
        logging.info(f"Processing report file: {report_path}")
        data = json.loads(report_path.read_text())

        longrepr_list = collect_longrepr(data)

        questions += longrepr_list

    def get_initial_instruction(questions:List[str],language:str) -> str:
        # Add the main directive or instruction based on whether there are failed tests
        if questions:
            initial_instruction = get_directive(language)
        else:
            initial_instruction = f'In {language}, please comment on the student code given the assignment instruction.'
        return initial_instruction

    
    questions = (
        # Add the initial instruction
        [get_initial_instruction(questions, human_language), get_question_header(human_language)]
        + questions
        # Add the code and instructions
        + [get_question_footer(human_language), get_code_instruction(student_files, readme_file, human_language)]
    )

    # Join all questions into a single string
    consolidated_question = "\n\n".join(questions)

    return consolidated_question


@functools.lru_cache
def get_directive(human_language:str) -> str:
    d = {
        'Korean': '숙제 답안으로 제출한 코드가 오류를 일으킨 원인을 입문자 용어만으로 중복 없는 간결한 문장으로 설명하시오.',
        'English': 'Explain in beginner terms, without duplicates, the cause of the error in the code submitted as homework.',
        'Japanese': '宿題の回答として提出されたコードがエラーの原因を、初心者向けの用語で重複なく簡潔に説明してください。',
        'Chinese': '请用初学者术语简洁地解释作业提交的代码出错的原因，不要重复。',
        'Spanish': 'Explique en términos para principiantes, sin duplicados, la causa del error en el código enviado como tarea.',
        'French': '''Expliquez en termes de débutant, sans doublons, la cause de l'erreur dans le code soumis comme devoir.''',
        'German': 'Erklären Sie in Anfängerterminologie ohne Duplikate die Ursache des Fehlers im als Hausaufgabe eingereichten Code.',
        'Thai': 'อธิบายด้วยภาษาของผู้เริ่มต้นโดยไม่ซ้ำซ้อนว่าสาเหตุของข้อผิดพลาดในรหัสที่ส่งเป็นการบ้านคืออะไร',
    }
    return f"{d[human_language]}\n"


def collect_longrepr(data:Dict[str, str]) -> List[str]:
    longrepr_list = []
    # Collect questions from tests not-passed yet
    for r in data['tests']:
        if r['outcome'] != 'passed':
            for k in r:
                if isinstance(r[k], dict) and 'longrepr' in r[k]:
                    longrepr_list.append(r['outcome'] + ':' + k + ':' + r[k]['longrepr'])
    return longrepr_list


@functools.lru_cache
def get_question(longrepr:str, human_language:str,) -> str:
    return (
        get_question_header(human_language) + f"{longrepr}\n" + get_question_footer(human_language)
    )


@functools.lru_cache
def get_question_header(human_language:str) -> str:
    d = {
        'Korean': "오류 메시지 시작",
        'English': "Error Message Start",
        'Japanese': "エラーメッセージ開始",
        'Chinese': "错误消息开始",
        'Spanish': "Mensaje de error comienza",
        'French': '''Message d'erreur commence''',
        'German': "Fehlermeldung beginnt",
        'Thai': "ข้อความผิดพลาดเริ่มต้น",
    }
    return (
        f"## {d[human_language]}\n"
    )


@functools.lru_cache
def get_question_footer(human_language:str) -> str:
    d = {
        'Korean': "오류 메시지 끝",
        'English': "Error Message End",
        'Japanese': "エラーメッセージ終わり",
        'Chinese': "错误消息结束",
        'Spanish': "Mensaje de error termina",
        'French': '''Message d'erreur fin''',
        'German': "Fehlermeldung endet",
        'Thai': "ข้อความผิดพลาดสิ้นสุด",
    }
    return (
        f"## {d[human_language]}\n"
    )


@functools.lru_cache
def get_code_instruction(
        student_files:Tuple[pathlib.Path],
        readme_file:pathlib.Path,
        human_language:str,
    ) -> str:

    d_homework_start = {
        'Korean': "숙제 제출 코드 시작",
        'English': "Homework Submission Code Start",
        'Japanese': "宿題提出コード開始",
        'Chinese': "作业提交代码开始",
        'Spanish': "Inicio del código de envío de tareas",
        'French': '''Début du code de soumission des devoirs''',
        'German': "Code für die Einreichung von Hausaufgaben von hier aus",
        'Thai': "การส่งงานเริ่มต้น",
    }

    d_homework_end = {
        'Korean': "숙제 제출 코드 끝",
        'English': "Homework Submission Code End",
        'Japanese': "宿題提出コード終わり",
        'Chinese': "作业提交代码结束",
        'Spanish': "Fin del código de envío de tareas",
        'French': '''Fin du code de soumission des devoirs''',
        'German': "Ende der Hausaufgaben-Einreichungscodes",
        'Thai': "การส่งงานสิ้นสุด",
    }

    d_instruction_start = {
        'Korean': "과제 지침 시작",
        'English': "Assignment Instruction Start",
        'Japanese': "課題指示開始",
        'Chinese': "作业说明开始",
        'Spanish': "Inicio de la instrucción de la tarea",
        'French': '''Début de l'instruction de la tâche''',
        'German': "Start der Aufgabenanweisung",
        'Thai': "คำแนะนำการบ้านเริ่มต้น",
    }

    d_instruction_end = {
        'Korean': "과제 지침 끝",
        'English': "Assignment Instruction End",
        'Japanese': "課題指示終わり",
        'Chinese': "作业说明结束",
        'Spanish': "Fin de la instrucción de la tarea",
        'French': '''Fin de l'instruction de la tâche''',
        'German': "Ende der Aufgabenanweisung",
        'Thai': "คำแนะนำการบ้านสิ้นสุด",
    }

    return (
        f"\n\n## {d_homework_start[human_language]}\n"
        f"{assignment_code(student_files)}\n"
        f"## {d_homework_end[human_language]}\n"
        f"## {d_instruction_start[human_language]}\n"
        f"{assignment_instruction(readme_file)}\n"
        f"## {d_instruction_end[human_language]}\n"
    )


@functools.lru_cache
def assignment_code(student_files:Tuple[pathlib.Path]) -> str:
    return '\n\n'.join([f"# begin : {str(f.name)} ======\n{f.read_text()}\n# end : {str(f.name)} ======\n" for f in student_files])


@functools.lru_cache
def assignment_instruction(readme_file:pathlib.Path) -> str:
    return readme_file.read_text()
