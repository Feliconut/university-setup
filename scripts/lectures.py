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

        def __format__(self, format_spec):
            raise NotImplementedError()

    @staticmethod
    def is_filename_valid(filename: str) -> bool:
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
    def range(cls, all_indices: List[DocIndex], start: DocIndex, end: DocIndex) -> List[DocIndex]:
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
            return 'lecture_{0:02d}.tex'.format(self)

        @classmethod
        def from_filename(cls, filename: str):
            return cls(str(filename).replace('.tex', '').replace('lecture_', ''))

        def __sub__(self, __x: int):
            return self.__class__(super().__sub__(__x))

        def __add__(self, __x: int):
            return self.__class__(super().__add__(__x))

    @staticmethod
    def is_filename_valid(filename: str) -> bool:
        try:
            re.search('^lecture_(.*).tex$', str(filename)).group(1).isdigit()
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
                return list(map(cls.DocIndex, filter(cls.range(all_index, indices[0], indices[-1]))))
            else:
                return []
        try:
            return filter([cls.DocIndex(string)])
        except:
            return []

    @classmethod
    def range(cls, all_indices: List[DocIndex], start: DocIndex, end: DocIndex) -> List[DocIndex]:
        return [cls.DocIndex(i) for i in range(start, end + 1)]

    @classmethod
    def new_index(cls, all_indices: List[DocIndex], *args) -> DocIndex:
        return max(all_indices, default=cls.DocIndex(0)) + 1


