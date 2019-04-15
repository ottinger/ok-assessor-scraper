# helpers.py
#
# Helper methods

# get_int()
#
# Converts an integer expressed as a string (with or without commas) to an integer.
#
# Example: get_int("4,000") returns 4000
def get_int(the_str):
    try:
        return int(the_str.replace(',', ''))
    except:
        return 0 # sometimes we will have blank input, see txns on PropertyID=151340 for example

# get_float()
#
# Converts a floating point number expressed as a string (with or without commas) to an integer.
#
# Example: get_float("1,234,567.89") returns 1234567.89
def get_float(the_str):
    try:
        return float(the_str.replace(',', ''))
    except: # most common if input is blank
        return 0.0

# get_sq_ft()
#
# Performs a nearly identical function to get_int(), used to convert square foot strings for
# buildings to integers. Main difference is that the function will return 0 if the string
# inputted is "1". (The assessor site sometimes sums the sq ft for multiple buildings into
# one row, then lists "1" on other rows.)
#
# Example: get_sqft("4,000") returns 4000. get_sqft("1") returns 0.
def get_sq_ft(the_str):
    if the_str == '': # sometimes there's a blank string, ie if land is vacant
        return 0
    x = int(the_str.replace(',', ''))
    return x if x != 1 else 0