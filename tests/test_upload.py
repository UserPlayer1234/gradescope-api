import os
import pytest

from dotenv import load_dotenv

from gradescopeapi.classes.connection import GSConnection
from gradescopeapi.classes.upload import upload_assignment

# load .env file
load_dotenv()

GRADESCOPE_CI_STUDENT_EMAIL = os.getenv("GRADESCOPE_CI_STUDENT_EMAIL")
GRADESCOPE_CI_STUDENT_PASSWORD = os.getenv("GRADESCOPE_CI_STUDENT_PASSWORD")
GRADESCOPE_CI_INSTRUCTOR_EMAIL = os.getenv("GRADESCOPE_CI_INSTRUCTOR_EMAIL")
GRADESCOPE_CI_INSTRUCTOR_PASSWORD = os.getenv("GRADESCOPE_CI_INSTRUCTOR_PASSWORD")

@pytest.mark.skip(reason="Not testing file uploads")
def new_session(account_type="student"):
    """Creates and returns a session for testing"""
    connection = GSConnection()

    match account_type.lower():
        case "student":
            connection.login(
                GRADESCOPE_CI_STUDENT_EMAIL, GRADESCOPE_CI_STUDENT_PASSWORD
            )
        case "instructor":
            connection.login(
                GRADESCOPE_CI_INSTRUCTOR_EMAIL, GRADESCOPE_CI_INSTRUCTOR_PASSWORD
            )
        case _:
            raise ValueError("Invalid account type: must be 'student' or 'instructor'")

    return connection.session

@pytest.mark.skip(reason="Not testing file uploads")
def test_valid_upload():
    # create test session
    test_session = new_session("student")

    course_id = "1302606"
    assignment_id = "8043535"

    with (
        open("tests/upload_files/text_file.txt", "rb") as text_file,
        open("tests/upload_files/markdown_file.md", "rb") as markdown_file,
        open("tests/upload_files/python_file.py", "rb") as python_file,
    ):
        submission_link = upload_assignment(
            test_session,
            course_id,
            assignment_id,
            text_file,
            markdown_file,
            python_file,
            leaderboard_name="test",
        )

    assert submission_link is not None

@pytest.mark.skip(reason="Not testing file uploads")
def test_invalid_upload():
    # create test session
    test_session = new_session("student")

    course_id = "1302606"
    invalid_assignment_id = "1111111"

    with (
        open("tests/upload_files/text_file.txt", "rb") as text_file,
        open("tests/upload_files/markdown_file.md", "rb") as markdown_file,
        open("tests/upload_files/python_file.py", "rb") as python_file,
    ):
        submission_link = upload_assignment(
            test_session,
            course_id,
            invalid_assignment_id,
            text_file,
            markdown_file,
            python_file,
        )

    assert submission_link is None

@pytest.mark.skip(reason="Not testing file uploads")
def test_upload_with_no_files():
    test_session = new_session("student")
    course_id = "1302606"
    assignment_id = "8043535"
    # No files are passed
    submission_link = upload_assignment(test_session, course_id, assignment_id)
    assert submission_link is None, "Should handle missing files gracefully"
