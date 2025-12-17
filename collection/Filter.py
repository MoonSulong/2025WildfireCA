import pandas as pd

def contains_keywords(text, required_keywords):
    """
    Check if the text contains at least one required keyword and one optional keyword.
    
    Args:
        text (str): The text to search.
        required_keywords (list or str): One or more required keywords.
    
    Returns:
        bool: True if the text contains at least one required and one optional keyword.
    """
    # Ensure required_keywords is a list
    if isinstance(required_keywords, str):
        required_keywords = [required_keywords]
    
    text_lower = str(text).lower()
    has_required = any(keyword.lower() in text_lower for keyword in required_keywords)
    return has_required

def filter_by_keywords(df, required_keywords, text_columns=['title', 'body']):
    """
    Returns a boolean mask for rows that contain the required and optional keywords
    in at least one of the specified text columns.
    
    Args:
        df (pd.DataFrame): Input DataFrame.
        required_keywords (str or list): Required keyword(s).
        text_columns (list): List of columns to search for keywords.
    
    Returns:
        pd.Series: Boolean mask where True indicates the row meets the keyword condition.
    """
    mask = pd.Series(False, index=df.index)
    for col in text_columns:
        mask |= df[col].apply(lambda x: contains_keywords(x, required_keywords))
    return mask

def filter_by_date(df, date_column, date_cutoff):
    """
    Returns a boolean mask for rows where the date in date_column is greater than date_cutoff.
    
    Args:
        df (pd.DataFrame): Input DataFrame.
        date_column (str): Column name for the date.
        date_cutoff (str): Cutoff date (ISO format: 'YYYY-MM-DD').
    
    Returns:
        pd.Series: Boolean mask based on the date condition.
    """
    # Assuming the date column is in ISO string format or already comparable.
    return df[date_column] > date_cutoff

def filter_and_output(global_file, local_file, required_keywords,
                      date_column, date_cutoff, text_columns, output_file):
    """
    Reads from the global posts CSV, filters it by keywords, appends data from the local posts CSV,
    filters the combined DataFrame by date, and writes the final data to output_file.
    
    Args:
        global_file (str): Path to the global posts CSV.
        local_file (str): Path to the local posts CSV.
        required_keywords (list or str): Required keyword(s) for filtering global posts.
        date_column (str): Name of the date column.
        date_cutoff (str): Date cutoff (ISO format: 'YYYY-MM-DD').
        text_columns (list): List of columns to search for keywords.
        output_file (str): Output CSV file path.
    """
    # Read the global posts CSV and filter by keywords.
    df_global = pd.read_csv(global_file)
    mask_keywords = filter_by_keywords(df_global, required_keywords, text_columns)
    df_global_filtered = df_global[mask_keywords]
    print(f"{global_file}: {len(df_global)} rows, filtered to {len(df_global_filtered)} rows by keywords.")
    
    # Read the local posts CSV.
    df_local = pd.read_csv(local_file)
    print(f"{local_file}: {len(df_local)} rows.")
    
    # Append (concatenate) the filtered global posts with the local posts.
    df_combined = pd.concat([df_global_filtered, df_local], ignore_index=True)
    print(f"Combined rows: {len(df_combined)}.")
    
    # Filter the combined DataFrame by the date cutoff.
    mask_date = filter_by_date(df_combined, date_column, date_cutoff)
    df_final = df_combined[mask_date].sort_values(by=date_column)
    print(f"Final rows after date filter: {len(df_final)}.")
    
    # Write the final DataFrame to the output CSV.
    df_final.to_csv(output_file, index=False)
    print(f"Final data saved to {output_file}.")

# --------------------------
# Set common parameters
# --------------------------
date_column = 'date'
date_cutoff = '2024-12-31'  # Adjust as needed
text_columns = ['title', 'body']

# # --------------------------
# # For Eaton Fire
# # --------------------------
# eaton_required = ['eaton fire', 'eaton wildfire']
# filter_and_output(
#     global_file='eaton_global_posts.csv',
#     local_file='eaton_local_posts.csv',
#     required_keywords=eaton_required,
#     date_column=date_column,
#     date_cutoff=date_cutoff,
#     text_columns=text_columns,
#     output_file='eaton_final_posts.csv'
# )

# # --------------------------
# # For Palisades Fire
# # --------------------------
# palisades_required = ['palisades fire', 'palisades wildfire']
# filter_and_output(
#     global_file='palisades_global_posts.csv',
#     local_file='palisades_local_posts.csv',
#     required_keywords=palisades_required,
#     date_column=date_column,
#     date_cutoff=date_cutoff,
#     text_columns=text_columns,
#     output_file='palisades_final_posts.csv'
# )

# # --------------------------
# # For Hughes Fire
# # --------------------------
# hughes_required = ['hughes fire', 'hughes wildfire']
# filter_and_output(
#     global_file='hughes_global_posts.csv',
#     local_file='hughes_local_posts.csv',
#     required_keywords=hughes_required,
#     date_column=date_column,
#     date_cutoff=date_cutoff,
#     text_columns=text_columns,
#     output_file='hughes_final_posts.csv'
# )

# --------------------------
# For ALL Fire
# --------------------------
all_required = ['palisades fire', 'palisades wildfire', 
                'eaton fire', 'eaton wildfire', 
                'hughes fire', 'hughes wildfire', 
                'la county fire', 'la fire', 'la wildfire',
                'california fire', 'california wildfire', 'calfire']
filter_and_output(
    global_file='ca_global_posts.csv',
    local_file='ca_local_posts.csv',
    required_keywords=all_required,
    date_column=date_column,
    date_cutoff=date_cutoff,
    text_columns=text_columns,
    output_file='ca_final_posts.csv'
)

