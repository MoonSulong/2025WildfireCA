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


def fetch_comments(post_id: str, reddit, retries: int = 3, retry_delay: int = 5):
    """
    Fetch all comments for a specific post with retry logic and convert created_utc to a human-readable date.
    If all retry attempts fail, the exception is raised.

    Args:
        post_id (str): The ID of the Reddit post.
        reddit: An instance of the PRAW Reddit API client.
        retries (int): Number of retry attempts.
        retry_delay (int): Seconds to wait between retries.

    Returns:
        List[Dict[str, Any]]: List of dictionaries with comment details.

    Raises:
        Exception: The exception encountered on the final retry attempt.
    """
    for attempt in range(retries):
        try:
            submission = reddit.submission(id=post_id)
            print(f"[{post_id}] Replacing MoreComments placeholders...")
            submission.comments.replace_more(limit=None)
            print(f"[{post_id}] Flattening the comment tree...")
            all_comments = submission.comments.list()

            comments_data = [
                {
                    'post_id': post_id,
                    'comment_id': comment.id,
                    'author': comment.author.name if comment.author else "[deleted]",
                    'body': comment.body,
                    'score': comment.score,
                    'created_utc': datetime.utcfromtimestamp(comment.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                }
                for comment in all_comments
            ]
            return comments_data

        except Exception as e:
            print(f"Attempt {attempt + 1} failed for post ID {post_id}: {e}")
            if attempt < retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"All retry attempts failed for post ID {post_id}. Raising exception.")
                raise  # Propagate the exception instead of returning an empty list

def fetch_all_comments(post_ids, reddit, rate_limit_sleep: int = 10, retries: int = 3, retry_delay: int = 5):
    """
    Fetch comments for a list of posts with rate limit handling and retry logic.
    
    If any post fails (i.e. fetch_comments raises an exception), the failure is logged and the post ID is recorded.
    After processing all posts, if there were any failures, an exception is raised with the list of failed IDs.
    
    Args:
        post_ids (List[str]): List of Reddit post IDs.
        reddit: An instance of the PRAW Reddit API client.
        rate_limit_sleep (int): Seconds to sleep between requests.
        retries (int): Number of retries for each post.
        retry_delay (int): Seconds to wait between retries.
    
    Returns:
        List[Dict[str, Any]]: Combined list of comment details from all posts.
    
    Raises:
        Exception: If one or more posts fail to fetch comments.
    """
    all_comments = []
    failed_ids = []
    
    for post_id in post_ids:
        print(f"Fetching comments for post ID: {post_id}")
        try:
            comments = fetch_comments(post_id, reddit, retries, retry_delay)
            all_comments.extend(comments)
            print(f"Successfully fetched {len(comments)} comments for post ID: {post_id}")
        except Exception as e:
            print(f"An error occurred while processing post ID {post_id}: {e}")
            failed_ids.append(post_id)
        time.sleep(rate_limit_sleep)
    
    if failed_ids:
        error_message = f"Failed to fetch comments for the following post IDs: {failed_ids}"
        print(error_message)
        # Optionally, write failed IDs to a file
        with open("failed_ids.txt", "w") as f:
            for fid in failed_ids:
                f.write(f"{fid}\n")
        raise Exception(error_message)
    
    return all_comments


def save_to_csv(df, filename):
    """
    Save reddit data to a CSV file using pandas DataFrame.

    Args:
        contents (list): A list of dictionaries containing details.
        filename (str): The name of the CSV file to save the data.
    """
    try:
        print(f"Saving reddits data to {filename}...")
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Data successfully saved to {filename}.")
    except Exception as e:
        print(f"An error occurred while saving to CSV: {e}")


df = pd.read_csv('all_final_posts.csv')
post_id_list = df['post_id'].to_list()
comment_df = pd.DataFrame(fetch_all_comments(post_id_list, reddit))
save_to_csv(comment_df, 'all_raw_comments.csv')