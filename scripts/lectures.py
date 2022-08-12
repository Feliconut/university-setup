#!/usr/local/bin/python3

import locale
from pathlib import Path
import re
import subprocess
from datetime import datetime
from typing import List

from config import DATE_FORMAT, get_week

# TODO
#locale.setlocale(locale.LC_TIME, "en_US.utf8")
locale.setlocale(locale.LC_ALL, "en_US")


class DocIndexSystem():
    ''' The trivial index system for the documents.'''

    class DocIndex(int):
        pass

    def number2filename(n:DocIndex) -> str:
        return 'lec_{0:02d}.tex'.format(n)


    def filename2number(s:str) -> DocIndex:
        return int(str(s).replace('.tex', '').replace('lec_', ''))


class Lecture():
    doc_type_name = 'lecture'
    def __init__(self, file_path, course):
        with file_path.open() as f:
            for line in f:
                doc_match = re.search(
                    self.doc_type_name + r'\{(.*?)\}\{(.*?)\}\{(.*)\}', line)
                if doc_match:
                    break

        date_str = doc_match.group(2)
        date = datetime.strptime(date_str, DATE_FORMAT)
        week = get_week(date)

        title = doc_match.group(3)

        self.file_path = file_path
        self.date = date
        self.week = week
        self.index = DocIndexSystem.filename2number(file_path.stem)
        self.title = title
        self.course = course

    def edit(self):
        assert self.course.is_activated
        # TODO remember to set --servername in the editor synctex command also to `purdue`
        subprocess.call([
            f"source ~/.zshrc; mvim --servername purdue --remote-silent \"{str(self.file_path)}\"",
        ], shell=True)

    def __str__(self):
        return f'<{self.doc_type_name.capitalize()} {self.course.info["short"]} {self.index} "{self.title}">'


class Lectures():
    doc_type_name = 'lecture'


    def __init__(self, course):
        self.course = course
        self.root = course.path
        self.master_file: Path = self.root / 'master.tex'
        self.documents = self.read_files()
        self.all_indices = [doc.index for doc in self.documents]

    def __iter__(self):
        return iter(self.documents)

    def __len__(self):
        return len(self.documents)

    def get_from_index(self, index:DocIndexSystem.DocIndex):
        for doc in self:
            doc: Lecture
            if doc.index == index:
                return doc

    def read_files(self):
        files = self.root.glob('lec_*.tex')
        return sorted((Lecture(f, self.course) for f in files), key=lambda l: l.index)

    def parse_doc_spec(self, string):
        try:
            if string.isdigit():
                return int(string)
            elif string == 'last' or string == 'current':
                return self.documents[-1].index
            elif string == 'prev':
                return self.documents[-1].index - 1
            else:
                raise ValueError(f'Invalid spec: {string}')
        except IndexError:
            raise FileNotFoundError(f'This course is empty')

    def parse_range_string(self, arg):
        all_index = self.all_indices
        if 'all' in arg:
            return all_index

        def filter(ls):
            return [l for l in ls if l in all_index]

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
                    self.parse_doc_spec(nums[0])
                    break
                except:
                    del nums[0]
            while nums:
                try:
                    if not nums[-1]:
                        nums[-1] = 'last'
                    self.parse_doc_spec(nums[-1])
                    break
                except:
                    del nums[-1]
            if nums:
                return filter(list(range(self.parse_doc_spec(nums[0]), self.parse_doc_spec(nums[-1]) + 1)))
            else:
                return []
        try:
            return filter([self.parse_doc_spec(arg)])
        except:
            return []

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

    def update_docs_in_master(self, r :List[DocIndexSystem.DocIndex]):
        header, footer = self.get_header_footer(self.master_file)
        body = ''.join(
            ' ' * 4 + r'\input{' + DocIndexSystem.number2filename(index) + '}\n' for index in r)
        self.master_file.write_text(header + body + footer)

    def new_doc(self, name):
        if len(self) != 0:
            new_doc_index = self.documents[-1].index + 1
        else:
            new_doc_index = 1

        name = name.strip()

        new_doc_path = self.root / DocIndexSystem.number2filename(new_doc_index)
        assert not new_doc_path.exists()

        today = datetime.today()
        date = today.strftime(DATE_FORMAT)

        new_doc_path.touch()
        new_doc_path.write_text(
            f'\\{self.doc_type_name}{{{new_doc_index}}}{{{date}}}{{{name}}}\n')

        if new_doc_index == 1:
            self.update_docs_in_master([1])
        else:
            self.update_docs_in_master(
                [new_doc_index - 1, new_doc_index])

        self.read_files()

        l = Lecture(new_doc_path, self.course)

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
        if (self.root / 'master.pdf').exists():
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
        else:
            raise FileNotFoundError(
                f'{self.root / "master.pdf"} not found')
