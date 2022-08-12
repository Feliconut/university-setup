#!/usr/local/bin/python3
from courses import courses

for course in courses:
    lectures = course.lectures

    r = lectures.parse_range_string('all')
    lectures.update_docs_in_master(r)
    lectures.compile_master()
