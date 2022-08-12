#!/usr/local/bin/python3
from courses import courses

for course in courses:
        lectures = course.lectures
        course_title = course.info["title"]
        lines = [r'%&pdflatex',
                 r'\documentclass[a4paper]{article}',
                 r'\input{../preamble.tex}',
                 fr'\title{{{course_title}}}',
                 r'\begin{document}',
                 r'    \maketitle',
                 r'    \tableofcontents',
                 fr'    % start lectures',
                 fr'    % end lectures',
                 r'\end{document}'
                ]
        lectures.master_file.touch()
        lectures.master_file.write_text('\n'.join(lines))
        (lectures.path / 'master.tex.latexmain').touch()
        (lectures.path / 'figures').mkdir(exist_ok=True)
