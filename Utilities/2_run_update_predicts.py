import subprocess

no_of_race = input("Input Total Number of Race: ")

scripts = [
    "NeuroPredictRegressor.py",
    "NeuroPredictRegressor2.py",
    "NeuroPredictRegressor5.py"
]

for script in scripts:
    print(f"Running {script} ...")
    subprocess.run(["python3", script, no_of_race])
