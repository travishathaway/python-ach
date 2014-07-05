import json


class Parser(object):
    '''
    Parser for ACH files
    '''

    FILE_HEADER = '1'
    FILE_CONTROL = '9'
    BATCH_HEADER = '5'
    BATCH_CONTROL = '8'
    ENTRY_DETAIL = '6'
    ADDENDA_RECORD = '7'

    FILE_HEADER_DEF = [
        {
            'field': 'record_type_code',
            'pos': 0,
            'len': 1,
        },
        {
            'field': 'priority_code',
            'pos': 1,
            'len': 2,
        },
        {
            'field': 'immediate_dest',
            'pos': 3,
            'len': 10,
        },
        {
            'field': 'immediate_org',
            'pos': 13,
            'len': 10,
        },
        {
            'field': 'file_crt_date',
            'pos': 23,
            'len': 6,
        },
        {
            'field': 'file_crt_time',
            'pos': 29,
            'len': 4,
        },
        {
            'field': 'file_id_mod',
            'pos': 33,
            'len': 1,
        },
        {
            'field': 'record_size',
            'pos': 34,
            'len': 3,
        },
        {
            'field': 'blk_factor',
            'pos': 37,
            'len': 2,
        },
        {
            'field': 'format_code',
            'pos': 39,
            'len': 1,
        },
        {
            'field': 'im_dest_name ',
            'pos': 40,
            'len': 23,
        },
        {
            'field': 'im_orgn_name ',
            'pos': 63,
            'len': 23,
        },
        {
            'field': 'reference_code',
            'pos': 86,
            'len': 8,
        }
    ]

    FILE_CONTROL_DEF = [
        {
            'field': 'record_type_code',
            'pos': 0,
            'len': 1,
        },
        {
            'field': 'batch_count',
            'pos': 1,
            'len': 6,
        },
        {
            'field': 'block_count',
            'pos': 7,
            'len': 6,
        },
        {
            'field': 'entadd_count',
            'pos': 13,
            'len': 8,
        },
        {
            'field': 'entry_hash',
            'pos': 21,
            'len': 10,
        },
        {
            'field': 'debit_amount',
            'pos': 31,
            'len': 12,
        },
        {
            'field': 'credit_amount',
            'pos': 43,
            'len': 12,
        },
        {
            'field': 'reserved',
            'pos': 55,
            'len': 39,
        },
    ]

    BATCH_HEADER_DEF = [
        {
            'field': 'record_type_code',
            'pos': 0,
            'len': 1,
        },
        {
            'field': 'serv_cls_code',
            'pos': 1,
            'len': 3,
        },
        {
            'field': 'company_name',
            'pos': 4,
            'len': 16,
        },
        {
            'field': 'cmpy_dis_data',
            'pos': 20,
            'len': 20,
        },
        {
            'field': 'company_id',
            'pos': 40,
            'len': 10,
        },
        {
            'field': 'std_ent_cls_code',
            'pos': 50,
            'len': 3,
        },
        {
            'field': 'entry_desc',
            'pos': 53,
            'len': 10,
        },
        {
            'field': 'desc_date',
            'pos': 63,
            'len': 6,
        },
        {
            'field': 'eff_ent_date',
            'pos': 69,
            'len': 6,
        },
        {
            'field': 'settlement_date',
            'pos': 75,
            'len': 3,
        },
        {
            'field': 'orig_stat_code',
            'pos': 78,
            'len': 1,
        },
        {
            'field': 'orig_dfi_id',
            'pos': 79,
            'len': 8,
        },
        {
            'field': 'batch_id',
            'pos': 87,
            'len': 7,
        },
    ]

    BATCH_CONTROL_DEF = [
        {
            'field': 'record_type_code',
            'pos': 0,
            'len': 1,
        },
        {
            'field': 'serv_cls_code',
            'pos': 1,
            'len': 3,
        },
        {
            'field': 'entadd_count',
            'pos': 4,
            'len': 6,
        },
        {
            'field': 'entry_hash',
            'pos': 10,
            'len': 10,
        },
        {
            'field': 'debit_amount',
            'pos': 20,
            'len': 12,
        },
        {
            'field': 'credit_amount',
            'pos': 32,
            'len': 12,
        },
        {
            'field': 'company_id',
            'pos': 44,
            'len': 10,
        },
        {
            'field': 'mesg_auth_code',
            'pos': 54,
            'len': 19,
        },
        {
            'field': 'reserved',
            'pos': 73,
            'len': 6,
        },
        {
            'field': 'orig_dfi_id',
            'pos': 79,
            'len': 8,
        },
        {
            'field': 'orig_dfi_id',
            'pos': 87,
            'len': 7,
        },
    ]

    ENTRY_DETAIL_DEF = [
        {
            'field': 'record_type_code',
            'pos': 0,
            'len': 1,
        },
        {
            'field': 'transaction_code',
            'pos': 1,
            'len': 2,
        },
        {
            'field': 'recv_dfi_id',
            'pos': 3,
            'len': 8,
        },
        {
            'field': 'check_digit',
            'pos': 11,
            'len': 1,
        },
        {
            'field': 'dfi_acnt_num',
            'pos': 12,
            'len': 17,
        },
        {
            'field': 'amount',
            'pos': 29,
            'len': 10,
        },
        {
            'field': 'ind_id',
            'pos': 39,
            'len': 15,
        },
        {
            'field': 'ind_name',
            'pos': 54,
            'len': 22,
        },
        {
            'field': 'disc_data',
            'pos': 76,
            'len': 2,
        },
        {
            'field': 'add_rec_ind',
            'pos': 78,
            'len': 1,
        },
        {
            'field': 'trace_num',
            'pos': 79,
            'len': 15,
        },
    ]

    ADDENDA_RECORD_DEF = [
        {
            'field': 'record_type_code',
            'pos': 0,
            'len': 1,
        },
        {
            'field': 'addenda_type_code',
            'pos': 1,
            'len': 2,
        },
        {
            'field': 'pmt_rel_info',
            'pos': 3,
            'len': 80,
        },
        {
            'field': 'add_seq_num',
            'pos': 83,
            'len': 4,
        },
        {
            'field': 'ent_det_seq_num',
            'pos': 87,
            'len': 7,
        },
    ]

    record_type_codes = {
        '1': 'file_header',
        '9': 'file_control',
        '5': 'batch_header',
        '8': 'batch_control',
        '6': 'entry_detail',
        '7': 'addenda_record',
    }

    def __init__(self, ach_file):
        self.ach_file = ach_file
        self.ach_lines = ach_file.split('\n')
        self.ach_data = {}

        self.__parse_file()

    def as_json(self):
        return json.dumps(self.ach_data)

    def as_dict(self):
        return self.ach_data

    def __parse_file(self):
        self.__parse_file_header()
        self.__parse_file_control()

        batch_info = self.__get_batch_info()
        self.__parse_batches(batch_info)

    def __parse_line(self, line, record_type):
        defintions = getattr(self, record_type)
        record_data = {}

        for rule in defintions:
            value = line[rule['pos']:rule['pos'] + rule['len']]
            record_data[rule['field']] = value

        return record_data

    def __parse_file_header(self):
        for line in self.ach_lines:
            if line:
                if line[0] == self.FILE_HEADER:
                    self.ach_data['file_header'] = self.__parse_line(
                        line, 'FILE_HEADER_DEF'
                    )
                    break

    def __parse_file_control(self):
        for line in self.ach_lines:
            if line:
                if line[0] == self.FILE_CONTROL:
                    self.ach_data['file_control'] = self.__parse_line(
                        line, 'FILE_CONTROL_DEF'
                    )
                    break

    def __get_batch_info(self):
        batches = []

        for line_num, line in enumerate(self.ach_lines):
            if line:
                if line[0] == self.BATCH_HEADER:
                    batches.append({
                        'batch_header_line': line_num,
                    })
                if line[0] == self.BATCH_CONTROL:
                    batches[len(batches) - 1]['batch_control_line'] = line_num

        return batches

    def __parse_batches(self, batch_info):
        self.ach_data['batches'] = []

        for batch in batch_info:
            self.ach_data['batches'].append({
                'batch_header': self.__parse_line(
                    self.ach_lines[batch['batch_header_line']],
                    'BATCH_HEADER_DEF'
                ),
                'batch_control': self.__parse_line(
                    self.ach_lines[batch['batch_control_line']],
                    'BATCH_CONTROL_DEF'
                ),
                'entries': [],
            })

            start = batch['batch_header_line'] + 1
            stop = batch['batch_control_line']

            for line_num in range(start, stop):
                if self.ach_lines[line_num]:
                    cur_batch = len(self.ach_data['batches']) - 1
                    cur_entry = len(
                        self.ach_data['batches'][cur_batch]['entries']
                    ) - 1

                    if self.ach_lines[line_num][0] == self.ENTRY_DETAIL:
                        self.ach_data['batches'][cur_batch]['entries'].append({
                            'entry_detail': self.__parse_line(
                                self.ach_lines[line_num],
                                'ENTRY_DETAIL_DEF'
                            ),
                            'addenda': []
                        })
                    if self.ach_lines[line_num][0] == self.ADDENDA_RECORD:
                        self.ach_data['batches'][cur_batch]['entries'][
                            cur_entry
                        ]['addenda'].append(
                            self.__parse_line(
                                self.ach_lines[line_num], 'ADDENDA_RECORD_DEF'
                            )
                        )
