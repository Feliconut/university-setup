#!/usr/local/bin/python3
from action import Action, Service
from courses import courses
from lectures import Lecture, Lectures
from utils import generate_short_title, MAX_LEN

current_course = courses.current
lectures = current_course.lectures


class OpenLecture(Action):
    'Edit a lecture using vimtex. This action opens a MacVim window with the lecture file.'

    def __init__(self, lecture: Lecture):
        self.lecture = lecture
        super().__init__(
            name='Open lecture {}'.format(lecture.file_path),
            display_name="Open {number: >2}. {title: <{fill}} {date}  ({week})".format(
                fill=MAX_LEN,
                number=lecture.number,
                title=generate_short_title(lecture.title),
                date=lecture.date.strftime('%a %d %b'),
                week=lecture.week,
                course_short=lecture.course.info['short']
            )
        )

    def execute(self, ):
        self.logger.info('Opening lecture {}'.format(self.lecture.file_path))
        self.lecture.edit()


class CreateLecture(Action):
    '''Create a new lecture in the current course. The 
    lecture will be opened in vimtex.'''

    def __init__(self, name=''):
        self.lecture_name = name
        super().__init__(
            name='new lecture',
            display_name='New Lecture',
        )

    def execute(self, ):
        self.logger.info(
            'Creating new lecture in {}'.format(current_course.name))
        try:
            new_lecture = lectures.new_lecture(name=self.lecture_name)
            OpenLecture(new_lecture).execute()
        except:
            self.logger.exception(
                'Could not create lecture: {}'.format(self.lecture_name))


class CreateLectureService(Service):
    '''Create a new lecture in the current course. The lecture will be opened in vimtex. The lecture name is given as an argument. If no argument is given, the name will be empty.'''

    def __init__(self):
        super().__init__(name='create lecture')
        self.hint_word = ['New', 'Lecture']

    def make_custom_action(self, args):
        return CreateLecture(name=' '.join(args))


class ChooseLecture(Service):
    '''Choose a lecture from the current course. The lecture will be opened in vimtex. The lecture number is given as an argument. If no argument is given, nothing will happen.'''

    def __init__(self):
        super().__init__(
            name='choose lectures',)
        self.hint_word = ['Open', 'Lecture']

    def suggested_actions(self):
        return [OpenLecture(lecture) for lecture in lectures]

    def make_custom_action(self, args):
        if args:
            lecture_number = lectures.parse_lecture_spec(args[0])
            if lecture_number in lectures.all_numbers:
                try:
                    return OpenLecture(lectures.get_from_number(lecture_number))
                except IndexError:
                    pass


if __name__ == '__main__':
    ChooseLecture().execute()
