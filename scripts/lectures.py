#!/usr/local/bin/python3

import locale
from pathlib import Path
import re
import subprocess
from datetime import datetime

from config import DATE_FORMAT, get_week

# TODO
#locale.setlocale(locale.LC_TIME, "en_US.utf8")
locale.setlocale(locale.LC_ALL, "en_US")


def number2filename(n):
    return 'lec_{0:02d}.tex'.format(n)


def filename2number(s):
    return int(str(s).replace('.tex', '').replace('lec_', ''))


class Lecture():
    def __init__(self, file_path, course):
        with file_path.open() as f:
            for line in f:
                lecture_match = re.search(
                    r'lecture\{(.*?)\}\{(.*?)\}\{(.*)\}', line)
                if lecture_match:
                    break

        # number = int(lecture_match.group(1))

        date_str = lecture_match.group(2)
        date = datetime.strptime(date_str, DATE_FORMAT)
        week = get_week(date)

        title = lecture_match.group(3)

        self.file_path = file_path
        self.date = date
        self.week = week
        self.number = filename2number(file_path.stem)
        self.title = title
        self.course = course

    def edit(self):
        assert self.course.is_activated
        # TODO remember to set --servername in the editor synctex command also to `purdue`
        subprocess.call([
            f"source ~/.zshrc; mvim --servername purdue --remote-silent {str(self.file_path)}",
        ], shell=True)

    def __str__(self):
        return f'<Lecture {self.course.info["short"]} {self.number} "{self.title}">'


class Lectures(list):
    def __init__(self, course):
        self.course = course
        self.root = course.path
        self.master_file: Path = self.root / 'master.tex'
        list.__init__(self, self.read_files())
        self.all_numbers = [lecture.number for lecture in self]

    def get_from_number(self, number):
        for lecture in self:
            lecture: Lecture
            if lecture.number == number:
                return lecture

    def read_files(self):
        files = self.root.glob('lec_*.tex')
        return sorted((Lecture(f, self.course) for f in files), key=lambda l: l.number)

    def parse_lecture_spec(self, string):
        if string.isdigit():
            return int(string)
        elif string == 'last' or string == 'current':
            return self[-1].number
        elif string == 'prev':
            return self[-1].number - 1
        else:
            raise ValueError(f'Invalid lecture spec: {string}')

    def parse_range_string(self, arg):
        all_numbers = self.all_numbers
        if 'all' in arg:
            return all_numbers

        def filter(ls):
            return [l for l in ls if l in all_numbers]

        if ',' in arg:
            res = []
            for part in arg.split(','):
                if part:
                    res += self.parse_range_string(part)
            return res

        if '-' in arg:
            nums = arg.split('-')
            # scan from left to right
            while nums:
                try:
                    if not nums[0]:
                        nums[0] = 'first'
                    self.parse_lecture_spec(nums[0])
                    break
                except:
                    del nums[0]
            while nums:
                try:
                    if not nums[-1]:
                        nums[-1] = 'last'
                    self.parse_lecture_spec(nums[-1])
                    break
                except:
                    del nums[-1]
            if nums:
                return filter(list(range(self.parse_lecture_spec(nums[0]), self.parse_lecture_spec(nums[-1]) + 1)))
            else:
                return []
        return filter([self.parse_lecture_spec(arg)])

    @staticmethod
    def get_header_footer(filepath):
        part = 0
        header = ''
        footer = ''
        with filepath.open() as f:
            for line in f:
                # order of if-statements is important here!
                if 'end lectures' in line:
                    part = 2

                if part == 0:
                    header += line
                if part == 2:
                    footer += line

                if 'start lectures' in line:
                    part = 1
        return (header, footer)

    def update_lectures_in_master(self, r):
        header, footer = self.get_header_footer(self.master_file)
        body = ''.join(
            ' ' * 4 + r'\input{' + number2filename(number) + '}\n' for number in r)
        self.master_file.write_text(header + body + footer)

    def new_lecture(self, name):
        if len(self) != 0:
            new_lecture_number = self[-1].number + 1
        else:
            new_lecture_number = 1

        name = name.strip()

        new_lecture_path = self.root / number2filename(new_lecture_number)
        assert not new_lecture_path.exists()

        today = datetime.today()
        date = today.strftime(DATE_FORMAT)

        new_lecture_path.touch()
        new_lecture_path.write_text(
            f'\\lecture{{{new_lecture_number}}}{{{date}}}{{{name}}}\n')

        if new_lecture_number == 1:
            self.update_lectures_in_master([1])
        else:
            self.update_lectures_in_master(
                [new_lecture_number - 1, new_lecture_number])

        self.read_files()

        l = Lecture(new_lecture_path, self.course)

        return l

    def clean_latexmk(self):
        subprocess.call(['latexmk', '-c'], cwd=str(self.root))

    def compile_master(self):
        # self.clean_latexmk()
        result = subprocess.run(
            # ['pdflatex',str(self.master_file)],
            ['latexmk', '-f', '-interaction=nonstopmode',
                str(self.master_file)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=str(self.root)
        )
        return result.returncode

    def open_pdf(self):
        result = subprocess.run(
            ['osascript',
             '-e', 'tell application "Skim" to activate',
             '-e', 'set theFile to POSIX file "' +
             str(self.root / 'master.pdf') + '"',
             '-e', 'set thePath to POSIX path of (theFile as alias)',
             '-e', 'tell application "Skim"',
             '-e', 'try',
             '-e', 'set theDocs to get documents whose path is thePath',
             '-e', 'if (count of theDocs) > 0 then revert theDocs',
             '-e', 'end try',
             '-e', 'open theFile',
             '-e', 'end tell'
             ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=str(self.root)
        )
        return result.returncode
