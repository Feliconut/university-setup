#!/usr/local/bin/python3
from action import Action, Service
from courses import courses

lectures = courses.current.lectures

commands = ['last', 'prev-last', 'all', 'prev']
cmd_display = ['Current lecture', 'Last two lectures',
               'All lectures', 'Previous lectures']


class SetCompileRange(Action):
    'Set the compile range, i.e. the range of lectures to include in the compiled pdf'

    def __init__(self, range: str, range_display: str):
        self.range = range
        super().__init__(
            name='Set compile range to {}'.format(self.range),
            display_name='Include {}'.format(range_display),
        )

    def execute(self, ):
        lectures.update_master_from_range_string(self.range)
        self.logger.info(self.display_name)
        lectures.compile_master()


class ChooseCompileRange(Service):
    '''Choose compile range. You may use "," to separate the range, e.g. "1,2,3,4,5". You may use "-" to indicate a range, e.g. "1-5". You may use "all" to include all lectures. You may use "last", "prev-last", "prev" to include the last, the last two, or the previous lectures.
    Note: duplication of lecture numbers is allowed.
    '''

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
