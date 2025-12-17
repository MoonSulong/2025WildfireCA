import csv

# List of CSV files to read
files = ['palisades_posts.csv', 'eaton_posts.csv', 'hughes_posts.csv']

# Set to store unique post IDs
unique_ids = set()

# Read each file and add the post IDs (assumed to be in the first column) to the set
for file_path in files:
    try:
        with open(file_path, mode='r', newline='') as infile:
            reader = csv.reader(infile)
            header = next(reader, None)  # Skip header row if present
            for row in reader:
                if row:  # Ensure the row is not empty
                    unique_ids.add(row[0])
        print(f"Processed {file_path}.")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

# Write the unique post IDs to a merged CSV file
output_file = "merged_global_posts.csv"
with open(output_file, mode='w', newline='') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(["post_id"])  # Write header
    for post_id in unique_ids:
        writer.writerow([post_id])

print(f"Merged unique post IDs written to {output_file}.")