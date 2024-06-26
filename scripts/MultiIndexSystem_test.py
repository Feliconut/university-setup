from lectures import MultiIndexSystem

Index = MultiIndexSystem.DocIndex
i = Index(('lecture', 1))
j = Index(('lecture', 3))

current_indices = [Index(('lecture', 1)),
                   Index(('lecture', 2)),
                   Index(('lecture', 3))]

# test creating new indices

print(MultiIndexSystem.new_index( current_indices,'lecture'))

print(MultiIndexSystem.new_index( current_indices,'lab'))

print(MultiIndexSystem.new_index( current_indices,'unknown'))

# test creation shorthand

print(current_indices[-1] + 3)

# test make_defline

print(MultiIndexSystem.make_defline(current_indices[-1], 'date', 'title'))

# test parse_defline

print(MultiIndexSystem.parse_defline(r'\lecture{4}{date}{title}'))


# test range generation
print(MultiIndexSystem.range(current_indices, i, j))

# test range generation with skipping indices

current_indices = [Index(('lecture', 1)),
                   Index(('lecture', 3)),
                   Index(('lecture', 4)), ]
print(MultiIndexSystem.range(current_indices, i, current_indices[-1]))

# test range generation with input indices too large and too small

print(MultiIndexSystem.range(current_indices, ('lecture', -1,), ('lecture', 20)))

# test range generation with different types of document

current_indices = [Index(('lecture', 1)),
                   Index(('lecture', 2)),
                   Index(('lab', 1)),
                   Index(('lab', 2)),
                   Index(('lecture', 3)),
                   Index(('lecture', 4)), ]
print(MultiIndexSystem.range(current_indices, i, current_indices[-1]))

# test range generation with different types of document and skipping indices

current_indices = [Index(('lecture', 1)),
                   Index(('lecture', 2)),
                   Index(('lab', 1)),
                   Index(('lab', 2)),
                   Index(('lecture', 4)), ]
print(MultiIndexSystem.range(current_indices, i, current_indices[-1]))

# test range generation with endpoints of different types of document

print(MultiIndexSystem.range(current_indices, i, Index(('lab', 2))))


# test range parsing with simple range strings

print(MultiIndexSystem.match_range('lecture 1 - lecture 2', current_indices, ))

# test range parsing with complex range strings

print(MultiIndexSystem.match_range('lecture 1 - 2', current_indices, ))

print(MultiIndexSystem.match_range(' 1 - 2', current_indices, ))

print(MultiIndexSystem.match_range('   lecture 1-7   ', current_indices, ))

print(MultiIndexSystem.match_range('  1- lab 7   ', current_indices, ))

print('should fail', MultiIndexSystem.match_range('  lecture 2 - lab 7   ', current_indices, ))
# this case should fail.

print(MultiIndexSystem.match_range('  lecture 2 - lab 2   ', current_indices, ))

# test compounded sentences with ,

print(MultiIndexSystem.match_range('lecture 1-2, lecture 2-3, lecture 3-4', current_indices, ))

print(MultiIndexSystem.match_range('lecture 1-3, lecture 2-lab 2, lecture 3-4', current_indices, ))

# test compounded sentences with 'sorted by'

print(MultiIndexSystem.match_range('lecture 1-2, sorted by date, lecture 2-3', current_indices, ))

# test simple sentences with 'first'

print(MultiIndexSystem.match_range('lecture first - lecture last', current_indices, ))
print(MultiIndexSystem.match_range('lecture first - lecture prev', current_indices, ))
print(MultiIndexSystem.match_range('lecture 2 - lecture last', current_indices, ))
print(MultiIndexSystem.match_range('lecture first - lecture 3', current_indices, ))
print(MultiIndexSystem.match_range('lecture first - lab last', current_indices, ))
print(MultiIndexSystem.match_range('lab first - lecture last', current_indices, ))
print(MultiIndexSystem.match_range('lab first - lecture 4', current_indices, ))
print('should fail', MultiIndexSystem.match_range('lab first - lecture 3', current_indices, ))

# test complex range with 'first'

print(MultiIndexSystem.match_range('lecture first - last', current_indices, ))
print(MultiIndexSystem.match_range('lecture first - prev', current_indices, ))
print(MultiIndexSystem.match_range(' 2 - lecture last', current_indices, ))
print(MultiIndexSystem.match_range(' first - lecture 3', current_indices, ))
print(MultiIndexSystem.match_range('lab first - last', current_indices, ))
print(MultiIndexSystem.match_range('lab first - lecture 4', current_indices, ))
print('should fail', MultiIndexSystem.match_range('lab first - lecture', current_indices, ))

# test complex range with 'all'

print(MultiIndexSystem.match_range('lecture all', current_indices, ))
print(MultiIndexSystem.match_range('all lecture', current_indices, ))
print('should fail',MultiIndexSystem.match_range(' all first lecture', current_indices, ))
print(MultiIndexSystem.match_range(' all', current_indices, ))

# test reversing arguments in each clause

print(MultiIndexSystem.match_range('first lecture - last', current_indices, ))
print(MultiIndexSystem.match_range('lecture first - prev', current_indices, ))
print(MultiIndexSystem.match_range(' 2 lecture - lecture last', current_indices, ))
print(MultiIndexSystem.match_range(' first -  3   lecture ', current_indices, ))
print(MultiIndexSystem.match_range(' first lab- last', current_indices, ))
print(MultiIndexSystem.match_range(' first    lab- lecture  4 ', current_indices, ))

# test entering single clause

print(MultiIndexSystem.match_range('first lecture , lab last', current_indices, ))
