# package
# __init__.py

import sys
import os

root_path = os.path.abspath(__file__)
platform = sys.platform
if 'win' in sys.platform:
    root_path = "\\".join(root_path.split("\\")[:-1])

else:
    root_path = "/".join(root_path.split("/")[:-1])
print(root_path)
sys.path.append(root_path)
# import DialoguePrediction
# import model
# import InstructionPrediction

