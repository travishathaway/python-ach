python-ach
==========

ACH file generator module for python. So far, this has been tested with
“PPD” and “CCD” batches with addenda records.

Example
=======

Below is an example of how to use the module:

.. code:: python


    from ach.builder import AchFile

    settings = {
        'immediate_dest' : '123456789', # Your bank's routing number 
        'immediate_org' : '123456789', # Bank assigned routing number
        'immediate_dest_name' : 'YOUR BANK',
        'immediate_org_name' : 'YOUR COMPANY',
        'company_id' : '1234567890', #tax number
    }

    ach_file = AchFile('A',settings) #file Id mod

    entries = [
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
            'routing_number' : '12323231',
            'account_number' : '123123123',
            'amount'         : '12.13',
            'name'           : 'Rachel Welch',
        },
    ]

    ach_file.add_batch('PPD', entries, credits=True, debits=True)

    print ach_file.render_to_string()

This returns the following NACHA file:

::

    101 123456789 1234567891407141745A094101YOUR BANK              YOUR COMPANY                   
    5220YOUR COMPANY                        1234567890PPDPAYROLL         140714   1123456780000001
    62212345678011232132         0000001000               ALICE WANDERDUST        1123456780000001
    705HERE IS SOME ADDITIONAL INFORMATION                                             00000000001
    622123456780234234234        0000015000               BILLY HOLIDAY           0123456780000002
    622123232315123123123        0000001213               RACHEL WELCH            0123456780000003
    822000000400370145870000000000000000000172131234567890                         123456780000001
    9000001000001000000040037014587000000000000000000017213                                       
    9999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999
    9999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999
