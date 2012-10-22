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

    def validate_binary_field(self, field ):
        """
        Validates binary string field (either '1' or '0')
        """

        if field not in ['1','0']:
            raise AchException("filed not '1' or '0'")
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
                    debit_amount, credit_amount, company_id, 
                    orig_dfi_id, batch_id, mesg_auth_code=''):
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

class AchEntryDetail(Ach):
    """
    Object represents a single Entry Detail record of an ACH file
    """

    record_type_code = '6'

    std_ent_cls_code_list = [ 'ARC', 'PPD', 'CTX', 'POS', 'WEB',
                                'BOC', 'TEL', 'MTE', 'SHR', 'CCD',
                                'CIE', 'POP', 'RCK' ]

 
    numeric_fields = ['transaction_code', 'recv_dfi_id', 'check_digit',
                        'amount', 'num_add_recs', 'card_exp_date' ,'doc_ref_num',
                        'ind_card_acct_num', 'card_tr_typ_code_shr', 'trace_num']

    alpha_numeric_fields = [ 'dfi_acnt_num', 'chk_serial_num', 'ind_name',
                                'disc_data', 'id_number', 'recv_cmpy_name',
                                'terminal_city', 'terminal_state',
                                'card_tr_typ_code_pos', 'pmt_type_code']

    field_lengths = {
        'transaction_code'      : 2,
        'recv_dfi_id'           : 8,
        'check_digit'           : 1,
        'dfi_acnt_num'          : 17,
        'amount'                : 10,
        'chk_serial_num'        : [9, #POP
                                    15,], #ARC, BOC
        'ind_name'              : [15, #CIE, MTE
                                    22,], #ARC, BOC, CCD, PPD, TEL, POP, POS, WEB
        'disc_data'             : 2,
        'id_number'             : 15,
        'ind_id'                : 22,
        'num_add_recs'          : 4,
        'recv_cmpy_name'        : 16,
        'reserved'              : 2,
        'terminal_city'         : 4,
        'terminal_state'        : 2,
        'card_tr_typ_code_pos'  : 2,
        'card_tr_typ_code_shr'  : 2,
        'card_exp_date'         : 4,
        'doc_ref_num'           : 11,
        'ind_card_acct_num'     : 22,
        'pmt_type_code'         : 2,
        'trace_num'             : 15,
    }

    def __init__(self, std_ent_cls_code, transaction_code='',recv_dfi_id='', check_digit='',
                    amount='', num_add_recs='', card_exp_date='' ,doc_ref_num='',
                    ind_card_acct_num='', card_tr_typ_code_shr='', card_tr_typ_code_pos='',
                    trace_num='', dfi_acnt_num='', ind_name='', disc_data='', id_number='', 
                    recv_cmpy_name='', chk_serial_num='', terminal_city='', terminal_state='', 
                    pmt_type_code=''):
        """
        Initialize and validate the values in Entry Detail record
        """
        self.std_ent_cls_code = std_ent_cls_code

        if transaction_code != '':
            self.transaction_code = transaction_code
        else:
            self.transaction_code = self.make_zero(2)

        if recv_dfi_id != '':
            self.recv_dfi_id = recv_dfi_id
        else:
            self.recv_dfi_id = self.make_zero(8)

        if check_digit != '':
            self.check_digit = check_digit
        else:
            self.check_digit = self.make_zero(1)

        if amount != '':
            self.amount = amount
        else:
            self.amount = self.make_zero(10)

        if num_add_recs != '':
            self.num_add_recs = num_add_recs
        else:
            self.num_add_recs = self.make_zero(4)

        if card_exp_date != '':
            self.card_exp_date = card_exp_date
        else:
            self.card_exp_date = self.make_zero(4)

        if doc_ref_num != '':
            self.doc_ref_num = doc_ref_num
        else:
            self.doc_ref_num = self.make_zero(11)

        if ind_card_acct_num != '':
            self.ind_card_acct_num = ind_card_acct_num
        else:
            self.ind_card_acct_num = self.make_zero(22)

        if card_tr_typ_code_shr != '':
            self.card_trans_type_code_shr = card_tr_typ_code_shr
        else:
            self.card_tr_typ_code_shr = self.make_zero(2)

        if trace_num != '':
            self.trace_num = trace_num
        else:
            self.trace_num = self.make_zero(15)

        if card_tr_typ_code_pos != '':
            self.card_tr_typ_code_pos = card_tr_typ_code_pos
        else:
            self.card_tr_typ_code_pos = self.make_space(2)

        if dfi_acnt_num != '':
            self.dfi_acnt_num = dfi_acnt_num
        else:
            self.dfi_acnt_num = self.make_zero(17)

        if ind_name != '':
            self.ind_name = ind_name
        elif self.std_ent_cls_code in ['CIE','MTE']:
            self.ind_name = self.make_zero(15)
        else:
            self.ind_name = self.make_zero(22)

        if disc_data != '':
            self.disc_data = disc_data
        else:
            self.disc_data = self.make_zero(2)

        if id_number != '':
            self.id_number = id_number
        else:
            self.id_number = self.make_zero(15)

        if recv_cmpy_name != '':
            self.recv_cmpy_name = recv_cmpy_name
        else:
            self.recv_cmpy_name = self.make_space(16)

        if chk_serial_num != '':
            self.chk_serial_num = chk_serial_num
        elif self.std_ent_cls_code == 'POP':
            self.chk_serial_num = self.make_space(9)
        else:
            self.chk_serial_num = self.make_space(15)

        if terminal_city != '':
            self.terminal_city = terminal_city
        else:
            self.terminal_city = self.make_space(4)

        if terminal_state != '':
            self.terminal_state = terminal_state
        else:
            self.terminal_state = self.make_space(2)

        if pmt_type_code != '':
            self.pmt_type_code = pmt_type_code
        else:
            self.pmt_type_code = self.make_space(2)

    def __setattr__(self, name, value):
        """
        Overides the setattr method for the object. We do this so
        that we can validate the field as it gets assigned. 
        """

        if name in self.alpha_numeric_fields:
            # Special handling for Indvidiual/Company name field
            if name == 'ind_name' and self.std_ent_cls_code in ['CIE', 'MTE']:
                value = self.validate_alpha_numeric_field( value, self.field_lengths[name][0] )
            elif name == 'ind_name':
                value = self.validate_alpha_numeric_field( value, self.field_lengths[name][1] )
            
            # Special handling for Check serial number field
            elif name == 'chk_serial_num' and self.std_ent_cls_code_list == 'POP':
                value = self.validate_alpha_numeric_field( value, self.field_lengths[name][0] )
            elif name == 'chk_serial_num':
                value = self.validate_alpha_numeric_field( value, self.field_lengths[name][1] )

            #The rest
            else:
                value = self.validate_alpha_numeric_field( value, self.field_lengths[name] )

        elif name in self.numeric_fields:
            value = self.validate_numeric_field( value, self.field_lengths[name] )

        elif name == 'std_ent_cls_code' and value in self.std_ent_cls_code_list:
            pass
 
        else:
            raise TypeError("Field not in numeric_fields or alpha_numeric_fields")

        super(AchEntryDetail, self).__setattr__(name, value)



class AchAddendaRecord(Ach):

    record_type_code = '7'
    addenda_type_code = '05'

    def __init__(self, trans_desc, net_id_code, term_id_code,
                    trans_serial_code, trans_date, trans_time,
                    terminal_loc, terminal_city, terminal_state,
                    trace_num):
        """
        Initializes and validates values in entry addenda rows 
        """

        return        
