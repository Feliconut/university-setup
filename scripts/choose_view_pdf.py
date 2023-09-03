from action import Action, Service
from courses import Course, courses
from utils import MAX_LEN




class OpenCoursePDF(Action):
    'Open the compiled PDF of this course.'

    def __init__(self, course: Course):
        self.course = course
        super().__init__(
            name='Open course PDF',
            display_name=f'Open PDF: {" "*MAX_LEN}{course.name}',
        )

    def execute(self, ):
        self.logger.info('Opening course PDF')
        self.course.lectures.open_pdf()


class ChooseCoursePDF(Service):
    'Choose the course name whose PDF should be opened.'

    def __init__(self):
        super().__init__(
            name='Choose course PDF',
        )

    def suggested_actions(self):
        return [OpenCoursePDF(course) for course in courses]

class ExportCurrentCoursePDF(Action):
    'Export the compiled PDF of this course.'

    def __init__(self):
        super().__init__(
            name='Export course PDF',
            display_name='Export course PDF',
        )
    

    def execute(self, ):
        self.logger.info('Exporting course PDF')
        pdf_path = str(courses.current.lectures.path / 'master.pdf')
        # copy the file to desktop of current user
        from shutil import copyfile
        from pathlib import Path
        home = str(Path.home())
        copyfile(pdf_path, home + '/Desktop/' + courses.current.name + '.pdf')



if __name__ == '__main__':
    OpenCoursePDF(courses.current).execute()
