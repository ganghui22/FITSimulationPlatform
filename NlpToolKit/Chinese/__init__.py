# package
# __init__.py
import sys
import os
root_path = os.path.abspath(__file__)
root_path = '/'.join(root_path.split('/')[:-1])
sys.path.append(root_path)
import DialoguePrediction
import model

