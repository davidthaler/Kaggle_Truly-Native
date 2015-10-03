import pandas as pd

# This module imports pandas

def rf_importance_df(rf, data, drops=['file', 'sponsored']):
  '''
  Generates a Pandas data frame of importance for the input variables.
  
  args:
    rf - a fitted sklearn RandomForestClassifer with oob_score=True
    data - a Pandas data frame with the data the RF was trained on
    drops - list of column names that were dropped to make x
    
  return:
    data frame with columns: field name, sum of counts, feature importance
  '''
  names = list(data.drop(drops, 1).columns)
  totals = data.drop(drops, 1).sum(axis=0).values
  f_imp = rf.feature_importances_
  out = pd.DataFrame({'name':names, 
                      'total':totals, 
                      'feature_importance': f_imp})
  return out[['name', 'total', 'feature_importance']]


