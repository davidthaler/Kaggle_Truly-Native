import util

util.combine_dvs(['submission_linear.csv'], 
                 ['submission_rf.csv', 'submission_extra.csv'],
                  0.01, 
                  'combo')