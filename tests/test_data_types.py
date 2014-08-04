import nose.tools as nt
from ach import data_types as dt


class TestDataTypes(object):

    def setup(self):
        '''
        We need to set up some data types
        '''

        self.header = dt.Header(
            '123456789', '123456789', 'A', 'YOUR BANK', 'YOUR COMPANY'
        )
        self.file_control = dt.FileControl(1, 1, 0, 213123123, 12300, 12300)
        self.batch_header = dt.BatchHeader()
        self.batch_control = dt.BatchControl()
        self.entry_detail = dt.EntryDetail()
        self.addenda_record = dt.AddendaRecord()

    def test_line_width(self):
        '''
        Test each record to make sure they are 94 characters wide
        '''
        nt.assert_equals(len(self.header.get_row()), 94)
        nt.assert_equals(len(self.file_control.get_row()), 94)
        nt.assert_equals(len(self.batch_header.get_row()), 94)
        nt.assert_equals(len(self.batch_control.get_row()), 94)
        nt.assert_equals(len(self.entry_detail.get_row()), 94)
        nt.assert_equals(len(self.addenda_record.get_row()), 94)

    def test_invalid_property_header(self):
        '''
        We make sure that properties that are not define in "numeric_fields"
        or "alpha_numeric_fields" cannot be defined as object properties.
        '''
        nt.assert_raises(dt.AchError, setattr, self.header,
                         'test_property', 'testtesttest')
        nt.assert_raises(dt.AchError, setattr, self.file_control,
                         'test_property', 'testtesttest')
        nt.assert_raises(dt.AchError, setattr, self.batch_header,
                         'test_property', 'testtesttest')
        nt.assert_raises(dt.AchError, setattr, self.batch_control,
                         'test_property', 'testtesttest')
        nt.assert_raises(dt.AchError, setattr, self.entry_detail,
                         'test_property', 'testtesttest')
        nt.assert_raises(dt.AchError, setattr, self.addenda_record,
                         'test_property', 'testtesttest')

    def test_check_digit(self):
        '''
        Ensure our check digit is being calculate appropriately on
        entry detail records
        '''
        self.entry_detail.recv_dfi_id = '11100002'
        self.entry_detail.calc_check_digit()

        nt.assert_equal(
            self.entry_detail.recv_dfi_id + self.entry_detail.check_digit,
            '111000025'
        )
