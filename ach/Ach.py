
class Ach(object):
    """
    Base class for ACH record fields
    """

    def make_space(self, spaces=1):
        """
        Return string with x number of spaces
        Defaults to 1
        """
        space_string = ''

        for i in range(spaces - 1):
            space_string += ' '

        return space_string

    def make_zero(self, zeros=1):
        """
        Return string with x number of zeros
        Defaults to 1
        """
        zero_string = '0'

        for i in range(zeros - 1):
            zero_string += '0'

        return zero_string
