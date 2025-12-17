import praw

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

# Subreddit to search
subreddit = reddit.subreddit('all')

# Assumes you have already authenticated your Reddit instance using PRAW
# e.g., reddit = praw.Reddit(client_id='YOUR_ID', client_secret='YOUR_SECRET', user_agent='YOUR_AGENT')
subreddit = reddit.subreddit('all')

def fetch_posts(subreddit, query):
    posts = []
    try:
        for i, post in enumerate(subreddit.search(query, sort='comments', limit=None, time_filter='year')):
            # Convert UTC timestamp to human-readable format
            readable_date = datetime.utcfromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S')

            # Safely extract author details (handle cases where author is deleted)
            author_id = getattr(post.author, 'id', None)
            author_verified = getattr(post.author, 'has_verified_email', None)

            # Append post data to our list
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
    except Exception as e:
        print(f"An error occurred while fetching posts for '{query}': {e}")
    return posts

def save_to_csv(df, filename):
    try:
        print(f"Saving Reddit data to {filename}...")
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Data successfully saved to {filename}.")
    except Exception as e:
        print(f"An error occurred while saving to CSV: {e}")

# Define our queries and corresponding output filenames
queries = {
    "Palisades Fire": "palisades_global_posts.csv",
    "Eaton Fire": "eaton_global_posts.csv",
    "Hughes Fire": "hughes_global_posts.csv"
}

# Loop through each query, fetch posts, and save to a CSV file
for query, filename in queries.items():
    print(f"Fetching posts for query: {query}")
    posts = fetch_posts(subreddit, query)
    post_df = pd.DataFrame(posts)
    save_to_csv(post_df, filename)