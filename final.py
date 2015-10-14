import tree_model
from sklearn.externals import joblib
import paths

tree_model.run_model('final_train', 'final_test', 1000, '17a', 'rf', True)
tree_model.run_model('final_train', 'final_test', 1000, '17b', 'extra', True)
tree_model.run_model('final_train', 'final_test', 1000, '17c', 'rf', True)
tree_model.run_model('final_train', 'final_test', 1000, '17d', 'extra', True)
tree_model.run_model('final_train', 'final_test', 1000, '17e', 'rf', True)
tree_model.run_model('final_train', 'final_test', 1000, '17f', 'extra', True)