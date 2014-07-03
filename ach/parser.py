import json

#from .data_types import (
#    Header, FileControl, BatchHeader,
#    BatchControl, EntryDetail, AddendaRecord
#)


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

    FILE_HEADER_RECORD = [
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
                        line, 'FILE_HEADER_RECORD'
                    )
                    break

    def __parse_file_control(self):
        for line in self.ach_lines:
            if line:
                if line[0] == self.FILE_CONTROL:
                    self.ach_data['file_control'] = line
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
                'batch_header': self.ach_lines[batch['batch_header_line']],
                'batch_control': self.ach_lines[batch['batch_control_line']],
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
                            'entry_detail': self.ach_lines[line_num],
                            'addenda': []
                        })
                    if self.ach_lines[line_num][0] == self.ADDENDA_RECORD:
                        self.ach_data['batches'][cur_batch]['entries'][
                            cur_entry
                        ]['addenda'].append(
                            self.ach_lines[line_num]
                        )

    def __parse_file_header_line(self, line):
        return {}

    def __parse_file_control_line(self, line):
        return {}

    def __parse_batch_header(self, line):
        return {}

    def __parse_batch_control(self, line):
        return {}

    def __parse_entry_detail(self, line):
        return {}

    def __parse_addenda_record(self, line):
        return {}
