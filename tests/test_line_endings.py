import nose.tools as nt

from ach.builder import AchFile

class TestLineEndings(object):
    def setup(self):

        self.settings = {
            'immediate_dest' : '123456780',
            'immediate_org' : '123456780',
            'immediate_dest_name' : 'YOUR BANK',
            'immediate_org_name' : 'YOUR COMPANY',
            'company_id' : '1234567890', #tax number
        }

        self.ach_file = AchFile('A', self.settings) #file Id mod

        self.entries = [
            {
                'type'           : '22', # type of
                'routing_number' : '12345678',
                'account_number' : '11232132',
                'amount'         : '10.00',
                'name'           : 'Alice Wanderdust',
                'addenda' : [
                    {
                        'payment_related_info': 'Here is some additional information',
                    },
                ],
            },
            {
                'type'           : '27',
                'routing_number' : '12345678',
                'account_number' : '234234234',
                'amount'         : '150.00',
                'name'           : 'Billy Holiday',
            },
            {
                'type'           : '22',
                'routing_number' : '123232318',
                'account_number' : '123123123',
                'amount'         : '12.13',
                'name'           : 'Rachel Welch',
            },
        ]

        self.ach_file.add_batch('PPD', self.entries, credits=True, debits=True)

    def test_normal(self):
        ach_output = self.ach_file.render_to_string()

        rows = ach_output.split('\n')
        nt.assert_equals(len(rows), 10)
        for row in rows:
            nt.assert_equals(len(row), 94)

    def test_force_crlf(self):
        ach_output = self.ach_file.render_to_string(force_crlf=True)

        rows = ach_output.split('\r\n')
        nt.assert_equals(len(rows), 10)
        for row in rows:
            nt.assert_equals(len(row), 94)
