import util

util.combine_dvs(['submission_linear.csv'], 
                 ['submission_rf.csv', 'submission_extra'],
                  0.01, 
                  'combo')