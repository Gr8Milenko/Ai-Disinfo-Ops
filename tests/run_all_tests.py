import subprocess

def run_tests():
    print("[1/2] Generating synthetic test data...")
    subprocess.run(["python", "tests/generate_test_data.py"], check=True)

    print("[2/2] Running test pipeline...")
    subprocess.run(["python", "tests/test_runs.py"], check=True)

    print("[DONE] All tests passed.")

if __name__ == "__main__":
    run_tests()
