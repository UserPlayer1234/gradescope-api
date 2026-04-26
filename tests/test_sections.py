import pytest

from datetime import datetime, timedelta

from gradescopeapi.classes.account import Account


from gradescopeapi.classes.assignments import (
    update_assignment_date,
    update_assignment_by_sections,
    Deadlines,
)


def test_get_sections(create_session):
    """Test retrieving sections for a course."""
    # create account with test session
    account = Account(create_session("instructor"))
    course_id = "1302606"

    sections = account.get_sections(course_id)

    assert sections != {}, "Did not retrieve sections correctly"
    assert sections[0].section_name == "Section1", (
        "Did not retrieve correct section name"
    )


def test_update_assignment_by_sections(create_session):
    """Test updating section due dates for an assignment."""
    # create account with test session
    test_session = create_session("instructor")
    account = Account(test_session)
    course_id = "1302606"
    assignment_id = "8043535"

    # retrieve sections
    sections = []
    sections_objects = account.get_sections(course_id)
    for section_obj in sections_objects:
        sections.append(section_obj.section_name)

    release_date = datetime(2026, 1, 1)
    due_date = release_date + timedelta(days=1)
    og_late_due_date = due_date + timedelta(days=1)

    result = update_assignment_date(
        test_session, course_id, assignment_id, release_date, due_date, og_late_due_date
    )

    assert result, "Failed to update assignment due dates"

    sec_late_due_date = due_date + timedelta(days=5)

    result = update_assignment_by_sections(
        test_session,
        course_id,
        assignment_id,
        sections,
        True,
        release_date,
        due_date,
        sec_late_due_date,
    )

    assert result, "Failed to update section assignment due dates"

    assignments = account.get_assignments(course_id)
    for assignment in assignments:
        if assignment.assignment_id == assignment_id:
            assert assignment.deadlines == Deadlines(
                release_date, due_date, og_late_due_date
            ), "Original assignment date was changed!"
