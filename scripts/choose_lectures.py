#!/usr/local/bin/python3
from action import Action, Service
from courses import courses
from lectures import Lecture, Lectures
from courses import Course
from utils import generate_short_title, MAX_LEN

current_course = courses.current
lectures = current_course.lectures


class OpenLecture(Action):
    'Edit a document using vimtex. This action opens a MacVim window with the .tex file.'

    def __init__(self, lecture: Lecture, course: Course):
        self.lecture = lecture
        super().__init__(
            name='Open document {}'.format(lecture.file_path),
            display_name="Open {number}.           {title: <{fill}} {space} {date:<{fill}}".format(
                fill=MAX_LEN,
                number=lecture.index,
                title=generate_short_title(lecture.title),
                date=lecture.date.strftime('%a %d %b'),
                week=lecture.week,
                course_short=course.info['short'],
                space = ' '*int((MAX_LEN - len(generate_short_title(lecture.title)))*1.35)
            )
        )

    def execute(self, ):
        self.logger.info('Opening document {}'.format(self.lecture.file_path))
        self.lecture.edit()


class CreateLecture(Action):
    '''Create a new document in the current course. The 
    document will be opened in vimtex.'''

    def __init__(self, name='', type_name='lecture'):
        self.lecture_name = name
        self.type_name = type_name
        super().__init__(
            name='new lecture',
            display_name='New Lecture',
        )

    def execute(self, ):
        self.logger.info(
            'Creating new lecture in {}'.format(current_course.name))
        try:
            new_lecture = lectures.new_doc(
                name=self.lecture_name, type_name=self.type_name)
            OpenLecture(new_lecture, current_course).execute()
        except:
            self.logger.exception(
                'Could not create lecture: {}'.format(self.lecture_name))


class CreateLectureService(Service):
    '''Create a new document in the current course. The document will be opened in vimtex. The document name and type is given as an argument. If no argument is given, the name will be empty, and type will default to `lecture`.'''

    def __init__(self, type_name='lecture'):
        super().__init__(name='create lecture')
        self.hint_word = ['New', type_name.capitalize()]
        self.type_name = type_name

    def make_custom_action(self, args):
        return CreateLecture(name=' '.join(args), type_name=self.type_name)


class ChooseLecture(Service):
    '''Choose a document from the current course. The document will be opened in vimtex. The index (eg. `Lecture 1`) is given as an argument. If no argument is given, nothing will happen.'''

    def __init__(self, type_name='lecture',):
        super().__init__(
            name='choose documents')
        self.type_name = type_name
        self.hint_word = ['Open'] + [type_name.capitalize()]

    def suggested_actions(self):
        return [OpenLecture(lecture, current_course) for lecture in lectures if lecture.index[0] == self.type_name]

    def make_custom_action(self, args):
        if args:
            lecture_number = lectures.parse_range_string(
                self.type_name + ' ' + ' '.join(args))[0]
            if lecture_number in lectures.all_indices:
                try:
                    return OpenLecture(lectures.get_from_index(lecture_number), current_course)
                except IndexError:
                    pass


class CreateDocumentTypeService(Service):
    '''Create a new document type. The document type is given as an argument. If no argument is given, nothing will happen.'''

    def __init__(self):
        super().__init__(name='create document type')
        self.hint_word = ['New', 'Document', 'Type']

    def make_custom_action(self, args):
        # check that the document type does not already exist
        if args:
            type_name = args[0]
            if type_name in lectures.all_types:
                self.logger.error(
                    'Document type {} already exists'.format(type_name))
                return None
            return CreateLecture(name=' '.join(args), type_name=args[0].lower())


if __name__ == '__main__':
    # ChooseLecture().execute()
    CreateDocumentTypeService().execute()
