#!/usr/local/bin/python3
from action import Action, Service
from courses import courses

lectures = courses.current.lectures

commands = ['last', 'prev-last', 'all', 'prev']
cmd_display = ['Current lecture', 'Last two lectures',
               'All lectures', 'Previous lectures']


class SetCompileRange(Action):
    'Set compile range'

    def __init__(self, range: str, range_display: str):
        self.range = range
        super().__init__(
            name='Set compile range to {}'.format(self.range),
            display_name='Include {}'.format(range_display),
        )

    def execute(self, ):
        lecture_range = lectures.parse_range_string(self.range)
        lectures.update_lectures_in_master(lecture_range)
        self.logger.info(self.display_name)
        lectures.compile_master()


class ChooseCompileRange(Service):
    'Choose compile range'

    def __init__(self):
        super().__init__(
            name='choose compile range',
        )
        self.hint_word = ['Include']

    def suggested_actions(self):
        return [SetCompileRange(cmd, disp) for cmd, disp in zip(commands, cmd_display)]

    def make_custom_action(self, args):
        range_str = ','.join(args)
        try:
            lectures.parse_range_string(range_str)
            return SetCompileRange(range_str, 'User entered range: ' + range_str)
        except:
            self.logger.exception(
                'Could not parse range: {}'.format(range_str))


if __name__ == '__main__':
    ChooseCompileRange().execute()
