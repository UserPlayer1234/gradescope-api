import pytest

from datetime import datetime, timedelta

from gradescopeapi.classes.connection import GSConnection
from gradescopeapi.classes.assignments import Assignment, Deadlines, InvalidTitleName

import requests
import uuid


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
