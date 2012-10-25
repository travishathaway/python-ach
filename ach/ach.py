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
                        'ind_card_acct_num', 'card_tr_typ_code_shr', 'add_rec_ind',
                        'trace_num']

    alpha_numeric_fields = [ 'dfi_acnt_num', 'chk_serial_num', 'ind_name',
                                'disc_data', 'id_number', 'recv_cmpy_name',
                                'terminal_city', 'terminal_state', 'reserved',
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
        'add_rec_ind'           : 1,
        'trace_num'             : 15,
    }

    def __init__(self, std_ent_cls_code, transaction_code='',recv_dfi_id='', check_digit='',
                    amount='', num_add_recs='', card_exp_date='' ,doc_ref_num='',
                    ind_card_acct_num='', card_tr_typ_code_shr='', card_tr_typ_code_pos='',
                    trace_num='', dfi_acnt_num='', ind_name='', disc_data='', id_number='', 
                    recv_cmpy_name='', chk_serial_num='', terminal_city='', terminal_state='', 
                    pmt_type_code='', add_rec_ind=''):
        """
        Initialize and validate the values in Entry Detail record
        """
        self.std_ent_cls_code = std_ent_cls_code
        self.reserved = self.make_space(2)

        fields = locals().copy()

        for key in fields:
            if key == 'self': continue

            if fields[key] != '':
                self.__setattr__(key, fields[key])

            elif key in ['chk_serial_num', 'ind_name']:
                if self.std_ent_cls_code in ['CIE', 'MTE', 'POP']:
                    self.__setattr__(key, self.make_space( self.field_lengths[key][0] ) )
                else:
                    self.__setattr__(key, self.make_space( self.field_lengths[key][1] ) )

            elif key in self.numeric_fields:
                self.__setattr__(key, self.make_zero( self.field_lengths[key] ) )

            elif key in self.alpha_numeric_fields:
                self.__setattr__(key, self.make_space( self.field_lengths[key] ) )

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
            raise TypeError(name+" not in numeric_fields or alpha_numeric_fields")

        super(AchEntryDetail, self).__setattr__(name, value)

    def get_row(self):

        ret_string = '';

        ret_string = self.record_type_code +\
                        self.transaction_code +\
                        self.recv_dfi_id +\
                        self.check_digit +\
                        self.dfi_acnt_num +\
                        self.amount

        if self.std_ent_cls_code in ['ARC','BOC']:
            ret_string += self.chk_serial_num +\
                self.ind_name +\
                self.disc_data

        elif self.std_ent_cls_code in ['CCD','PPD','TEL']:
            ret_string += self.id_number +\
                self.ind_name +\
                disc_data

        elif self.std_ent_cls_code == 'CIE':
            ret_string += self.ind_name +\
                self.ind_id +\
                self.disc_data

        elif self.std_ent_cls_code == 'CTX':
            ret_string += self.id_number +\
                self.num_add_recs +\
                self.recv_cmpy_name +\
                self.reserved +\
                self.disc_data

        elif self.std_ent_cls_code == 'MTE':
            ret_string += self.ind_name +\
                self.ind_id +\
                self.disc_data

        elif self.std_ent_cls_code == 'POP':
            ret_string += self.chk_serial_num +\
                self.terminal_city +\
                self.terminal_state +\
                self.ind_name +\
                self.disc_data

        elif self.std_ent_cls_code == 'POS':
            ret_string += self.id_number +\
                self.ind_name +\
                self.card_tr_typ_code_pos

        elif self.std_ent_cls_code == 'SHR':
            ret_string += self.card_exp_date +\
                self.doc_ref_num +\
                self.ind_card_acct_num +\
                self.card_tr_typ_code_shr

        elif self.std_ent_cls_code == 'RCK':
            ret_string += self.chk_serial_num +\
                self.ind_name +\
                self.disc_data

        elif self.std_ent_cls_code == 'WEB':
            ret_string += self.id_number +\
                self.ind_name +\
                self.pmt_type_code

        ret_string += self.add_rec_ind +\
            self.trace_num
 
        return ret_string       



class AchAddendaRecord(Ach):

    record_type_code = '7'
    addenda_type_code = '05'

    alpha_numeric_fields = ['trans_desc', 'net_id_code', 'term_id_code',
                            'trans_serial_code', 'terminal_loc', 'terminal_city', 
                            'terminal_state', 'ref_info_1', 'ref_info_2', 'pmt_rel_info',
                            'auth_card_exp']

    numeric_fields  = ['trans_date', 'trans_time', 'trace_num', 'ent_det_seq_num',
                        'add_seq_num']

    field_lengths = {
        'trans_desc'        : 7,
        'net_id_code'       : 3,
        'term_id_code'      : 6,
        'trans_serial_code' : 6,
        'terminal_loc'      : 27,
        'terminal_city'     : 15,
        'terminal_state'    : 2,
        'ref_info_1'        : 7,
        'ref_info_2'        : 3,
        'pmt_rel_info'      : 80,
        'trans_date'        : 4,
        'trans_time'        : 6,
        'trace_num'         : 15,
        'ent_det_seq_num'   : 7,
        'auth_card_exp'     : 6,
        'add_seq_num'       : 4,
    }
        

    def __init__(self, std_ent_cls_code, trans_desc='', net_id_code='', term_id_code='',
                    ref_info_1='', ref_info_2='', trans_serial_code='', 
                    trans_date='', trans_time='', terminal_loc='', 
                    terminal_city='', terminal_state='', trace_num='',
                    auth_card_exp='',add_seq_num='', ent_det_seq_num='',
                    pmt_rel_info=''):
        """
        Initializes and validates values in entry addenda rows 
        """

        fields = locals().copy()

        self.std_ent_cls_code = std_ent_cls_code

        for key in fields:

            if key == 'self': continue

            if fields[key] != '':
                self.__setattr__(key, fields[key] )

            elif key in self.numeric_fields:
                self.__setattr__(key, self.make_zero( self.field_lengths[key] ) )

            elif key in self.alpha_numeric_fields:
                self.__setattr__(key, self.make_space( self.field_lengths[key] ) )

    def __setattr__(self, name, value):

        if name in self.alpha_numeric_fields:
            value = self.validate_alpha_numeric_field(value, self.field_lengths[name])
        elif name in self.numeric_fields:
            value = self.validate_numeric_field(value, self.field_lengths[name])
        elif name == 'std_ent_cls_code':
            pass
        else:
            raise TypeError(value+" not in numeric or alpha numeric fields")

        super(AchAddendaRecord, self).__setattr__(name, value)

    def get_row(self):

        ret_string = ''

        ret_string += self.record_type_code +\
            self.addenda_type_code

        if self.std_ent_cls_code == 'MTE':
            ret_string += self.trans_desc +\
                self.net_id_code +\
                self.term_id_code +\
                self.trans_serial_code +\
                self.trans_date +\
                self.trans_time +\
                self.terminal_loc +\
                self.terminal_city +\
                self.terminal_state +\
                self.trace_num

        elif self.std_ent_cls_code in ['POS','SHR']:
            ret_string += self.ref_info_1 +\
                self.ref_info_2 +\
                self.term_id_code +\
                self.trans_serial_code +\
                self.trans_date +\
                self.auth_card_exp +\
                self.terminal_loc +\
                self.terminal_city +\
                self.terminal_state +\
                self.trace_num

        else:
            ret_string += self.pmt_rel_info +\
                self.add_seq_num +\
                self.ent_det_seq_num

        return ret_string

