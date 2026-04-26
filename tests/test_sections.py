import pytest

from datetime import datetime, timedelta

from gradescopeapi.classes.account import Account


from gradescopeapi.classes.assignments import (
    update_assignment_date,
    update_assignment_date_by_sections,
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


def test_update_assignment_date_by_sections(create_session):
    """Test updating section due dates for an assignment."""
    # create account with test session
    test_session = create_session("instructor")
    account = Account(test_session)
    course_id = "1302606"
    assignment_id = "8043535"

    # retrieve sections
    section_names = ["Section1"]
    sections_objects = account.get_sections(course_id)
    # for section_obj in sections_objects:
    # section_names.append(section_obj.section_name)

    og_release_date = datetime(2026, 1, 1)
    og_due_date = og_release_date + timedelta(days=1)
    og_late_due_date = og_due_date + timedelta(days=1)

    result = update_assignment_date(
        session=test_session,
        course_id=course_id,
        assignment_id=assignment_id,
        release_date=og_release_date,
        due_date=og_due_date,
        late_due_date=og_late_due_date,
    )

    assert result, "Failed to update assignment deadlines"

    sec_release_date = og_release_date + timedelta(days=10)
    sec_due_date = sec_release_date + timedelta(days=1)
    sec_late_due_date = sec_due_date + timedelta(days=1)

    result = update_assignment_date_by_sections(
        session=test_session,
        course_id=course_id,
        assignment_id=assignment_id,
        sections=section_names,
        visibility=True,
        release_date=sec_release_date,
        due_date=sec_due_date,
        late_due_date=sec_late_due_date,
    )

    assert result, "Failed to update section assignment deadlines"

    assignments = account.get_assignments(course_id)
    assignment = next(
        (
            assignment
            for assignment in assignments
            if assignment.assignment_id == assignment_id
        )
    )

    assert assignment.deadlines == Deadlines(
        og_release_date, og_due_date, og_late_due_date
    ), "Original assignment deadline was changed!"

    section_obj = next(
        (
            section_obj
            for section_obj in sections_objects
            if section_obj.section_name == "Section1"
        )
    )
    section_deadline = assignment.sections.get(section_obj.section_id)

    assert section_deadline == Deadlines(
        sec_release_date, sec_due_date, sec_late_due_date, True
    ), "Section assignment deadline was not changed!"
