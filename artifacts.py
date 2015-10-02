import os
import cPickle
import paths

def put_artifact(obj, artifactfile):
  '''
  Pickles an object at ARTIFACTS/artifactfile
  
  args:
    obj - an intermediate result to pickle
    artifactfile - obj is pickled at ARTIFACT/artifactfile
  
  return:
    nothing, but obj is pickled at ARTIFACT/artifactfile.pkl
  '''
  artifactpath = os.path.join(paths.ARTIFACTS, artifactfile + '.pkl')
  with open(artifactpath, 'w') as f:
    cPickle.dump(obj, f)


def get_artifact(artifactfile):
  '''
  Recovers a pickled intermediate result (artifact) from ARTIFACTS/
  
  args:
    artifactfile - an object is loaded from ARTIFACTS/artifactfile 
    
  return:
    the reloaded intermediate object
  '''
  artifactpath = os.path.join(paths.ARTIFACTS, artifactfile + '.pkl')
  with open(artifactpath) as f:
    artifact = cPickle.load(f)
  return artifact