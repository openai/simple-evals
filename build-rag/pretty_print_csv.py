import csv
import json
import ast

# File name
file_name = "simple_qa_test_set.csv"

# Read and process the file
with open(file_name, 'r') as file:
    reader = csv.reader(file)

    # Skip header
    header = next(reader)

    # Process each line
    for row in reader:
        metadata, problem, answer = row
        
        # Convert metadata string to dictionary safely
        metadata_dict = ast.literal_eval(metadata)

        # Pretty print metadata, problem, and answer
        print("Metadata:")
        print(json.dumps(metadata_dict, indent=4))  # Pretty-print dictionary
        print("Problem:")
        print(problem)
        print("Answer:")
        print(answer)
        print("=" * 80)

