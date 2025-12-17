import praw
import prawcore

# API config
reddit = praw.Reddit(client_id='',
                     client_secret='',
                     user_agent='',
                     username="",
                     check_for_async=False)

import time
import pandas as pd
from datetime import datetime

pd.set_option('max_colwidth', None)

def get_global_post_ids(global_files):
    """
    Reads each global CSV file and returns a set of all post IDs combined.
    
    Args:
        global_files (list): List of global CSV file paths.
    
    Returns:
        set: A set of post IDs from all provided files.
    """
    global_set = set()
    for file in global_files:
        try:
            df = pd.read_csv(file)
            ids = df['post_id'].tolist()
            global_set.update(ids)
            print(f"Loaded {len(ids)} post IDs from {file}.")
        except Exception as e:
            print(f"Error reading {file}: {e}")
    return global_set

def append_posts(subreddits, query, global_post_set):
    """
    Searches through a list of subreddits for the given query,
    skipping any posts that are already present in the global_post_set.
    
    Args:
        subreddits (list): List of subreddit names to search.
        query (str): Search query to use.
        global_post_set (set): Set of post IDs (from all global files) to skip.
    
    Returns:
        List of dictionaries containing post details.
    """
    posts = []
    
    for sub in subreddits:
        print(f"Searching in r/{sub} for query '{query}'")
        subreddit_instance = reddit.subreddit(sub)
        try:
            for i, post in enumerate(subreddit_instance.search(query, limit=None, sort="comments", time_filter='year')):
                if post.id in global_post_set:
                    continue  # Skip posts already in one of the global files
                
                # Convert the UTC timestamp to a human-readable format.
                readable_date = datetime.utcfromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S')
                author_id = getattr(post.author, 'id', None)
                author_verified = getattr(post.author, 'has_verified_email', None)
                
                posts.append({
                    'post_id': post.id,
                    'subreddit': post.subreddit.display_name,
                    'author_id': author_id,
                    'author_verified': author_verified,
                    'flare': post.author_flair_text,
                    'title': post.title,
                    'score': post.score,
                    'date': readable_date,
                    'num_comments': post.num_comments,
                    'body': post.selftext,
                })
        except prawcore.exceptions.NotFound as nf:
            # This exception is raised if the subreddit is not found.
            print(f"Subreddit r/{sub} raised a NotFound exception: {nf}")
        except Exception as e:
            print(f"An error occurred while searching in r/{sub}: {type(e).__name__}: {e}")
        time.sleep(2)  # Delay to help respect API rate limits
    
    return posts

def save_to_csv(df, filename):
    """
    Saves the provided DataFrame to a CSV file.
    
    Args:
        df (pandas.DataFrame): DataFrame containing post data.
        filename (str): Name of the CSV file to save.
    """
    try:
        print(f"Saving Reddit data to '{filename}'...")
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Data successfully saved to '{filename}'.")
    except Exception as e:
        print(f"An error occurred while saving to CSV: {e}")

# Global CSV files for each fire type
queries = {
    "Palisades Fire": "palisades_global_posts.csv",
    "Eaton Fire": "eaton_global_posts.csv",
    "Hughes Fire": "hughes_global_posts.csv"
}

# Combine post IDs from all three global files.
global_files = list(queries.values())
global_post_set = get_global_post_ids(global_files)
print(f"Total unique global post IDs loaded: {len(global_post_set)}.")

# Local configurations for each fire type.
local_configurations = [
    {
        "fire_type": "Palisades Fire",
        "subreddits": ["PacificPalisades"],
        "query": "fire wildfire",
        "local_csv": "palisades_local_posts.csv"
    },
    {
        "fire_type": "Eaton Fire",
        "subreddits": ["Pasadena", "Altadena"],
        "query": "fire wildfire",
        "local_csv": "eaton_local_posts.csv"
    },
    {
        "fire_type": "Hughes Fire",
        "subreddits": ["SantaClarita"],
        "query": "fire wildfire",
        "local_csv": "hughes_local_posts.csv"
    },
    {
        "fire_type": "CA Fire",
        "subreddits": ["California", "LosAngeles"],
        "query": "fire wildfire",
        "local_csv": "all_local_posts.csv"
    }
]

# Make sure you have authenticated your Reddit instance (using PRAW) before running this code.
# For example:
# import praw
# reddit = praw.Reddit(client_id='YOUR_ID', client_secret='YOUR_SECRET', user_agent='YOUR_AGENT')

# Loop through each local configuration to fetch and save local posts.
for config in local_configurations:
    print(f"\nProcessing local search for {config['fire_type']}")
    posts = append_posts(config['subreddits'], config['query'], global_post_set)
    post_df = pd.DataFrame(posts)
    save_to_csv(post_df, config['local_csv'])