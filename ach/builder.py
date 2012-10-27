class AchFile(object):

    """
    Holds:

    Header (1)
    Batch  (n) <-- multiple
    Footer (1)
    """

    def __init__(self, header, batches, control ):
        """
        args: header (Header), batches (List[FileBatch]), control (FileControl)
        """

        self.header  = header
        self.batches = batches
        self.control = control

    def render_file(self):
        """
        Renders a nacha file as a string
        """
        return

class FileBatch(object):

    """
    Holds:

    BatchHeader  (1)
    Entry        (n) <-- multiple
    BatchControl (1)
    """

    def __init__(self, batch_header, entries, batch_control):
        """
        args: batch_header (BatchHeader), entries (List[FileEntry]), batch_control (BatchControl)
        """

        self.batch_header   = batch_header
        self.entries        = entries
        self.batch_control  = batch_control

class FileEntry(object):

    """
    Holds:

    EntryDetail (1)
    AddendaRecord (n) <-- for some types of entries there can be more than one
    """

    def __init__(self, entry_detail, addenda_record):
        """
        args: entry_detail( EntryDetail), addenda_record (AddendaRecord)
        """

        self.entry_detail   = entry_detail
        self.addenda_record = addenda_record

