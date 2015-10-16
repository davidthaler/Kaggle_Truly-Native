## Kaggle "Truly Native?" competition code

The ["Truly Native?"](https://www.kaggle.com/c/dato-native) 
competition was hosted on Kaggle and sponsored by Dato/Graphlab
Create with data provided by StumbleUpon. 
The competition involved predicting which of 
a large set of web pages were sponsored advertising, based on their contents. 
There were about 400,000 webpages total, provided as raw HTML.
The model implemented here finished 18th out of 274, with an AUC of 0.9797.

### Requirements
To run this model, you will need:
*  The [data](https://www.kaggle.com/c/dato-native/data). Do not unzip the files.
You may have to agree to a set of competition rules before downloading.
*  Python - version 2.7.10 
*  numpy - 1.9.2
*  scipy - 0.15.1
*  Pandas - 0.16.2 
*  scikit-learn - 0.16.1
*  BeautifulSoup - 4.3.2   
*  Pypy - 2.4.0    

The model does not use any cutting edge features of those packages, 
so any recent versions should be fine.   

You will need to create the directory structure:
```
.
+-- artifacts/
+-- data/
    +-- processed/
+-- models/
+-- submissions/
+-- tmp/
```   
where . denotes the project root.

### Files
The main files are:   
 *  paths.py - Describes the file layout under the project directory. You will have to edit this file.
 *  sparse_features.py - Creates the features for the linear model. Run under Pypy.
 *  linear_models.py - Runs the linear_models. Run in Python.
 *  counts.py - Collects counts of tags, tokens, etc. that occur frequently. Run under Pypy.
 *  wide_features.py - Constructs features for the tree models. Run under Pypy.
 *  tree_models.py - . Run in Python.   

The rule here is: If it creates features, it runs under Pypy, otherwise, Python.   

### Usage

You will have to edit the path for BASE (and maybe HOME) in paths.py so 
that it points to the project root.
