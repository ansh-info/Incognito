import os
import subprocess

# List of files to include (you can add filenames or patterns here)
INCLUDE_FILES = ["questionbank/create_questions.py", "questionbank/create_users.py", "questionbank/insert_questions.py",
                 "questionbank/master_candidate.py", "questionbank/suitable_candidates.py", "emailclient/logs/create_email_interview_logging_db.py",
                 "emailclient/logs/create_email_selected_logging_db.py", "api_fetch/operations.py"]

def run_all_scripts(root_dir):
    # Traverse all directories and subdirectories
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            # Only consider Python files and include only the ones in the INCLUDE_FILES list
            script_path = os.path.join(dirpath, filename)
            if filename.endswith(".py") and os.path.relpath(script_path, root_dir) in INCLUDE_FILES:
                print(f"Running {script_path}...")
                
                # Run the script
                result = subprocess.run(['python', script_path], capture_output=True, text=True)
                
                # Output the result of the script
                print(f"Output of {script_path}:\n{result.stdout}")
                if result.stderr:
                    print(f"Errors:\n{result.stderr}")

if __name__ == "__main__":
    # Call the function and provide the root directory where your scripts are located
    run_all_scripts(os.path.dirname(os.path.abspath(__file__)))
