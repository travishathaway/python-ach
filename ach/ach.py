from datetime import datetime

"""
Collection of class the comprise the row type objects
in a nacha file
"""

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

class AchHeader(Ach):
    """
    Creates our File Header record of the nacha file
    """

    def __init__(self, record_type_code, priority_code, immediate_dest,
                 immediate_org, file_id_mod, record_size, blk_factor,
                 format_code, im_dest_name, im_orgn_name, reference_code):
        """
        Initializes all values needed for 
        our header row
        """

        date = datetime.today()

        self.__record_type_code = record_type_code
        self.__priority_code    = priority_code
        self.__immediate_dest   = immediate_dest
        self.__immediate_org    = immediate_org
        self.__file_crt_date    = date.strftime('%y%m%d')
        self.__file_crt_time    = date.strftime('%M%S')
        self.__file_id_mod      = file_id_mod
        self.__record_size      = record_size
        self.__blk_factor       = blk_factor
        self.__format_code      = format_code
        self.__im_dest_name     = im_dest_name
        self.__im_orgn_name     = im_orgn_name
        self.__reference_code   = reference_code

    def get_row(self):
        """
        returns concatenated string of all parameters in
        nacha file
        """
        return self.__record_type_code +\
                self.__priority_code +\
                self.__immediate_dest +\
                self.__immediate_org +\
                self.__file_crt_date +\
                self.__file_crt_time +\
                self.__file_id_mod +\
                self.__record_size +\
                self.__blk_factor +\
                self.__format_code +\
                self.__im_dest_name +\
                self.__im_orgn_name +\
                self.__reference_code

    def get_char_count(self):
        """
        Returns length of all parameters in nach
        file
        """
        return len(self.__record_type_code +\
                self.__priority_code +\
                self.__immediate_dest +\
                self.__immediate_org +\
                self.__file_crt_date +\
                self.__file_crt_time +\
                self.__file_id_mod +\
                self.__record_size +\
                self.__blk_factor +\
                self.__format_code +\
                self.__im_dest_name +\
                self.__im_orgn_name +\
                self.__reference_code)

