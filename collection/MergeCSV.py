import pandas as pd

def merge_csv_files(file_paths, output_path):
    """
    Merges multiple CSV files with the same columns into a single CSV file.

    Parameters:
        file_paths (list of str): List of file paths to the CSV files to merge.
        output_path (str): The file path where the merged CSV will be saved.

    Returns:
        None
    """
    try:
        # Read and concatenate all CSV files
        dataframes = [pd.read_csv(file) for file in file_paths]
        merged_df = pd.concat(dataframes, ignore_index=True)
        
        merged_df.drop_duplicates(subset=['post_id'], inplace=True)
        
        # Save the merged data to the output file
        merged_df.to_csv(output_path, index=False)
        print(f"Files merged successfully into {output_path}!")
    except Exception as e:
        print(f"An error occurred: {e}")

# # Example usage
# file_paths = [
#     ['eaton_global_posts.csv', 'eaton_local_posts.csv'],
#     ['palisades_global_posts.csv', 'palisades_local_posts.csv'],
#     ['hughes_global_posts.csv', 'hughes_local_posts.csv']
# ]
# output_path = ['eaton_raw_posts.csv', 'palisades_raw_posts.csv', 'hughes_raw_posts.csv']

# for in_file, out_file in zip(file_paths, output_path):
#     merge_csv_files(in_file, out_file)
    
# Example usage
# file_paths = ['eaton_global_posts.csv', 'palisades_global_posts.csv', 'hughes_global_posts.csv']
# output_path = 'ca_global_posts.csv'

# merge_csv_files(file_paths, output_path)

file_paths = ['ca_final_posts.csv', 'palisades_final_posts.csv', 'eaton_final_posts.csv', 'hughes_final_posts.csv']
output_path = 'all_final_posts.csv'

merge_csv_files(file_paths, output_path)