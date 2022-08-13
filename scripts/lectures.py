#!/usr/local/bin/python3

import locale
from pathlib import Path
import re
import subprocess
from datetime import datetime
from typing import List, Tuple

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
    def match_range(cls, string: str, all_index: List[DocIndex]) -> List[DocIndex]:
        raise NotImplementedError()

    @staticmethod
    def parse_defline(defline: str) -> List[str]:
        'Parse the defline and return the info. Throw an exception if the defline is invalid.'
        raise NotImplementedError()

    @staticmethod
    def make_defline(index: DocIndex, date: str, title: str) -> str:
        'The info is (index, date, title)'
        raise NotImplementedError()

    @classmethod
    def range(cls, start: DocIndex, end: DocIndex) -> List[DocIndex]:
        'Return a list of indices in the range [start, end]'
        raise NotImplementedError()

    @classmethod
    def new_index(cls, all_indices: List[DocIndex], *args) -> DocIndex:
        raise NotImplementedError()


class LinearLectureIndexSystem(DocIndexSystem):
    ''' The trivial index system for the documents.
    There is a 1-1 isomorphism between the indices and the valid filenames.
    '''

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

    @staticmethod
    def is_filename_valid(filename: str) -> bool:
        try:
            re.search('^lec_(.*).tex$', str(filename)).group(1).isdigit()
            return True
        except (AttributeError, IndexError):
            return False

    @staticmethod
    def parse_defline(defline: str) -> List[str]:
        'Parse the defline and return the info. Throw an exception if the defline is invalid.'
        # \lecture{1}{Sat 13 Aug 2022 02:07}{lecture title}
        m = re.match(
            r'^\\lecture\{(.*?)\}\{(.*?)\}\{(.*?)\}$', defline.strip())
        # throw error if not matched
        return [m.group(1), m.group(2), m.group(3)]

    @staticmethod
    def make_defline(index: DocIndex, date: str, title: str) -> str:
        'The info is (index, date, title)'
        return '\\lecture' + '{' + str(index) + '}' + '{' + date + '}' + '{' + title + '}'

    @classmethod
    def match_range(cls, string: str, all_index: List[DocIndex]) -> List[DocIndex]:
        string = string.replace('current', 'last')  # an alias

        if 'all' in string:
            return all_index

        # implicitly check if there are enough index entries
        string = string.replace('first', str(all_index[0]))
        string = string.replace('last', str(all_index[-1]))
        string = string.replace('prev', str(all_index[-2]))

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

    @classmethod
    def range(cls, start: DocIndex, end: DocIndex) -> List[DocIndex]:
        return [cls.DocIndex(i) for i in range(start, end + 1)]

    @classmethod
    def new_index(cls, all_indices: List[DocIndex], *args) -> DocIndex:
        return max(all_indices, default=cls.DocIndex(0)) + 1


class Lecture():
    def __init__(self, file_path: Path, index_system: DocIndexSystem):
        # read index from filenumber
        self.index_system = index_system
        self.index = index_system.DocIndex.from_filename(
            file_path.stem)

        with file_path.open('r+') as f:
            for line in f:
                try:
                    index_str, date_str, title = index_system.parse_defline(
                        line)
                    break
                except IndexError:
                    pass
            else:
                # no match. create title line

                title_line = index_system.make_defline(
                    self.index, datetime.now().strftime(DATE_FORMAT), '')
                f.seek(0, 0)  # point to the beginning of the file
                f.write(title_line)

                index_str, date_str, title = index_system.parse_defline(
                    title_line)

        date = datetime.strptime(date_str, DATE_FORMAT)
        week = get_week(date)

        self.file_path = file_path
        self.date = date
        self.week = week
        self.title = title

    def edit(self):
        # TODO remember to set --servername in the editor synctex command also to `purdue`
        subprocess.call([
            f"source ~/.zshrc; mvim -c \"lcd {str(self.file_path.parent)}\" --servername purdue --remote-silent \"{str(self.file_path)}\"",
        ], shell=True)

    def __str__(self):
        return f'<{self.__class__.__name__} {self.index} "{self.title}">'


class Lectures():
    def __init__(self, path: Path, index_system: DocIndexSystem = LinearLectureIndexSystem()):
        self.path = path
        self.index_system = index_system

        self.master_file: Path = self.path / 'master.tex'
        self.documents = self.read_files()
        self.all_indices = [doc.index for doc in self.documents]

    def __iter__(self):
        return iter(self.documents)

    def __len__(self):
        return len(self.documents)

    def get_from_index(self, index: DocIndexSystem.DocIndex):
        for doc in self:
            if doc.index == index:
                return doc

    def read_files(self):
        files = [file for file in self.path.iterdir(
        ) if self.index_system.is_filename_valid(file.name)]
        return sorted((Lecture(f, self.index_system) for f in files), key=lambda l: l.index)

    def parse_doc_spec(self, string: str) -> DocIndexSystem.DocIndex:
        all_index = self.all_indices
        try:
            return self.index_system.match_range(all_index, string+'-'+string)[0]
        except IndexError:
            raise FileNotFoundError(
                f'No file found for {string}. The course may be empty.')
        except:
            raise ValueError(f'Invalid index {string}')

    def parse_range_string(self, string: str) -> List[DocIndexSystem.DocIndex]:
        all_index = self.all_indices
        return self.index_system.match_range(string, all_index)

    def parse_master_range(self, filepath) -> Tuple[str, List[DocIndexSystem.DocIndex], str]:
        part = 0
        header: str = ''
        footer: str = ''
        indices: List[DocIndexSystem.DocIndex] = []
        with filepath.open() as f:
            for line in f:
                # order of if-statements is important here!
                if 'end lectures' in line:
                    part = 2

                if part == 0:
                    header += line
                if part == 1:
                    # line = '\input{lec_01.tex}'
                    indices.append(self.index_system.DocIndex.from_filename(
                        line.split('{')[1].split('}')[0]))
                if part == 2:
                    footer += line

                if 'start lectures' in line:
                    part = 1
        return (header, indices, footer)

    def update_docs_in_master(self, indices: List[DocIndexSystem.DocIndex]):
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
        new_doc_index = self.index_system.new_index(self.all_indices)
        new_doc_path = self.path / new_doc_index.to_filename()
        assert not new_doc_path.exists()

        today = datetime.today()
        date = today.strftime(DATE_FORMAT)

        # write new document
        new_doc_path.touch()
        new_doc_path.write_text(
            self.index_system.make_defline(new_doc_index, date, name))

        # update master.tex
        _, indices, _ = self.parse_master_range(self.master_file)
        self.update_docs_in_master(indices + [new_doc_index])

        # reload documents to include the new document
        self.__init__(self.path)

        return Lecture(new_doc_path, self.index_system)

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