class MultiIndexSystem(DocIndexSystem):
    ''' This index system allows different types of docs,
    e.g. lecture, lab, homework, ...
    Each type of doc have a linear order. All docs together
    can be ordered by their creation sequence.
    This index system is backward compatible with the `LinearLectureIndexSystem`.'''

    RESERVED_WORDS = ['current', 'first', 'last', 'prev', 'all',
                      'latest', 'next', 'previous', 'earliest',
                      'oldest', 'newest', 'sorted', 'by', 'date',
                      'title', 'desc', 'asc', 'descending', 'ascending',
                      'time']
    # current = last = latest = newest = end
    # first = earliest = oldest = start
    # prev = previous
    # desc = descending
    # asc = ascending

    # The DocIndex is a tuple of (type, index)

    class DocIndex(tuple, DocIndexSystem.DocIndex):
        # def __new__(cls, type, index):
        #     return super().__new__(cls, (type, index))

        def __init__(self, *args):
            super().__init__(*args)
            try:
                assert len(self) == 2
            except AssertionError:
                raise ValueError('DocIndex must be a tuple of (type, index)')
            type_name, num = self
            type_name: str
            num: int
            # name must no be in RESERVED_WORDS
            try:
                assert type_name not in MultiIndexSystem.RESERVED_WORDS
            except AssertionError:
                raise ValueError(
                    'DocIndex type name must not be in RESERVED_WORDS')
            try:
                assert type_name.isalpha()
            except AssertionError:
                raise ValueError('DocIndex type must be an alphabetic word')
            try:
                assert isinstance(num, int)
                assert num >= 1
            except AssertionError:
                raise ValueError('DocIndex index must be a positive integer')

        def __compare__(self, other: Tuple[str, int]):
            if self[0] == other[0]:
                return self[1] - other[1]
            return super().__cmp__(other)  # same as __eq__

        def to_filename(self) -> str:
            return '{0}_{1:02d}.tex'.format(self[0], self[1])

        @classmethod
        def from_filename(cls, filename: str):
            return cls((str(filename).replace('.tex', '').split('_')[0],
                       int(str(filename).replace('.tex', '').split('_')[1])))

        # syntactic sugar to create new index

        def __sub__(self, __x: int):
            return self.__class__((self[0], self[1]-__x))

        def __add__(self, __x: int):
            return self.__class__((self[0], self[1]+__x))

        def __format__(self, format_spec):
            return '{0} {1:02d}'.format(self[0][:3].capitalize(), self[1])

    @staticmethod
    def is_filename_valid(filename: str) -> bool:
        try:
            assert re.search('^([a-z]+)_(.*).tex$', str(filename)).group(1)
            assert re.search('^([a-z]+)_(.*).tex$',
                             str(filename)).group(2).isdigit()
            return True
        except (AssertionError, AttributeError, IndexError):
            return False

    @staticmethod
    def parse_defline(defline: str) -> List[str]:
        'Parse the defline and return the info. Throw an exception if the defline is invalid.'
        m = re.match(
            r'^\\([a-z]+)\{(.*?)\}\{(.*?)\}\{(.*?)\}$', defline.strip())
        # throw error if not matched
        return [str((m.group(1), m.group(2))), m.group(3), m.group(4)]

    @staticmethod
    def make_defline(index: DocIndex, date: str, title: str) -> str:
        'The info is (index, date, title)'
        return '\\{0}'.format(index[0]) + '{' + str(index[1]) + '}' + '{' + date + '}' + '{' + title + '}'

    @classmethod
    def match_range(cls, string: str, all_index: List[DocIndex]) -> List[DocIndex]:
        # example prompt:
        # lecture 1-5, lab 1, homework 2
        # lecture 1-5, lab 1-2, homework 2-last, current
        # last lecture, current
        # all lecture, all lab, sorted by date

        def position_num(position_string: str, type_str: str) -> int:
            ''' resolve the position string to a list of DocIndex '''

            all_num = [i[1]
                       for i in all_index if i[0] == type_str or not type_str]
            position_string = position_string.strip()
            if position_string in 'current last latest newest end'.split():
                return all_num[-1]
            elif position_string in 'first earliest oldest start'.split():
                return all_num[0]
            elif position_string in 'prev previous'.split():
                try:
                    return all_num[-2]
                except IndexError:
                    return all_num[-1]
            elif position_string.isdigit():
                # if int(position_string) in all_num:
                return int(position_string)
            return False

        def parse_clause(spec_str) -> cls.DocIndex:
            # replace any number of space with a single space
            spec_str = re.sub(r'\s+', ' ', spec_str)

            try:
                start = spec_str.strip()
                start_type, start_pos = start.split(' ')  # reverse order
                start_num = position_num(start_pos, start_type)
                start_index = cls.DocIndex((start_type, start_num))
                return start_index
            except:
                pass
            try:
                start = spec_str.strip()
                start_pos, start_type = start.split(' ')  # reverse order
                start_num = position_num(start_pos, start_type)
                start_index = cls.DocIndex((start_type, start_num))
                return start_index
            except:
                pass
            raise ValueError('Invalid spec: {0}'.format(spec_str))

        def parse_complex_range(range_str) -> List[cls.DocIndex]:
            # example prompt:
            # lecture 1 - lecture 5
            # lecture 1 - 5
            # lecture 2 - lab 3
            # 2 - lab 3
            # 2 - 3

            range_str = range_str.strip()
            # TODO add something here to make it more tolerant to typos
            try:
                start, end = range_str.strip().split('-')
                start_index = parse_clause(start)
                end_index = parse_clause(end)
                return cls.range(all_index, start_index, end_index)
            except:
                pass
            try:  # assume it is of the form "1 - 5"
                # use 'lecture' as a default type
                start, end = range_str.split('-')
                start = start.strip()
                end = end.strip()
                type_str = 'lecture'
                return cls.range(all_index,
                                 parse_clause(type_str + ' ' + start),
                                 parse_clause(type_str + ' ' + end))

            except:
                pass
            try:  # assume one side if a index and the other side is a number.
                # apply the same type to both sides.
                start, end = range_str.split('-')
                start_index = end_index = None
                try:
                    start_index = parse_clause(start)
                except:
                    pass
                try:
                    end_index = parse_clause(end)
                except:
                    pass
                if start_index:
                    assert position_num(end, start_index[0])
                    return cls.range(all_index, start_index,
                                     parse_clause(start_index[0] + ' ' + str(position_num(end, start_index[0]))))
                if end_index:
                    assert position_num(start, end_index[0])
                    return cls.range(all_index, parse_clause(end_index[0] + ' ' + str(position_num(start, end_index[0]))), end_index)
            except:
                pass
            raise ValueError('Invalid range: {0}'.format(range_str))

        def parse_sorting_info(sorting_sentence: str):
            'Parse the sorting info. Return the sorter function that can be used to sort the list.'
            # example prompt:
            # sorted by date
            # sorted by date desc
            # sorted by title asc
            assert 'sort' in sorting_sentence.lower()

            reverse = False

            sorting_sentence = (sorting_sentence
                                .replace('sorted by', '')
                                .replace('sorted', '')
                                .replace('sort', '')
                                .replace('by', '')
                                .replace('asc', '')  # ascending is a default
                                .strip())
            if 'desc' in sorting_sentence:
                reverse = True
                sorting_sentence = sorting_sentence.replace('desc', '').strip()

            # now it must be alphabetical
            if not sorting_sentence.isalpha():
                # return trivial sorter
                raise ValueError(
                    'Invalid sorting info: {0}'.format(sorting_sentence))

            attr_name = sorting_sentence.lower()

            def sort(documents: Lecture, reverse: bool = False) -> List[Lecture]:
                'Sort the list of documents by the date.'
                try:
                    return sorted(documents, key=lambda x: getattr(x, attr_name), reverse=reverse)
                except AttributeError:
                    return documents
            return sort

        parsed_range = []
        def sorter(x): return x
        for sentence in string.split(','):
            sentence = sentence.strip()
            # try to parse it as a sorting info
            try:
                sorter = parse_sorting_info(sentence)
                continue
            except:
                pass
            # try to parse it as an 'all' sentence. ex: all lecture, all lab, all homework
            try:
                assert 'all' in sentence
                sentence = sentence.replace('all', '').strip()
                type_str = sentence.lower()
                assert type_str.isalpha() or not type_str
                parsed_range.extend(
                    [i for i in all_index if i[0] == type_str or not type_str])
                continue
            except:
                pass
            # try to parse it as a clause
            try:
                parsed_range.append(parse_clause(sentence))
                continue
            except:
                pass
            # try to parse it as a range
            try:
                parsed_range.extend(parse_complex_range(sentence))
                continue
            except ValueError:
                pass
            # do nothing with this command
            # warn the user
            print('Warning: invalid command: {0}'.format(sentence))

        return parsed_range  # TODO sorter feature

    @classmethod
    def range(cls, all_indices: List[DocIndex], start: DocIndex, end: DocIndex) -> List[DocIndex]:
        'Return a list of indices in the range [start, end]'
        # start and end are of the same type
        if start[0] == end[0]:
            return [i for i in all_indices if i[0] == start[0] and i[1] >= start[1] and i[1] <= end[1]]
        else:
            # the items located between start and end in all_indices
            try:
                return all_indices[all_indices.index(start):all_indices.index(end)+1]
            except IndexError:
                raise ValueError('start and end must be in all_index')

    @classmethod
    def new_index(cls, all_indices: List[DocIndex], type_str=None) -> DocIndex:
        if not type_str:
            if not all_indices:
                type_str = 'lecture'
            else:
                type_str = all_indices[-1][0]
        matched_indices = [i for i in all_indices if i[0] == type_str]
        if not matched_indices:
            return cls.DocIndex((type_str, 1))
        else:
            return matched_indices[-1] + 1


