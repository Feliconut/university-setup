#!/usr/local/bin/python3
from courses import Courses
from rofi import rofi

lectures = Courses().current.lectures

commands = ['last', 'prev-last', 'all', 'prev']
options = ['Current lecture', 'Last two lectures',
           'All lectures', 'Previous lectures']


def process(returncode, index, selected):
    print((returncode, index, selected))
    if index >= 0:
        command = commands[index]
    else:
        command = selected

    lecture_range = lectures.parse_range_string(command)
    lectures.update_lectures_in_master(lecture_range)
    lectures.compile_master()


if __name__ == '__main__':
    process(*rofi('Select view', options, [
    ]))
