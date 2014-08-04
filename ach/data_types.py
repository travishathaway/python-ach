import math
import re
import string
from datetime import datetime

"""
Collection of classes that comprise the row type objects
in a nacha file
"""


class AchError(Exception):
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

    def make_right_justified(self, field, length):
        """
        Return string with x number of leading spaces depending on field length
        Routing numbers should be 9 digits long, so we technically only need 1
        leading space.
        """

        if len(field) != length:
            return field.rjust(length)
        else:
            return field

    def make_zero(self, zeros=1):
        """
        Return string with x number of zeros
        Defaults to 1
        """
        zero_string = ''

        for i in range(zeros):
            zero_string += '0'

        return zero_string

    def validate_alpha_numeric_field(self, field, length):
        """
        Validates alpha numeric fields for nacha files
        field: (str)
        length: (int)
        """
        str_length = str(length)

        match = re.match(r'([\w,\s]{1,' + str_length + '})', field)

        if match:
            if len(match.group(1)) < length:
                field = match.group(1) + self.make_space(
                    length - len(match.group(1)))
            else:
                field = match.group(1)
        else:
            raise AchError("field does not match alpha numeric criteria")

        return field.upper()

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
                field = self.make_zero(length - len(field)) + field
            elif len(field) > length:
                raise AchError("field can only be %s digits long" % length)
        else:
            raise AchError("field needs to be numeric characters only")

        return field

    def validate_binary_field(self, field):
        """
        Validates binary string field (either '1' or '0')
        """

        if field not in ['1', '0']:
            raise AchError("filed not '1' or '0'")
        return field


class Header(Ach):
    """
    Creates our File Header record of the nacha file
    """

    record_type_code = '1'
    priority_code = '01'
    record_size = '094'
    blk_factor = '10'
    format_code = '1'

    alpha_numeric_fields = [
        'immediate_dest', 'immediate_org', 'file_id_mod', 'im_dest_name',
        'im_orgn_name', 'reference_code', 'file_crt_date', 'file_crt_time'
    ]

    field_lengths = {
        'immediate_dest': 10,
        'immediate_org': 10,
        'file_id_mod': 1,
        'im_dest_name': 23,
        'im_orgn_name': 23,
        'reference_code': 8,
        'file_crt_date': 6,
        'file_crt_time': 4,
    }

    def __init__(self, immediate_dest='', immediate_org='', file_id_mod='A',
                 im_dest_name='', im_orgn_name='', reference_code=''):
        """
        Initializes all values needed for
        our header row
        """

        date = datetime.today()

        self.immediate_dest = self.make_right_justified(immediate_dest, 10)
        self.immediate_org = self.make_right_justified(immediate_org, 10)
        self.file_crt_date = date.strftime('%y%m%d')
        self.file_crt_time = date.strftime('%H%M')
        self.file_id_mod = self.validate_file_id_mod(file_id_mod)
        self.im_dest_name = self.validate_alpha_numeric_field(im_dest_name, 23)
        self.im_orgn_name = self.validate_alpha_numeric_field(im_orgn_name, 23)

        if reference_code != '':
            self.reference_code = self.validate_alpha_numeric_field(
                reference_code, 8)
        else:
            self.reference_code = self.make_space(8)

    def __setattr__(self, name, value):
        if name in self.alpha_numeric_fields:
            value = self.validate_alpha_numeric_field(
                value, self.field_lengths[name]
            )
        elif name == 'file_id_mod':
            value = self.validate_file_id_mod(value)
        else:
            raise AchError(
                '%s not in alpha numeric field list' % name
            )

        super(Header, self).__setattr__(name, value)

    def validate_file_id_mod(self, file_id_mod):
        '''
        Validates the file ID modifier. It has to be ascii_uppercase
        and one character in length
        '''
        if file_id_mod not in string.ascii_uppercase and len(file_id_mod) != 1:
            raise AchError("Invalid file_id_mod")

        return file_id_mod

    def get_row(self):
        """
        returns concatenated string of all parameters in
        nacha file
        """
        return self.record_type_code +\
            self.priority_code +\
            self.immediate_dest +\
            self.immediate_org +\
            self.file_crt_date +\
            self.file_crt_time +\
            self.file_id_mod +\
            self.record_size +\
            self.blk_factor +\
            self.format_code +\
            self.im_dest_name +\
            self.im_orgn_name +\
            self.reference_code

    def get_count(self):
        """
        Returns length of all parameters in nach
        file
        """
        return len(self.get_row())


