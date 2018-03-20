
# [Procedure calls]
# Why should we not track params to a function? because
# the input string may get progressively eaten rather than
# split recursively. So the input string variable actually
# causes more noise than signal.
Track_Params = False

Track_Vars = True

# Why we do not care about return values?
# * We expect the input value to be partitioned by each
#   procedure. Hence, the variables inside the procedures
#   are important. However, the return value of a given
#   procedure may not include the correct result. Even if
#   it did, it is probably already assigned an internal
#   variable (i.e: return my_val) in which case, we dont care
#   If not, (i.e: return i+j), the result may not represent
#   a sequence of input string.
Track_Return = False

# []

# Lambdas typicaly are unimportant, and contribute to noise.
Ignore_Lambda = True

# What should we do if we have a variable that eclipses already
# replaced variables?

Swap_Eclipsing_Keys = True

# [Verbosity]

Show_Colors = True

Show_Comparisons = False

Compress_Grammar = True

Prevent_Deep_Stack_Modification = False
