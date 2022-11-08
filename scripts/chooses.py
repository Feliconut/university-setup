#!/usr/local/bin/python3

from pathlib import Path
from typing import List, Union
from action import Action, MenuItem, Service
from courses import courses, semesters
from show_picture import ShowPictureAction

# register all services and options

exists_semester_current = semesters.has_current()
exists_course_current = courses.has_current()

services: List[Union[Service, MenuItem]] = []

if exists_course_current:
    from choose_lectures_view import ChooseCompileRange
    from choose_courses import ChooseCurrentCourse, DisplayCurrentCourse
    from choose_lectures import ChooseLecture, CreateLectureService, CreateDocumentTypeService
    services += [ChooseCompileRange(),
                 DisplayCurrentCourse(), ]

    append = []
    for type_name in courses.current.lectures.all_types:
        services += [ChooseLecture(type_name), ]
        append += [CreateLectureService(type_name)]
    services += append
    services += [CreateDocumentTypeService(), ]
    services += [
        ChooseCurrentCourse(),
    ]


if exists_semester_current:
    from choose_view_pdf import ChooseCoursePDF, ExportCurrentCoursePDF
    from choose_courses import CreateCourseService, ChooseCurrentSemester
    services += [
        CreateCourseService(),
        ChooseCoursePDF(),
        ExportCurrentCoursePDF(),
        ChooseCurrentSemester(), ]

from choose_logseq import ConvertVimtexAction
services += [ConvertVimtexAction(), 
             ShowPictureAction(Path(__file__).parent / 'assets/inkscape_shortcut.png'), ]


class AllChoicesService(Service):
    'All services, to be invoked by global shortcut'

    def __init__(self):
        super().__init__(name='ALL')
        self.services = services

    def suggested_actions(self):
        actions = []
        for service in self.services:
            try:
                actions.extend(service.get_displayed_menuitems())
            except AttributeError:  # is a MenuItem instead of a Service
                assert isinstance(service, MenuItem)
                actions.append(service)
                pass
            except NotImplementedError:
                pass
        return actions

    def action_from_prompt(self, prompt):
        for service in services:
            if isinstance(service, Service):
                try:
                    action: Action = service.action_from_prompt(prompt)
                    if action:
                        return action
                except NotImplementedError:
                    pass


if __name__ == '__main__':
    AllChoicesService().execute()