class FileControl(Ach):
    """
    Comprises the control record for an ACH file
    Appears at the end of file
    """

    record_type_code = '9'

    numeric_fields = [
        'batch_count', 'block_count', 'entadd_count', 'entry_hash',
        'debit_amount', 'credit_amount'
    ]

    alpha_numeric_fields = ['reserved', ]

    field_lengths = {
        'batch_count': 6,
        'block_count': 6,
        'entadd_count': 8,
        'entry_hash': 10,
        'debit_amount': 12,
        'credit_amount': 12,
        'reserved': 39,
    }

    def __init__(self, batch_count, block_count,
                 entadd_count, entry_hash, debit_amount,
                 credit_amount):
        """
        Initializes all the values we need for our file control record
        """

        self.batch_count = self.validate_numeric_field(batch_count, 6)
        self.block_count = self.validate_numeric_field(block_count, 6)
        self.entadd_count = self.validate_numeric_field(entadd_count, 8)
        self.entry_hash = self.validate_numeric_field(entry_hash, 10)
        self.debit_amount = self.validate_numeric_field(debit_amount, 12)
        self.credit_amount = self.validate_numeric_field(credit_amount, 12)
        self.reserved = self.make_space(39)

    def __setattr__(self, name, value):
        if name in self.numeric_fields:
            value = self.validate_numeric_field(
                value, self.field_lengths[name]
            )
        elif name in self.alpha_numeric_fields:
            value = self.validate_alpha_numeric_field(
                value, self.field_lengths[name]
            )
        else:
            raise AchError(
                '%s not in numeric field list' % name
            )

        super(FileControl, self).__setattr__(name, value)

    def get_row(self):

        return self.record_type_code +\
            self.batch_count +\
            self.block_count +\
            self.entadd_count +\
            self.entry_hash +\
            self.debit_amount +\
            self.credit_amount +\
            self.reserved

    def get_count(self):
        return len(self.get_row())


