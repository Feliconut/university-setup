#!/usr/local/bin/python3
from courses import Courses
from lectures import Lecture
from utils import generate_short_title, MAX_LEN

lectures = Courses().current.lectures


from courses import Courses
from action import Action,Service


class OpenLecture(Action):
    def __init__(self, lecture:Lecture):
        self.lecture = lecture
        super().__init__(
            name='Open lecture {}'.format(lecture.file_path),
            display_name="Edit {number: >2}. {title: <{fill}} {date}  ({week})".format(
        fill=MAX_LEN,
        number=lecture.number,
        title=generate_short_title(lecture.title),
        date=lecture.date.strftime('%a %d %b'),
        week=lecture.week,
        course_short = lecture.course.info['short']
    ),
            description='Edit a lecture using vimtex')

    def execute(self, state):
        self.logger.info('Opening lecture {}'.format(self.lecture.file_path))
        self.lecture.edit()

class ChooseLecture(Service):
    def __init__(self):
        super().__init__(
            name='choose lectures',
            description = 'Choose lectures to open from current course')

    def _load_actions(self):
        return [OpenLecture(lecture) for lecture in lectures]

    def improvise_action(self, prompt):
        try:
            new_lecture = lectures.new_lecture(name=prompt)
            return OpenLecture(new_lecture, 'Open the lecture: '+ new_lecture.name)
        except:
            self.logger.exception('Could not create lecture: {}'.format(prompt))

if __name__ == '__main__':
    ChooseLecture().execute()
   
