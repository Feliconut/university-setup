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
    ''' The trivial index system for the documents.
    There is a 1-1 isomorphism between the indices and the filenames.
    There is an injection from indices to tex_cmd_name values.'''

    index_pattern = 'lec_*.tex'

    class DocIndex(int):
        pass

    @staticmethod
    def number2filename(n: DocIndex) -> str:
        return 'lec_{0:02d}.tex'.format(n)

    @staticmethod
    def filename2number(s: str) -> DocIndex:
        return int(str(s).replace('.tex', '').replace('lec_', ''))

    @staticmethod
    def tex_cmd_name(n: DocIndex) -> str:
        return 'lecture'

    @staticmethod
    def match_range(string, all_index) -> List[DocIndex]:

        def filter(ls):
            return [l for l in ls if l in all_index]

        if ',' in string:
            res = []
            for part in string.split(','):
                if part:
                    res += DocIndexSystem.match_range(part)
            return res

        if '-' in string:
            nums = string.split('-')
            # scan from left to right
            while nums:
                try:
                    if not nums[0]:
                        nums[0] = 'first'
                    DocIndexSystem.DocIndex(nums[0])
                    break
                except:
                    del nums[0]
            while nums:
                try:
                    if not nums[-1]:
                        nums[-1] = 'last'
                    DocIndexSystem.DocIndex(nums[-1])
                    break
                except:
                    del nums[-1]
            if nums:
                return filter(list(range(DocIndexSystem.DocIndex(nums[0]), DocIndexSystem.DocIndex(nums[-1]) + 1)))
            else:
                return []
        try:
            return filter([DocIndexSystem.DocIndex(string)])
        except:
            return []


class Lecture():
    def __init__(self, file_path):
        # read index from filenumber
        self.index = DocIndexSystem.filename2number(file_path.stem)

        with file_path.open() as f:
            for line in f:
                doc_match = re.search(
                    DocIndexSystem.tex_cmd_name(self.index) + r'\{(.*?)\}\{(.*?)\}\{(.*)\}', line)
                if doc_match:
                    break

        date_str = doc_match.group(2)
        date = datetime.strptime(date_str, DATE_FORMAT)
        week = get_week(date)

        title = doc_match.group(3)

        self.file_path = file_path
        self.date = date
        self.week = week
        self.title = title

    def edit(self):
        # TODO remember to set --servername in the editor synctex command also to `purdue`
        subprocess.call([
            f"source ~/.zshrc; mvim --servername purdue --remote-silent \"{str(self.file_path)}\"",
        ], shell=True)

    def __str__(self):
        return f'<{self.__class__.__name__} {self.index} "{self.title}">'


class Lectures():
    doc_type_name = 'lecture'

    def __init__(self, path: Path):
        self.path = path
        self.master_file: Path = self.path / 'master.tex'
        self.documents = self.read_files()
        self.all_indices = [doc.index for doc in self.documents]

    def __iter__(self):
        return iter(self.documents)

    def __len__(self):
        return len(self.documents)

    def get_from_index(self, index: DocIndexSystem.DocIndex):
        for doc in self:
            doc: Lecture
            if doc.index == index:
                return doc

    def read_files(self):
        files = self.path.glob(DocIndexSystem.index_pattern)
        return sorted((Lecture(f) for f in files), key=lambda l: l.index)

    def parse_doc_spec(self, string: str) -> DocIndexSystem.DocIndex:
        all_index = self.all_indices

        try:
            string = (string
                      .replace('last', str(all_index[-1]))
                      .replace('current', str(all_index[-1]))
                      .replace('prev', str(all_index[-2])))
            try:
                # may not be in all_index
                return DocIndexSystem.DocIndex(string)
            except:
                raise ValueError(f'Invalid spec: {string}')
        except IndexError:
            raise FileNotFoundError(f'This course is empty')

    def parse_range_string(self, string: str) -> List[DocIndexSystem.DocIndex]:
        all_index = self.all_indices

        if 'all' in string:
            return all_index
        string = (string
                  .replace('last', str(all_index[-1]))
                  .replace('current', str(all_index[-1]))
                  .replace('prev', str(all_index[-2])))

        return DocIndexSystem.match_range(string, all_index)

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

    def update_docs_in_master(self, r: List[DocIndexSystem.DocIndex]):
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

        new_doc_path = self.path / \
            DocIndexSystem.number2filename(new_doc_index)
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

        l = Lecture(new_doc_path)

        return l

    def clean_latexmk(self):
        subprocess.call(['latexmk', '-c'], cwd=str(self.path))

    def compile_master(self):
        # self.clean_latexmk()
        result = subprocess.run(
            # ['pdflatex',str(self.master_file)],
            ['latexmk', '-f', '-interaction=nonstopmode',
                str(self.master_file)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=str(self.path)
        )
        return result.returncode

    def open_pdf(self):
        if (self.path / 'master.pdf').exists():
            result = subprocess.run(
                ['osascript',
                 '-e', 'tell application "Skim" to activate',
                 '-e', 'set theFile to POSIX file "' +
                 str(self.path / 'master.pdf') + '"',
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
                cwd=str(self.path)
            )
            return result.returncode
        else:
            raise FileNotFoundError(
                f'{self.path / "master.pdf"} not found')
