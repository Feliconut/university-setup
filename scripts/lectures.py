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
    class DocIndex():
        def __init__(self, v):
            pass

        def __compare__(self, other):
            pass

        def to_filename(self) -> str:
            raise NotImplementedError()

        @classmethod
        def from_filename(cls, filename: str):
            raise NotImplementedError()

    @classmethod
    def titleline_pattern(cls, index: DocIndex) -> str:
        raise NotImplementedError()

    @staticmethod
    def tex_cmd_name(x: DocIndex) -> str:
        raise NotImplementedError()

    @classmethod
    def match_range(cls, string, all_index) -> List[DocIndex]:

        def filter(ls):
            return [l for l in ls if l in all_index]

        if ',' in string:
            res = []
            for part in string.split(','):
                if part:
                    res += cls.match_range(part)
            return res

        if '-' in string:
            num_strs = string.split('-')
            # scan from left to right
            while num_strs:
                try:
                    if not num_strs[0]:
                        num_strs[0] = 'first'
                    cls.DocIndex(num_strs[0])
                    break
                except:
                    del num_strs[0]
            while num_strs:
                try:
                    if not num_strs[-1]:
                        num_strs[-1] = 'last'
                    cls.DocIndex(num_strs[-1])
                    break
                except:
                    del num_strs[-1]
            if num_strs:
                indices = [cls.DocIndex(n) for n in num_strs]
                return list(map(cls.DocIndex, filter(cls.range(indices[0], indices[-1]))))
            else:
                return []
        try:
            return filter([cls.DocIndex(string)])
        except:
            return []


class LinearLectureIndexSystem(DocIndexSystem):
    ''' The trivial index system for the documents.
    There is a 1-1 isomorphism between the indices and the filenames.
    There is an injection from indices to tex_cmd_name values.'''

    index_pattern = 'lec_*.tex'

    class DocIndex(int, DocIndexSystem.DocIndex):
        def to_filename(self) -> str:
            return 'lec_{0:02d}.tex'.format(self)

        @classmethod
        def from_filename(cls, filename: str):
            return cls(str(filename).replace('.tex', '').replace('lec_', ''))

        def __sub__(self, __x: int):
            return self.__class__(super().__sub__(__x))

        def __add__(self, __x: int):
            return self.__class__(super().__add__(__x))

    @classmethod
    def titleline_pattern(cls, index: DocIndex) -> str:
        return 'lecture' + r'\{(.*?)\}\{(.*?)\}\{(.*)\}'

    @staticmethod
    def tex_cmd_name(n: DocIndex) -> str:
        return '\\lecture' + '{' + str(n) + '}'

    @classmethod
    def range(cls, start: DocIndex, end: DocIndex) -> List[DocIndex]:
        return [cls.DocIndex(i) for i in range(start, end + 1)]

    @classmethod
    def new_index(cls, all_indices: List[DocIndex]):
        return max(all_indices, default=cls.DocIndex(0)) + 1


class Lecture():
    def __init__(self, file_path: Path):
        # read index from filenumber
        self.index = LinearLectureIndexSystem.DocIndex.from_filename(
            file_path.stem)

        with file_path.open('r+') as f:
            for line in f:
                doc_match = re.search(
                    LinearLectureIndexSystem.titleline_pattern(self.index), line)
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
    def __init__(self, path: Path):
        self.path = path
        self.master_file: Path = self.path / 'master.tex'
        self.documents = self.read_files()
        self.all_indices = [doc.index for doc in self.documents]

    def __iter__(self):
        return iter(self.documents)

    def __len__(self):
        return len(self.documents)

    def get_from_index(self, index: LinearLectureIndexSystem.DocIndex):
        for doc in self:
            if doc.index == index:
                return doc

    def read_files(self):
        files = self.path.glob(LinearLectureIndexSystem.index_pattern)
        return sorted((Lecture(f) for f in files), key=lambda l: l.index)

    def parse_doc_spec(self, string: str) -> LinearLectureIndexSystem.DocIndex:
        all_index = self.all_indices

        try:
            string = (string
                      .replace('last', str(all_index[-1]))
                      .replace('current', str(all_index[-1]))
                      .replace('prev', str(all_index[-2])))
            try:
                # may not be in all_index
                return LinearLectureIndexSystem.DocIndex(string)
            except:
                raise ValueError(f'Invalid spec: {string}')
        except IndexError:
            raise FileNotFoundError(f'This course is empty')

    def parse_range_string(self, string: str) -> List[LinearLectureIndexSystem.DocIndex]:
        all_index = self.all_indices

        if 'all' in string:
            return all_index
        string = (string
                  .replace('last', str(all_index[-1]))
                  .replace('current', str(all_index[-1]))
                  .replace('prev', str(all_index[-2])))

        return LinearLectureIndexSystem.match_range(string, all_index)

    @staticmethod
    def parse_master_range(filepath):
        part = 0
        header: str = ''
        footer: str = ''
        indices: List[LinearLectureIndexSystem.DocIndex] = []
        with filepath.open() as f:
            for line in f:
                # order of if-statements is important here!
                if 'end lectures' in line:
                    part = 2

                if part == 0:
                    header += line
                if part == 1:
                    # line = '\input{lec_01.tex}'
                    indices.append(LinearLectureIndexSystem.DocIndex.from_filename(
                        line.split('{')[1].split('}')[0]))
                if part == 2:
                    footer += line

                if 'start lectures' in line:
                    part = 1
        return (header, indices, footer)

    def update_docs_in_master(self, indices: List[LinearLectureIndexSystem.DocIndex]):
        'master.tex will only include the lectures in indices'

        header, _, footer = self.parse_master_range(self.master_file)
        body = ''.join(
            ' ' * 4 + r'\input{' + index.to_filename() + '}\n' for index in indices)
        self.master_file.write_text(header + body + footer)

    def update_master_from_range_string(self, string: str):
        indices = self.parse_range_string(string)
        self.update_docs_in_master(indices)

    def new_doc(self, name):
        name = name.strip()

        # assign a new index to the new document
        new_doc_index = LinearLectureIndexSystem.new_index(self.all_indices)
        new_doc_path = self.path / \
            new_doc_index.to_filename()
        assert not new_doc_path.exists()

        today = datetime.today()
        date = today.strftime(DATE_FORMAT)

        # write new document
        new_doc_path.touch()
        new_doc_path.write_text(
            f'\\{LinearLectureIndexSystem.tex_cmd_name(new_doc_index)}{{{date}}}{{{name}}}\n')

        # update master.tex
        _, indices, _ = self.parse_master_range(self.master_file)
        self.update_docs_in_master(indices + [new_doc_index])

        # reload documents to include the new document
        self.__init__(self.path)

        return Lecture(new_doc_path)

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
