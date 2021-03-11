from pathlib import Path
import subprocess

for i in [i for i in list(Path().resolve().glob("**/*.md")) if "node_modules" not in str(i.parent) and "_book" not in str(i.parent)]:
    #bert = subprocess.run(['npx', 'markdown-link-check', '"' + str(i) + '"', '-c', '.markdownlinkcheck.json'], capture_output=True, shell=True, cwd=Path().resolve())    
    bert = subprocess.run('npx markdown-link-check "' + str(i) + '"', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, cwd=Path().resolve())
    outpot = bert.stdout.decode().replace("\r", "").split("\n")
    outpot = [i for i in outpot if ("FILE: " in i or " → Status: " in i) and " → Status: 429" not in i]
    [print(i) for i in outpot]