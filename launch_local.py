import os
import subprocess
import sys

def run_command(description, command):
    print(f"\n==> {description}")
    try:
        subprocess.run(command, shell=True)
    except KeyboardInterrupt:
        print("\n[Stopped]")
    print("-" * 50)

def main():
    while True:
        print("\nSelect a task to run:")
        print("1. Launch Streamlit Dashboard")
        print("2. Run Active Learning Round")
        print("3. Start Real-Time Monitor (RSS/Twitter)")
        print("4. Start Background Task Scheduler")
        print("5. View Latest Log")
        print("0. Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            run_command("Launching Streamlit Dashboard...", "streamlit run dashboard/app.py")
        elif choice == "2":
            run_command("Running Active Learning Round...", "python src/active_learning_loop.py")
        elif choice == "3":
            print("Edit realtime_monitor.py to specify your RSS and Twitter keywords before use.")
            run_command("Starting Real-Time Monitor...", "python src/realtime_monitor.py")
        elif choice == "4":
            run_command("Starting Task Scheduler...", "python src/task_scheduler.py")
        elif choice == "5":
            run_command("Showing Latest Log...", "tail -n 50 logs/inference_log.jsonl")
        elif choice == "0":
            print("Exiting.")
            break
        else:
            print("Invalid input. Try again.")

if __name__ == "__main__":
    main()
