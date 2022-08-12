from action import Action, Service
from courses import Course, courses


current_course = courses.current
lectures = current_course.lectures


class OpenCoursePDF(Action):
    'Open the course PDF'

    def __init__(self, course: Course):
        self.course = course
        super().__init__(
            name='Open course PDF',
            display_name='Open {} PDF'.format(course.name),
        )

    def execute(self, ):
        self.logger.info('Opening course PDF')
        self.course.lectures.open_pdf()


class ChooseCoursePDF(Service):
    'Choose the course PDF'

    def __init__(self):
        super().__init__(
            name='Choose course PDF',
        )

    def suggested_actions(self):
        return [OpenCoursePDF(course) for course in courses]


if __name__ == '__main__':
    ChooseCoursePDF().execute()
