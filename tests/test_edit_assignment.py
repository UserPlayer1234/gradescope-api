from datetime import datetime, timedelta

from gradescopeapi.classes.connection import GSConnection
from gradescopeapi.classes.assignments import Deadlines, InvalidTitleName

import requests
import uuid


def test_deadline_creation():
    # Incorrectly ordered dates
    try:
        deadlines = Deadlines(
            release_date=datetime(2001, 1, 1),
            due_date=datetime(2001, 1, 2),
            late_due_date=datetime(2001, 1, 1),
            visibility=True,
        )
        assert False, "Did not throw error when creating incorrectly ordered deadlines"
    except Exception as e:
        assert isinstance(e, ValueError)

def test_deadline_addition():
    # Testing on regular deadlines
    deadlines = Deadlines(
        release_date=datetime(2001, 1, 1),
        due_date=datetime(2001, 1, 2),
        late_due_date=datetime(2001, 1, 3),
        visibility=True,
    )

    # Shift deadlines by 1 day with addition
    deadlines = deadlines + timedelta(days=1)

    # Assert deadlines shifted by 1 day
    assert deadlines.release_date == datetime(2001, 1, 2)
    assert deadlines.due_date == datetime(2001, 1, 3)
    assert deadlines.late_due_date == datetime(2001, 1, 4)

    # Testing new deadlines object from result
    deadlines2 = deadlines + timedelta(days=1)

    assert deadlines.release_date == datetime(2001, 1, 2)
    assert deadlines.due_date == datetime(2001, 1, 3)
    assert deadlines.late_due_date == datetime(2001, 1, 4)

    assert deadlines2.release_date == datetime(2001, 1, 3)
    assert deadlines2.due_date == datetime(2001, 1, 4)
    assert deadlines2.late_due_date == datetime(2001, 1, 5)

    # Testing on deadlines w/o late due date
    deadlines = Deadlines(
        release_date=datetime(2001, 1, 1),
        due_date=datetime(2001, 1, 2),
        late_due_date=None,
        visibility=True,
    )

    # Shift deadlines by 1 day with addition
    deadlines = deadlines + timedelta(days=1)

    # Assert deadlines shifted by 1 day and late due date is still None
    assert deadlines.release_date == datetime(2001, 1, 2)
    assert deadlines.due_date == datetime(2001, 1, 3)
    assert deadlines.late_due_date == None

    # Attempt to add something else to deadlines
    try:
        deadlines = deadlines + deadlines
        assert False, "Attempted to add non timedelta object to Deadlines"
    except Exception as e:
        assert isinstance(e, ValueError)

def test_deadline_cutoff():
    deadlines = Deadlines(
            release_date=datetime(2001, 1, 1),
            due_date=datetime(2001, 1, 6),
            late_due_date=datetime(2001, 1, 11),
            visibility=True,
        )
    
    deadlines.cut_off_date(datetime(2001, 1, 5))

    assert deadlines.release_date == datetime(2001, 1, 1)
    assert deadlines.due_date == datetime(2001, 1, 5)
    assert deadlines.late_due_date == datetime(2001, 1, 5)

def test_valid_change_assignment(create_connection):
    """Test valid assignment change."""
    # create test connection
    test_connection: GSConnection = create_connection("instructor")

    course_id = "1302606"
    assignment_id = "8043535"

    test_assignment = test_connection.account.get_assignment(course_id, assignment_id)

    release_date = datetime(2026, 1, 1)
    due_date = release_date + timedelta(days=1)
    late_due_date = due_date + timedelta(days=1)

    result = test_assignment.update_assignment_date(
        test_connection.session,
        release_date,
        due_date,
        late_due_date,
    )

    assert result, "Failed to update assignment"

    release_date = datetime(2026, 1, 2)
    due_date = release_date + timedelta(days=1)
    late_due_date = due_date + timedelta(days=1)

    result = test_assignment.update_assignment_date(
        test_connection.session,
        release_date,
        due_date,
        late_due_date,
    )

    assert result, "Failed to update assignment"

    assert test_assignment.deadlines == Deadlines(
        release_date, due_date, late_due_date
    ), "Assignment object deadlines not updated locally"


def test_boundary_date_assignment(create_connection):
    """Test updating assignment with boundary date values."""
    # create test connection
    test_connection: GSConnection = create_connection("instructor")

    course_id = "1302606"
    assignment_id = "8043535"

    test_assignment = test_connection.account.get_assignment(course_id, assignment_id)

    boundary_date = datetime(1900, 1, 1)  # Very old date

    result = test_assignment.update_assignment_date(
        test_connection.session,
        boundary_date,
        boundary_date,
        boundary_date,
    )

    assert result, "Failed to update assignment with boundary dates"


