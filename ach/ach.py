from datetime import datetime

import re
"""
Collection of class the comprise the row type objects
in a nacha file
"""

class AchException(Exception):
    pass

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

        for i in range(spaces):
            space_string += ' '

        return space_string

    def make_zero(self, zeros=1):
        """
        Return string with x number of zeros
        Defaults to 1
        """
        zero_string = ''

        for i in range(zeros):
            zero_string += '0'

        return zero_string

    def validate_alpha_numeric_field(self, field, length ):
        """
        Validates alpha numeric fields for nacha files
        field: (str)
        length: (int)
        """
        str_length = str(length)

        match = re.match(r'([\w,\s]{1,'+str_length+'})',field)

        if match:
            if len(match.group(1)) < length:
                field = match.group(1) + self.make_space( length - len(match.group(1)) )
            else:
                field = match.group(1)
        else:
            raise AchException("field does not match alpha numeric criteria")

        return field

    def validate_numeric_field(self, field, length):
        """
        Validates numeric field and zero right-pads if not 
        long enough.
        field (int|str)
        length (int)
        """
        field = str(field)

        if field.isdigit():
            if len(field) < length:
                field = self.make_zero( length - len(field) ) + field
            elif len(field) > length:
                raise AchException("field can only be "+length+" digits long")
        else:
            raise AchException("field needs to be numeric characters only")

        return field

    def validate_upper_num_field(self, field, length):
        """
        Validates upper case and numeric field
        field (int|str)
        length (int)
        """

        field = str(field)

        if field.isdigit():
            if len(field) > length:
                raise AchException("field exceeds length: "+length)
            elif len(field) < length:
                field = self.make_zero(length) + field
        elif field.isalpha():
            if len(field) > length:
                raise AchException("field exceeds length: "+length)
            elif len(field) < length:
                field = field + self.make_space(length)
        else:
            raise AchException("field is neith alpha or numeric")

        return field

class AchHeader(Ach):
    """
    Creates our File Header record of the nacha file
    """

    __record_size = '094'
    __blk_factor  = '10'
    __format_code = '1'

    def __init__(self, record_type_code, priority_code, immediate_dest,
                 immediate_org, file_id_mod,im_dest_name, im_orgn_name, 
                 reference_code):
        """
        Initializes all values needed for 
        our header row
        """

        date = datetime.today()

        self.__record_type_code = self.validate_numeric_field(record_type_code,1)
        self.__priority_code    = self.validate_numeric_field(priority_code,2)
        self.__immediate_dest   = immediate_dest # weird field, provided by bank
        self.__immediate_org    = immediate_org # again, weird field, provided by bank
        self.__file_crt_date    = date.strftime('%y%m%d')
        self.__file_crt_time    = date.strftime('%M%S')
        self.__file_id_mod      = self.validate_upper_num_field(file_id_mod,1)
        self.__im_dest_name     = self.validate_alpha_numeric_field(im_dest_name,23)
        self.__im_orgn_name     = self.validate_alpha_numeric_field(im_orgn_name,23)
        self.__reference_code   = self.validate_alpha_numeric_field(reference_code)

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