class Lecture():
    def __init__(self, file_path: Path, index_system: DocIndexSystem):
        # read index from filenumber
        self.index_system = index_system
        self.index: index_system.DocIndex = index_system.DocIndex.from_filename(
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
    def __init__(self, path: Path, index_system: DocIndexSystem = MultiIndexSystem()):
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

    def read_files(self) -> List[Lecture]:
        files = [file for file in self.path.iterdir(
        ) if self.index_system.is_filename_valid(file.name)]
        return sorted((Lecture(f, self.index_system) for f in files), key=lambda l: l.index)

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
                    indices.append(self.index_system.DocIndex.from_filename(
                        line.split('{')[1].split('}')[0]))
                if part == 2:
                    footer += line

                if 'start lectures' in line:
                    part = 1
        return (header, indices, footer)

    def get_all_doc_types(self) -> List[str]:
        return sorted(set(doc.index[0] for doc in self))

    def update_docs_in_master(self, indices: List[DocIndexSystem.DocIndex]):
        'master.tex will only include the lectures in indices'

        header, _, footer = self.parse_master_range(self.master_file)
        body = ''.join(
            ' ' * 4 + r'\input{' + index.to_filename() + '}\n' for index in indices)
        self.master_file.write_text(header + body + footer)

    def update_master_from_range_string(self, string: str):
        indices = self.parse_range_string(string)
        self.update_docs_in_master(indices)

    def new_doc(self, name, type_name='lecutre'):
        name = name.strip()

        # assign a new index to the new document
        new_doc_index = self.index_system.new_index(
            self.all_indices, type_name)
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
