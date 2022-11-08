from pathlib import Path
import subprocess
from action import Action
class ShowPictureAction(Action):
    def __init__(self, path:Path):
        super().__init__(
            name='show picture',
            display_name='Show inkscape reference card',
        )
        self.path = path
    def execute(self):
        self.logger.info('Showing picture {}'.format(self.path))
        # open img.png with Apple Quick View
        # execute applescript
        result = subprocess.run(
                ['osascript',
                 '-e', 'tell application "Finder" to open POSIX file "{}"'.format(self.path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=str(self.path.parent)
            )