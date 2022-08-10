#!/usr/local/bin/python3
import sys
from courses import Courses
from choose import rofi
from choose import Rofi
from utils import generate_short_title, MAX_LEN

lectures = Courses().current.lectures

sorted_lectures = sorted(lectures, key=lambda l: -l.number)

options = [
    "{number: >2}. {title: <{fill}} {date}  ({week})".format(
        fill=MAX_LEN,
        number=lecture.number,
        title=generate_short_title(lecture.title),
        date=lecture.date.strftime('%a %d %b'),
        week=lecture.week
    )
    for lecture in sorted_lectures
    
]

def process(returncode, index, selected):
    if returncode == Rofi.SELECTED:
        if index != -1:
            sorted_lectures[index].edit()
        else:
            new_lecture = lectures.new_lecture(name=selected)
            new_lecture.edit()

if __name__ == '__main__':

    process(*rofi('Select lecture', options, [    ]))

    