class BatchHeader(Ach):

    record_type_code = '5'

    std_ent_cls_code_list = ['ARC', 'PPD', 'CTX', 'POS', 'WEB',
                             'BOC', 'TEL', 'MTE', 'SHR', 'CCD',
                             'CIE', 'POP', 'RCK']

    serv_cls_code_list = ['200', '220', '225']

    numeric_fields = ['orig_dfi_id', 'batch_id',
                      'eff_ent_date', 'serv_cls_code']

    alpha_numeric_fields = ['company_name', 'cmpy_dis_data', 'company_id',
                            'std_ent_cls_code', 'entry_desc', 'desc_date',
                            'orig_stat_code', 'settlement_date']

    field_lengths = {
        'serv_cls_code': 3,
        'company_name': 16,
        'cmpy_dis_data': 20,
        'company_id': 10,
        'std_ent_cls_code': 3,
        'entry_desc': 10,
        'desc_date': 6,
        'eff_ent_date': 6,
        'settlement_date': 3,
        'orig_stat_code': 1,
        'orig_dfi_id': 8,
        'batch_id': 7,
    }

    def __init__(self, serv_cls_code='220', company_name='', cmpy_dis_data='',
                 company_id='', std_ent_cls_code='PPD', entry_desc='',
                 desc_date='', eff_ent_date='', orig_stat_code='',
                 orig_dfi_id='', batch_id=''):
        """
        Initializes and validates the values for our Batch Header
        rows. We use 220 and PPD as the default values for serv_cls_code
        and std_ent_cls_code.
        """

        args = locals().copy()

        self.settlement_date = self.make_space(3)

        for key in args:
            if key == 'self':
                continue

            if args[key] != '':
                self.__setattr__(key, args[key])

            elif key in self.numeric_fields:
                self.__setattr__(key, self.make_zero(self.field_lengths[key]))

            elif key in self.alpha_numeric_fields:
                self.__setattr__(key, self.make_space(self.field_lengths[key]))

    def __setattr__(self, name, value):

        if name in self.numeric_fields:
            if name == 'serv_cls_code' \
                    and str(value) not in self.serv_cls_code_list:
                raise AchError("%s not in serv_cls_code_list" % value)

            value = self.validate_numeric_field(
                value, self.field_lengths[name]
            )

        elif name in self.alpha_numeric_fields:
            if name == 'std_ent_cls_code' \
                    and str(value) not in self.std_ent_cls_code_list:
                raise AchError("%s not in std_ent_cls_code_list" % value)

            value = self.validate_alpha_numeric_field(
                value, self.field_lengths[name]
            )

        else:
            raise AchError(
                '%s not in numeric or alpha numeric fields list' % name
            )

        super(BatchHeader, self).__setattr__(name, value)

    def get_row(self):

        return self.record_type_code +\
            self.serv_cls_code +\
            self.company_name +\
            self.cmpy_dis_data +\
            self.company_id +\
            self.std_ent_cls_code +\
            self.entry_desc +\
            self.desc_date +\
            self.eff_ent_date +\
            self.settlement_date +\
            self.orig_stat_code +\
            self.orig_dfi_id +\
            self.batch_id

    def get_count(self):
        return len(self.get_row())


class BatchControl(Ach):

    record_type_code = '8'

    numeric_fields = ['serv_cls_code', 'entadd_count', 'entry_hash',
                      'debit_amount', 'credit_amount', 'orig_dfi_id',
                      'batch_id']

    alpha_numeric_fields = ['company_id', 'mesg_auth_code', 'reserved']

    field_lengths = {
        'serv_cls_code': 3,
        'entadd_count': 6,
        'entry_hash': 10,
        'debit_amount': 12,
        'credit_amount': 12,
        'company_id': 10,
        'mesg_auth_code': 19,
        'reserved': 6,
        'orig_dfi_id': 8,
        'batch_id': 7,
    }

    def __init__(self, serv_cls_code='220', entadd_count='', entry_hash='',
                 debit_amount='', credit_amount='', company_id='',
                 orig_dfi_id='', batch_id='', mesg_auth_code=''):
        """
        Initializes and validates the batch control record
        """
        args = locals().copy()

        self.reserved = self.make_space(6)

        for key in args:
            if key == 'self':
                continue

            if args[key] != '':
                if key == 'debit_amount' or key == 'credit_amount':
                    self.__setattr__(key, int(100 * args[key]))
                else:
                    self.__setattr__(key, args[key])

            elif key in self.numeric_fields:
                self.__setattr__(key, self.make_zero(self.field_lengths[key]))

            elif key in self.alpha_numeric_fields:
                self.__setattr__(key, self.make_space(self.field_lengths[key]))

    def __setattr__(self, name, value):
        if name in self.numeric_fields:
            value = self.validate_numeric_field(
                value, self.field_lengths[name]
            )
        elif name in self.alpha_numeric_fields:
            value = self.validate_alpha_numeric_field(
                value, self.field_lengths[name]
            )
        else:
            raise AchError(
                "%s not in numeric_fields or alpha_numeric_fields" % name
            )

        super(BatchControl, self).__setattr__(name, value)

    def get_row(self):

        return self.record_type_code +\
            self.serv_cls_code +\
            self.entadd_count +\
            self.entry_hash +\
            self.debit_amount +\
            self.credit_amount +\
            self.company_id +\
            self.mesg_auth_code +\
            self.reserved +\
            self.orig_dfi_id +\
            self.batch_id

    def get_count(self):
        return len(self.get_row())


