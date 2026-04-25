from datetime import datetime, timedelta

import pytest

from gradescopeapi.classes.extensions import (
    get_extensions,
    update_student_extension,
    remove_student_extension,
)


def test_get_extensions(create_session):
    """Test fetching extensions for an assignment."""
    # create test session
    test_session = create_session("instructor")

    course_id = "1302606"
    assignment_id = "8043535"

    extensions = get_extensions(test_session, course_id, assignment_id)
    assert len(extensions) > 0, (
        f"Got 0 extensions for course {course_id} and assignment {assignment_id}"
    )


def test_valid_change_extension(create_session):
    """Test granting a valid extension for a student."""
    # create test session
    test_session = create_session("instructor")

    course_id = "1302606"
    assignment_id = "8043535"
    user_id = "9629996"
    release_date = datetime(2026, 1, 1)
    due_date = release_date + timedelta(days=1)
    late_due_date = due_date + timedelta(days=1)

    result = update_student_extension(
        test_session,
        course_id,
        assignment_id,
        user_id,
        release_date,
        due_date,
        late_due_date,
    )
    assert result, "Failed to update student extension"


def test_invalid_change_extension(create_session):
    """Test granting an invalid extension for a student due to invalid dates."""
    # create test session
    test_session = create_session("instructor")

    course_id = "1302606"
    assignment_id = "8043535"
    user_id = "9629996"
    release_date = datetime(2026, 1, 1)
    due_date = release_date + timedelta(days=-1)
    late_due_date = due_date + timedelta(days=-1)

    with pytest.raises(
        ValueError,
        match="Dates must be in order: release_date <= due_date <= late_due_date",
    ):
        update_student_extension(
            test_session,
            course_id,
            assignment_id,
            user_id,
            release_date,
            due_date,
            late_due_date,
        )


def test_invalid_user_id(create_session):
    """Test granting an invalid extension for a student due to invalid user ID."""
    test_session = create_session("instructor")

    course_id = "1302606"
    assignment_id = "8043535"
    invalid_user_id = "9999999"  # Assuming this is an invalid ID

    # Attempt to change the extension with an invalid user ID
    result = update_student_extension(
        test_session,
        course_id,
        assignment_id,
        invalid_user_id,
        datetime.now(),
        datetime.now() + timedelta(days=1),
        datetime.now() + timedelta(days=2),
    )

    # Check the function returns False for non-existent user ID
    assert not result, "Function should indicate failure when given an invalid user ID"


def test_invalid_assignment_id(create_session):
    """Test extension handling with an invalid assignment ID."""
    test_session = create_session("instructor")
    course_id = "1302606"
    invalid_assignment_id = "9999999"

    # Attempt to fetch extensions with an invalid assignment ID
    with pytest.raises(RuntimeError, match="Failed to get extensions"):
        get_extensions(test_session, course_id, invalid_assignment_id)


def test_invalid_course_id(create_session):
    """Test extension handling with an invalid course ID."""
    test_session = create_session("instructor")
    invalid_course_id = "9999999"

    # Attempt to fetch or modify extensions with an invalid course ID
    with pytest.raises(RuntimeError, match="Failed to get extensions"):
        get_extensions(test_session, invalid_course_id, "8043535")


def test_valid_remove_extension(create_session):
    """Test remove extension with existing extension."""

    # Create extension for user
    test_valid_change_extension(create_session)

    test_session = create_session("instructor")
    course_id = "1302606"
    assignment_id = "8043535"
    user_id = "9629996"

    # Attempt to remove student extension
    result = remove_student_extension(test_session, course_id, assignment_id, user_id)

    assert result, "Failed to remove student extension"


def test_invalid_remove_extension(create_session):
    """Test remove extension with nonexistent extension."""

    # Create extension for user
    test_valid_change_extension(create_session)

    test_session = create_session("instructor")
    course_id = "1302606"
    assignment_id = "8043535"
    user_id = "9629996"

    # Attempt to remove student extension
    remove_student_extension(test_session, course_id, assignment_id, user_id)

    # Attempt to remove student extension again
    with pytest.raises(
        ValueError, match="No extension was found for the given user_id"
    ):
        remove_student_extension(test_session, course_id, assignment_id, user_id)
