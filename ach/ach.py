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

class AchFileControl(Ach):
    """
    Comprises the control record for an ACH file
    Appears at the end of file
    """

    __record_type_code = '9'

    def __init__(self, batch_count, block_count, 
                 entadd_count, entry_hash, debit_amount,
                 credit_amount):
        """
        Initializes all the values we need for our file control record
        """
        
        debit_amount = int((100 * debit_amount))
        credit_amount = int((100 * credit_amount)) 

        self.__batch_count   = self.validate_numeric_field( batch_count, 6)
        self.__block_count   = self.validate_numeric_field( block_count, 6)
        self.__entadd_count  = self.validate_numeric_field( entadd_count, 8)
        self.__entry_hash    = self.validate_numeric_field( entry_hash, 10)
        self.__debit_amount  = self.validate_numeric_field( debit_amount , 12)
        self.__credit_amount = self.validate_numeric_field( credit_amount, 12)
        self.__reserved      = self.make_space(39)

    def get_row(self):

        return self.__record_type_code +\
                self.__batch_count +\
                self.__block_count +\
                self.__entadd_count +\
                self.__entry_hash +\
                self.__debit_amount +\
                self.__credit_amount +\
                self.__reserved

    def get_count(self):

         return len(self.__record_type_code +\
                self.__batch_count +\
                self.__block_count +\
                self.__entadd_count +\
                self.__entry_hash +\
                self.__debit_amount +\
                self.__credit_amount +\
                self.__reserved)

class AchBatchHeader(Ach):

    __record_type_code = '5'

    std_ent_cls_code_list = [ 'ARC', 'PPD', 'CTX', 'POS', 'WEB',
                                'BOC', 'TEL', 'MTE', 'SHR', 'CCD',
                                'CIE', 'POP', 'RCK' ]

    serv_cls_code_list  = ['200', '220', '225']

    def __init__(self,serv_cls_code, company_name, cmpy_dis_data, 
                    company_id, std_ent_cls_code, entry_desc, desc_date,
                    eff_ent_date, settlement_date, orig_stat_code,
                    orig_dfi_id, batch_id):
        """
        Initializes and validates the values for our Batch Header
        rows
        """

        if str(serv_cls_code) not in serv_cls_code_list:
            raise AchException("serv_cls_code not valid. Choose 200, 220, 225")
        self.__serv_cls_code    = self.validate_numeric_field( serv_cls_code, 3 )

        self.__company_name     = self.validate_alpha_numeric_field( company_name, 16 )
        self.__cmpy_dis_data    = self.validate_alpha_numeric_field( cmpy_dis_data, 20 )
        self.__company_id       = self.validate_alpha_numeric_field( company_id, 10 )

        if str(std_ent_cls_code) not in std_ent_cls_code_list:
            raise AchException("std_ent_cls_code not in std_ent_cls_code_list")
        self.__std_ent_cls_code = self.validate_alpha_numeric_field( std_ent_cls_code, 3 )

        self.__entry_desc       = self.validate_alpha_numeric_field( entry_desc, 10 )
        self.__desc_date        = self.validate_alpha_numeric_field( desc_date, 6 )
        self.__eff_ent_date     = self.validate_numeric_field( eff_ent_date, 6 )
        self.__settlement_date  = self.make_space( 3 )
        self.__orig_stat_code   = self.validate_numeric_field( orig_stat_code, 1 )
        self.__orig_dfi_id      = self.validate_numeric_field( orig_dfi_id, 8 )
        self.__batch_id         = self.validate_numeric_field( batch_id, 7 )

    def get_row(self):

        return self.__serv_cls_code +\
               self.__company_name +\
               self.__cmpy_dis_data +\
               self.__company_id +\
               self.__std_ent_cls_code +\
               self.__entry_desc +\
               self.__desc_date +\
               self.__eff_ent_date +\
               self.__settlement_date +\
               self.__orig_stat_code +\
               self.__orig_dfi_id +\
               self.__batch_id

    def get_count(self):

        return len(self.__serv_cls_code +\
                   self.__company_name +\
                   self.__cmpy_dis_data +\
                   self.__company_id +\
                   self.__std_ent_cls_code +\
                   self.__entry_desc +\
                   self.__desc_date +\
                   self.__eff_ent_date +\
                   self.__settlement_date +\
                   self.__orig_stat_code +\
                   self.__orig_dfi_id +\
                   self.__batch_id)

class AchBatchControl(Ach):

    __record_type_code = '8'

    def __init__(self, serv_cls_code, entadd_count, entry_hash,
                    debit_amount, credit_amount, company_id, mesg_auth_code='',
                    orig_dfi_id, batch_id):
        """
        Initializes and validates the batch control record
        """
        
        debit_amount = int((100 * debit_amount))
        credit_amount = int((100 * credit_amount)) 

        self.__serv_cls_code    = self.validate_numeric_field( serv_cls_code, 3 )
        self.__entadd_count     = self.validate_numeric_field( entadd_count, 6 )
        self.__entry_hash       = self.validate_numeric_field( entry_hash, 10 )
        self.__debit_amount     = self.validate_numeric_field( debit_amount, 12 )
        self.__credit_amount    = self.validate_numeric_field( credit_amount, 12 )
        self.__company_id       = self.validate_alpha_numeric_field( company_id, 10 )

        # Field usually left blank, but lets see if it's not
        if mesg_auth_code == '':
            self.__mesg_auth_code = self.make_space(19)
        else:
            self.__mesg_auth_code = self.validate_alpha_numeric_field( mesg_auth_code, 19)
        
        self.__orig_dfi_id      = self.validate_numeric_field( orig_dfi_id, 8 )
        self.__batch_id         = self.validate_numeric_field( batch_id, 7 )


    def get_row(self):

        return self.__serv_cls_code +\
               self.__entadd_count +\
               self.__entry_hash +\
               self.__debit_amount +\
               self.__credit_amount +\
               self.__company_id +\
               self.__mesg_auth_code +\
               self.__orig_dfi_id +\
               self.__batch_id 

    def get_count(self):

        return len(self.__serv_cls_code +\
                   self.__entadd_count +\
                   self.__entry_hash +\
                   self.__debit_amount +\
                   self.__credit_amount +\
                   self.__company_id +\
                   self.__mesg_auth_code +\
                   self.__orig_dfi_id +\
                   self.__batch_id)

