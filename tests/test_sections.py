import pytest
import os

from datetime import datetime, timedelta

from gradescopeapi.classes.account import Account

from gradescopeapi.classes.connection import GSConnection

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

    section_names = [section.section_name for section in sections]
    assert section_names.__contains__("Section1") and section_names.__contains__(
        "Section2"
    ), "Did not retrieve correct section name"


def test_update_assignment_date_by_sections(create_session):
    """Test updating section due dates for an assignment."""
    # create account with test session
    test_session = create_session("instructor")
    account = Account(test_session)
    course_id = "1302606"
    assignment_id = "8043535"

    # retrieve sections
    sections_objects = account.get_sections(course_id)
    section_names = ["Section1"]

    # update assignment deadline
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

    # update section deadline
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

    # retrieve assignment
    assignments = account.get_assignments(course_id)
    assignment = next(
        (
            assignment
            for assignment in assignments
            if assignment.assignment_id == assignment_id
        )
    )

    # check assignment deadline was unchanged
    assert assignment.deadlines == Deadlines(
        og_release_date, og_due_date, og_late_due_date
    ), "Original assignment deadline was changed!"

    # retrieve section
    section_obj = next(
        (
            section_obj
            for section_obj in sections_objects
            if section_obj.section_name == "Section1"
        )
    )
    section_deadline = assignment.sections.get(section_obj.section_id)

    # check section deadline was changed
    assert section_deadline == Deadlines(
        sec_release_date, sec_due_date, sec_late_due_date, True
    ), "Section assignment deadline was not changed!"


def test_update_assignment_date_by_multiple_sections(create_session):
    """Test updating section due dates for an assignment."""
    # create account with test session
    test_session = create_session("instructor")
    account = Account(test_session)
    course_id = "1302606"
    assignment_id = "8043535"

    # retrieve sections
    sections_objects = account.get_sections(course_id)
    section_one = ["Section1"]
    section_two = ["Section2"]

    # update assignment deadline
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

    # update section one deadline
    sec1_release_date = og_release_date + timedelta(days=10)
    sec1_due_date = sec1_release_date + timedelta(days=1)
    sec1_late_due_date = sec1_due_date + timedelta(days=1)

    result = update_assignment_date_by_sections(
        session=test_session,
        course_id=course_id,
        assignment_id=assignment_id,
        sections=section_one,
        visibility=True,
        release_date=sec1_release_date,
        due_date=sec1_due_date,
        late_due_date=sec1_late_due_date,
    )

    assert result, "Failed to update section one assignment deadlines"

    # update section two deadline
    sec2_release_date = og_release_date + timedelta(days=100)
    sec2_due_date = sec2_release_date + timedelta(days=1)
    sec2_late_due_date = sec2_due_date + timedelta(days=1)

    result = update_assignment_date_by_sections(
        session=test_session,
        course_id=course_id,
        assignment_id=assignment_id,
        sections=section_two,
        visibility=True,
        release_date=sec2_release_date,
        due_date=sec2_due_date,
        late_due_date=sec2_late_due_date,
    )

    assert result, "Failed to update section two assignment deadlines"

    # retrieve assignment
    assignments = account.get_assignments(course_id)
    assignment = next(
        (
            assignment
            for assignment in assignments
            if assignment.assignment_id == assignment_id
        )
    )

    # check assignment deadline was unchanged
    assert assignment.deadlines == Deadlines(
        og_release_date, og_due_date, og_late_due_date
    ), "Original assignment deadline was changed!"

    # retrieve section one
    section_one_obj = next(
        (
            section_obj
            for section_obj in sections_objects
            if section_obj.section_name == "Section1"
        )
    )
    section_one_deadline = assignment.sections.get(section_one_obj.section_id)

    # check section one deadline was changed
    assert section_one_deadline == Deadlines(
        sec1_release_date, sec1_due_date, sec1_late_due_date, True
    ), "Section one assignment deadline was not changed!"

    # retrieve section two
    section_two_obj = next(
        (
            section_obj
            for section_obj in sections_objects
            if section_obj.section_name == "Section2"
        )
    )
    section_two_deadline = assignment.sections.get(section_two_obj.section_id)

    # check section two deadline was changed
    assert section_two_deadline == Deadlines(
        sec2_release_date, sec2_due_date, sec2_late_due_date, True
    ), "Section one assignment deadline was not changed!"

    # update section one and two to have section two deadline
    sections = ["Section1", "Section2"]

    result = update_assignment_date_by_sections(
        session=test_session,
        course_id=course_id,
        assignment_id=assignment_id,
        sections=sections,
        visibility=True,
        release_date=sec2_release_date,
        due_date=sec2_due_date,
        late_due_date=sec2_late_due_date,
    )

    assert result, "Failed to update section one and two assignment deadlines"

    # check assignment deadline was unchanged
    assert assignment.deadlines == Deadlines(
        og_release_date, og_due_date, og_late_due_date
    ), "Original assignment deadline was changed!"

    # update section one deadline variable
    updated_assignments = account.get_assignments(course_id)
    updated_assignment = next(
        (
            assignment
            for assignment in updated_assignments
            if assignment.assignment_id == assignment_id
        )
    )
    section_one_deadline = updated_assignment.sections.get(section_one_obj.section_id)

    # check section one and two deadlines are the same
    assert (
        section_one_deadline == section_two_deadline
        and section_two_deadline
        == Deadlines(sec2_release_date, sec2_due_date, sec2_late_due_date, True)
    ), "Both sections' assignment deadlines were not changed!"
