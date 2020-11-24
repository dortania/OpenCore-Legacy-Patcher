from __future__ import print_function

import json
import subprocess
import sys

models = json.load(open("models.json"))

current_model = subprocess.Popen("system_profiler SPHardwareDataType".split(), stdout=subprocess.PIPE)
current_model = [line.strip().split(": ", 1)[1] for line in current_model.stdout.read().split("\n")  if line.strip().startswith("Model Identifier")][0]
print(current_model)

if current_model not in models:
    print("Your model is not supported by this patcher!")
    sys.exit(1)