def test_update_assignment_date_invalid_session(create_connection):
    """Test updating assignment with student session."""
    test_connection: GSConnection = create_connection("instructor")

    course_id = "1302606"
    assignment_id = "8043535"

    test_assignment = test_connection.account.get_assignment(course_id, assignment_id)

    release_date = datetime(2026, 1, 1)
    due_date = release_date + timedelta(days=1)
    late_due_date = due_date + timedelta(days=1)

    student_connection = create_connection("student")

    try:
        test_assignment.update_assignment_date(
            student_connection.session,
            release_date,
            due_date,
            late_due_date,
        )
        assert False, "Incorrectly updated assignment title with invalid session"
    except requests.exceptions.HTTPError as e:
        assert e.response.status_code == 401  # HTTP 401 Not Authorized


def test_autograder_valid_image_name(create_connection):
    """Test updating assignment with valid image name."""
    test_connection: GSConnection = create_connection("instructor")

    course_id = "1302606"
    assignment_id = "8079664"
    image_name = "gradescope/autograder-base:ubuntu-22.04"

    test_assignment = test_connection.account.get_assignment(course_id, assignment_id)

    result = test_assignment.update_autograder_image_name(
        test_connection.session,
        image_name,
    )
    assert result, "Failed to update autograder image name"


def test_autograder_invalid_image_name(create_connection):
    """Test updating assignment with invalid image name."""
    test_connection: GSConnection = create_connection("instructor")

    course_id = "1302606"
    assignment_id = "8079664"
    image_name = "gradescope/autograders:us-prod-docker_image-123456"

    test_assignment = test_connection.account.get_assignment(course_id, assignment_id)

    result = test_assignment.update_autograder_image_name(
        test_connection.session,
        image_name,
    )
    assert not result, "Incorrectly updated to invalid autograder image name"


def test_autograder_invalid_session(create_connection):
    """Test updating assignment with student session."""
    test_connection: GSConnection = create_connection("instructor")

    course_id = "1302606"
    assignment_id = "8079664"
    image_name = "gradescope/autograder-base:ubuntu-22.04"

    test_assignment = test_connection.account.get_assignment(course_id, assignment_id)

    student_connection: GSConnection = create_connection("student")

    try:
        test_assignment.update_autograder_image_name(
            student_connection.session,
            image_name,
        )
        assert False, "Incorrectly updated assignment with invalid session"
    except requests.exceptions.HTTPError as e:
        assert e.response.status_code == 401  # HTTP 401 Not Authorized


def test_autograder_invalid_assignment_type(create_connection):
    """Test updating assignment with invalid assignment type."""
    test_connection: GSConnection = create_connection("instructor")

    course_id = "1302606"
    assignment_id = "8043535"
    image_name = "gradescope/autograder-base:ubuntu-22.04"

    test_assignment = test_connection.account.get_assignment(course_id, assignment_id)

    try:
        test_assignment.update_autograder_image_name(
            test_connection.session,
            image_name,
        )
        assert False, "Incorrectly updated assignment with invalid assignment"
    except requests.exceptions.HTTPError as e:
        assert e.response.status_code == 404  # HTTP 404 Not Found


def test_update_assignment_title_valid_random_title(create_connection):
    """Test updating assignment with random name."""
    test_connection: GSConnection = create_connection("instructor")

    course_id = "1302606"
    assignment_id = "8043535"
    new_assignment_name = f"Test Rename - {uuid.uuid4()}"

    test_assignment = test_connection.account.get_assignment(course_id, assignment_id)

    result = test_assignment.update_assignment_title(
        test_connection.session,
        new_assignment_name,
    )
    assert result, "Failed to update assignment name"


def test_update_assignment_title_invalid_title_whitespace(create_connection):
    """Test updating assignment with invalid name containing only whitespace."""
    test_connection: GSConnection = create_connection("instructor")

    course_id = "1302606"
    assignment_id = "8043535"
    new_assignment_name = "  "  # whitespace only not allowed

    test_assignment = test_connection.account.get_assignment(course_id, assignment_id)

    try:
        test_assignment.update_assignment_title(
            test_connection.session,
            new_assignment_name,
        )
        assert False, "Incorrectly updated to invalid assignment name"
    except InvalidTitleName:
        pass


def test_update_assignment_title_invalid_session(create_connection):
    """Test updating assignment with student session."""
    test_connection: GSConnection = create_connection("instructor")

    course_id = "1302606"
    assignment_id = "8043535"
    new_assignment_name = f"Test Rename - {uuid.uuid4()}"

    test_assignment = test_connection.account.get_assignment(course_id, assignment_id)

    student_connection: GSConnection = create_connection("student")

    try:
        test_assignment.update_assignment_title(
            student_connection.session,
            new_assignment_name,
        )
        assert False, "Incorrectly updated assignment title with invalid session"
    except requests.exceptions.HTTPError as e:
        assert e.response.status_code == 401  # HTTP 401 Not Authorized