class EntryDetail(Ach):
    """
    Object represents a single Entry Detail record of an ACH file
    """

    record_type_code = '6'

    std_ent_cls_code_list = ['ARC', 'PPD', 'CTX', 'POS', 'WEB',
                             'BOC', 'TEL', 'MTE', 'SHR', 'CCD',
                             'CIE', 'POP', 'RCK']

    numeric_fields = ['transaction_code', 'recv_dfi_id', 'check_digit',
                      'amount', 'num_add_recs', 'card_exp_date', 'doc_ref_num',
                      'ind_card_acct_num', 'card_tr_typ_code_shr',
                      'add_rec_ind', 'trace_num']

    alpha_numeric_fields = ['dfi_acnt_num', 'chk_serial_num', 'ind_name',
                            'disc_data', 'id_number', 'recv_cmpy_name',
                            'terminal_city', 'terminal_state', 'reserved',
                            'card_tr_typ_code_pos', 'pmt_type_code']

    field_lengths = {
        'transaction_code'      : 2,
        'recv_dfi_id'           : [8, 9],
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

    def __init__(self, std_ent_cls_code='PPD', transaction_code='', recv_dfi_id='',
                 check_digit='', amount='', num_add_recs='', card_exp_date='',
                 doc_ref_num='', ind_card_acct_num='', card_tr_typ_code_shr='',
                 card_tr_typ_code_pos='', trace_num='', dfi_acnt_num='',
                 ind_name='', disc_data='', id_number='', recv_cmpy_name='',
                 chk_serial_num='', terminal_city='', terminal_state='',
                 pmt_type_code='', add_rec_ind=''):
        """
        Initialize and validate the values in Entry Detail record
        """
        self.std_ent_cls_code = std_ent_cls_code
        self.reserved = self.make_space(2)

        fields = locals().copy()

        for key in fields:
            if key == 'self':
                continue

            if fields[key] != '':
                self.__setattr__(key, fields[key])

            elif key in ['chk_serial_num', 'ind_name']:
                if self.std_ent_cls_code in ['CIE', 'MTE', 'POP']:
                    self.__setattr__(
                        key, self.make_space(self.field_lengths[key][0])
                    )
                else:
                    self.__setattr__(
                        key, self.make_space(self.field_lengths[key][1])
                    )

            elif key in self.numeric_fields:
                if key == 'recv_dfi_id':
                    self.__setattr__(key, self.make_zero(self.field_lengths[key][0]))
                else:
                    self.__setattr__(key, self.make_zero(self.field_lengths[key]))

            elif key in self.alpha_numeric_fields:
                self.__setattr__(
                    key, self.make_space(self.field_lengths[key])
                )

    def __setattr__(self, name, value):
        """
        Overides the setattr method for the object. We do this so
        that we can validate the field as it gets assigned.
        """

        if name in self.alpha_numeric_fields:
            # Special handling for Indvidiual/Company name field
            if name == 'ind_name' and self.std_ent_cls_code in ['CIE', 'MTE']:
                value = self.validate_alpha_numeric_field(
                    value, self.field_lengths[name][0]
                )
            elif name == 'ind_name':
                value = self.validate_alpha_numeric_field(
                    value, self.field_lengths[name][1]
                )

            # Special handling for Check serial number field
            elif name == 'chk_serial_num' and \
                    self.std_ent_cls_code_list == 'POP':
                value = self.validate_alpha_numeric_field(
                    value, self.field_lengths[name][0]
                )
            elif name == 'chk_serial_num':
                value = self.validate_alpha_numeric_field(
                    value, self.field_lengths[name][1]
                )

            #The rest
            else:
                value = self.validate_alpha_numeric_field(
                    value, self.field_lengths[name]
                )

        elif name in self.numeric_fields:
            if name == 'recv_dfi_id':
                try:
                    # try 8 digits first
                    value = self.validate_numeric_field(value, self.field_lengths[name][0])
                except AchError:
                    # now try to validate it 9 instead
                    value = self.validate_numeric_field(value, self.field_lengths[name][1])
            else:
                value = self.validate_numeric_field( value, self.field_lengths[name] )

        elif name == 'std_ent_cls_code' and \
                value in self.std_ent_cls_code_list:
            pass

        else:
            raise AchError(
                "%s not in numeric_fields or alpha_numeric_fields" % name
            )

        super(EntryDetail, self).__setattr__(name, value)

    def get_row(self):

        ret_string = ''

        ret_string = self.record_type_code +\
            self.transaction_code +\
            self.recv_dfi_id

        if len(self.recv_dfi_id) < 9:
            ret_string += self.check_digit

        ret_string += self.dfi_acnt_num +\
            self.amount

        if self.std_ent_cls_code in ['ARC', 'BOC']:
            ret_string += self.chk_serial_num +\
                self.ind_name +\
                self.disc_data

        elif self.std_ent_cls_code in ['CCD', 'PPD', 'TEL']:
            ret_string += self.id_number +\
                self.ind_name +\
                self.disc_data

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

    def get_count(self):
        return len(self.get_row())

    def calc_check_digit(self):

        multipliers = [3, 7, 1, 3, 7, 1, 3, 7]

        tmp_num = 0

        for num, mult in zip(list(self.recv_dfi_id), multipliers):
            tmp_num += int(num) * mult

        nearest_10 = math.ceil(tmp_num / 10.0)

        self.check_digit = int((nearest_10 * 10) - tmp_num)


class AddendaRecord(Ach):

    record_type_code = '7'
    addenda_type_code = '05'

    alpha_numeric_fields = [
        'trans_desc', 'net_id_code', 'term_id_code',
        'trans_serial_code', 'terminal_loc', 'terminal_city',
        'terminal_state', 'ref_info_1', 'ref_info_2', 'pmt_rel_info',
        'auth_card_exp'
    ]

    numeric_fields = [
        'trans_date', 'trans_time', 'trace_num',
        'ent_det_seq_num', 'add_seq_num'
    ]

    field_lengths = {
        'trans_desc': 7,
        'net_id_code': 3,
        'term_id_code': 6,
        'trans_serial_code': 6,
        'terminal_loc': 27,
        'terminal_city': 15,
        'terminal_state': 2,
        'ref_info_1': 7,
        'ref_info_2': 3,
        'pmt_rel_info': 80,
        'trans_date': 4,
        'trans_time': 6,
        'trace_num': 15,
        'ent_det_seq_num': 7,
        'auth_card_exp': 6,
        'add_seq_num': 4,
    }

    def __init__(self, std_ent_cls_code='PPD', trans_desc='', net_id_code='',
                 term_id_code='', ref_info_1='', ref_info_2='',
                 trans_serial_code='', trans_date='', trans_time='',
                 terminal_loc='', terminal_city='', terminal_state='',
                 trace_num='', auth_card_exp='', add_seq_num='',
                 ent_det_seq_num='', pmt_rel_info=''):
        """
        Initializes and validates values in entry addenda rows
        """

        fields = locals().copy()

        self.std_ent_cls_code = std_ent_cls_code

        for key in fields:

            if key == 'self':
                continue

            if fields[key] != '':
                self.__setattr__(key, fields[key])

            elif key in self.numeric_fields:
                self.__setattr__(key, self.make_zero(self.field_lengths[key]))

            elif key in self.alpha_numeric_fields:
                self.__setattr__(key, self.make_space(self.field_lengths[key]))

    def __setattr__(self, name, value):

        if name in self.alpha_numeric_fields:
            value = self.validate_alpha_numeric_field(
                value, self.field_lengths[name]
            )
        elif name in self.numeric_fields:
            value = self.validate_numeric_field(
                value, self.field_lengths[name]
            )
        elif name == 'std_ent_cls_code':
            pass
        else:
            raise AchError(
                "%s not in numeric or alpha numeric fields" % value
            )

        super(AddendaRecord, self).__setattr__(name, value)

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

        elif self.std_ent_cls_code in ['POS', 'SHR']:
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

    def get_count(self):
        return len(self.get_row())
