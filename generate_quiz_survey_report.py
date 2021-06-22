from canvasapi import Canvas
import time
import os
import json
import logging
import urllib
from requests import get


# check the progress of quiz report
# return true if the progress is 100% done


def wait_till_quiz_report_is_ready(report_progress_url):
    report_ready = False
    while not report_ready:
        report_status_json = urllib.request.urlopen(report_progress_url).read()
        percentage = report_status_json["completion"]
        if percentage == 100:
            report_ready = True
    return


def main():
    """
    Get the configuration file
    """
    logger = logging.getLogger(__name__)

    # Set up ENV
    CONFIG_PATH = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'env.json')
    try:
        with open(CONFIG_PATH) as env_file:
            ENV = json.load(env_file)
    except FileNotFoundError:
        print(
            f'Configuration file could not be found; please add file "{CONFIG_PATH}".')
        ENV = dict()

    # get the API parameters from ENV
    API_URL = ENV["API_URL"]
    API_KEY = ENV["API_KEY"]
    TERM_ID = ENV["TERM_ID"]  # only one term, "DEFAULT TERM", for now
    CANVAS_ACCOUNT_ID = ENV["CANVAS_ACCOUNT_ID"]

    output_folder = '/tmp/'

    # Initialize a new Canvas object
    canvas = Canvas(API_URL, API_KEY)
    accounts = canvas.get_accounts()

    # search for all Canvas accounts
    for account in accounts:
        subaccounts = account.get_subaccounts()
        for sa in subaccounts:
            print(f"account title = {sa.name}; account id = {sa.id}")
            if sa.id != CANVAS_ACCOUNT_ID:
                continue

            # get all courses in CANVAS_ACCOUNT_ID
            courses = account.get_courses(
                enrollment_term_id=TERM_ID,
                published=True
            )

            course_count = 0
            for course in courses:
                course_count = course_count + 1
                print(course.name)

                # use course name and id as directory inside zip file
                course_output_path = f"{output_folder}{course.name}({course.id})/"
                os.makedirs(os.path.dirname(
                    course_output_path), exist_ok=True)
                users = course.get_users()

                # count user number
                user_number = 0
                for user in users:
                    user_number = user_number + 1
                    break

                # proceed only when course has user inside
                if user_number == 0:
                    continue

                # get all quizzes inside course
                quizzes = course.get_quizzes()
                for quiz in quizzes:
                    print(
                        f"""course id = {course.id} quiz id={quiz.id} type={quiz.quiz_type} assignment id = {quiz.assignment_id}""")

                    # create quiz "student analysis" report
                    quiz_report = quiz.create_report(
                        'student_analysis', include=['progress_url', 'file'])

                    # sleep for 2 sec before downloading the report file
                    time.sleep(2)

                    # download the student analysis report
                    try:
                        download_url = quiz_report.file['url']
                        response = get(download_url)
                        with open(f"{course_output_path}{quiz.title}_Student Analysis.csv", 'wb') as file:
                            file.write(response.content)
                    except AttributeError:
                        print(
                            f"course id = {course.id} quiz id={quiz.id} type={quiz.quiz_type}: has no attribute file.")
                    else:
                        print(
                            f"course id = {course.id} quiz id={quiz.id} type={quiz.quiz_type}: problem getting quiz report csv file.")


if __name__ == "__main__":
    main()