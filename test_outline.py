
from __future__ import print_function


'''
cut until after [Data] header
parse as CSV using pandas
'''

class TestSampleSheet(unittest.TestCase):

    def setUp(self):
        self.sheet = open('SampleSheet.csv')

def test_get_csv_from_samplesheet(self):
    expected = '''Sample_ID,Sample_Name,Sample_Plate,Sample_Well,I7_Index_ID,index,I5_Index_ID,index2,GenomeFolder,Sample_Project,Description'''
    actual = module.get_csv_substring(self.sheet)

def test_ss_to_data_frame(self):
    df = module.sample_sheet_to_df(self.sheet)
    actual = (df[0])
    expected = [ "011515DV1-WesPac74", "011515DV1-WesPac74", "20150317_Den_YFV_JEV_WNV",
     "A01", "N701", "TAAGGCGA", "S502", "CTCTCTAT", "PhiX\Illumina\RTA\Sequence\WholeGenomeFasta",
     float("nan"), float("nan") ]

#TODO: apply a scehma to the CSV file
# throw exception if rows are wrong
def test_sync_samples(self):
    pass
