#!/usr/bin/python3

from action import Action, MenuItem, Service
from courses import Course, Semester, Semesters, courses, semesters
from utils import MAX_LEN


class SetCurrentCourse(Action):
    'This action sets the current course to the given course. Only one course can be current at a time.'

    def __init__(self, course: Course):
        self.course = course
        super().__init__(
            name='set current course to {}'.format(course.name),
            display_name='Switch to {name:<{fill}} ({semester})'.format(
                name=course.name,
                fill=MAX_LEN,
                semester=course.semester),
        )

    def execute(self):
        self.logger.info(
            'Setting current course to {}'.format(self.course.name))
        courses.set_current_course(self.course)


class ChooseCurrentCourse(Service):
    'Choose current course'

    def __init__(self):
        super().__init__(
            name='choose current course',
        )

    def suggested_actions(self):
        actions = []
        actions += [SetCurrentCourse(course)
                    for course in courses if course is not courses.current]
        return actions


class DisplayCurrentCourse(MenuItem):
    'This is the current course.'

    def __init__(self):
        super().__init__(
            name='display current course',
            display_name='Now on: {name:<{fill}}    ({semester})'.format(
                name=courses.current.name,
                fill=MAX_LEN,
                semester=courses.current.path.resolve().parent.stem),
        )


class CreateCourse(Action):
    'This action creates a new course in the current semester.'

    def __init__(self, course_name):
        super().__init__(
            name='create course',
            display_name='Create new course',
        )
        self.course_name = course_name

    def execute(self):
        try:
            self.logger.info('Creating course {}'.format(self.course_name))

            courses.create_course(self.course_name)
        except Exception:
            self.logger.exception(
                'Failed to create course {}'.format(self.course_name))


class CreateCourseService(Service):
    'Create a new course. You must give the name of the course as an argument. If no argument is given, nothing will happen.'

    def __init__(self):
        super().__init__(
            name='create course',
        )
        self.hint_word = ['New', 'Course']

    def make_custom_action(self, args: list):
        return CreateCourse(' '.join(args))


class SetCurrentSemester(Action):
    'This action sets the current semester to the given semester.'

    def __init__(self, semester: Semester):
        self.semester = semester
        super().__init__(
            name='set current semester to {}'.format(semester),
            display_name='Switch to {semester_name}'.format(
                semester_name=semester.name),
        )

    def execute(self):
        self.logger.info(
            'Setting current semester to {}'.format(self.semester))
        semesters.set_current_semester(self.semester)


class ChooseCurrentSemester(Service):
    'Choose current semester'

    def __init__(self):
        super().__init__(
            name='choose current semester',
        )

    def suggested_actions(self):
        actions = []
        actions += [SetCurrentSemester(semester)
                    for semester in semesters if semester is not semesters.current]
        return actions


if __name__ == '__main__':
    ChooseCurrentSemester().execute()
