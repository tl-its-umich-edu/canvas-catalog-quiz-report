from canvasapi import Canvas
import time
import os
import json
import logging
from requests import get
import logging
import sys

def main():
    """
    Get the configuration file
    """
    logger = logging.getLogger("canvasapi")
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    # Set up ENV
    CONFIG_PATH = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'env.json')
    try:
        with open(CONFIG_PATH) as env_file:
            ENV = json.load(env_file)
    except FileNotFoundError:
        logger.error(
            f'Configuration file could not be found; please add file "{CONFIG_PATH}".')
        ENV = dict()

    # get the API parameters from ENV
    API_URL = ENV["API_URL"]
    API_KEY = ENV["API_KEY"]
    TERM_ID = ENV["TERM_ID"]  # only one term, "DEFAULT TERM", for now
    CANVAS_ACCOUNT_ID = ENV["CANVAS_ACCOUNT_ID"]

    # the output folder used in docker image
    # the local output folder can be mapped to different path in the docker command line
    output_folder = '/tmp/'

    # Initialize a new Canvas object
    canvas = Canvas(API_URL, API_KEY)

    # get the account with id equals to CANVAS_ACCOUNT_ID
    account = canvas.get_account(CANVAS_ACCOUNT_ID)

    # get all courses in CANVAS_ACCOUNT_ID
    courses = account.get_courses(
        enrollment_term_id=TERM_ID,
        published=True
    )

    course_count = 0
    for course in courses:
        course_count = course_count + 1
        # escape '/' in the course name string
        course_name = course.name.replace('/', ' ')
        # use course name and id as directory inside zip file
        course_output_path = f"{output_folder}{course.id} {course_name}/"
        os.makedirs(os.path.dirname(
            course_output_path), exist_ok=True)
        logger.info(f"course id: {course.id}; course name: {course_name}; output path: {course_output_path}")

        # count user number
        users = course.get_users()
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
            logger.info(
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
                logger.error(
                    f"Error: course id = {course.id} quiz id={quiz.id} type={quiz.quiz_type}: has no attribute file.")
            except Exception as e:
                logger.error(
                    f"Error: course id = {course.id} quiz id={quiz.id} type={quiz.quiz_type}: problem getting quiz report csv file. {e}")

if __name__ == "__main__":
    main()
