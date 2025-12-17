"""
Script to hash-protect sensitive ID columns in CSV files.
Uses HMAC-SHA256 with a user-specified password for consistent, deterministic hashing.
Same input + same password = same hash output (allows joining on IDs).
"""

import pandas as pd
import hmac
import hashlib
import argparse
from pathlib import Path


def hash_value(value, password: str) -> str:
    """
    Create a deterministic hash of a value using HMAC-SHA256.
    Same value + same password always produces the same hash.
    """
    if pd.isna(value):
        return value

    value_str = str(value)
    hash_bytes = hmac.new(
        password.encode('utf-8'),
        value_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    # Return first 16 chars for readability (still 64 bits of entropy)
    return hash_bytes[:16]


def hash_columns(df: pd.DataFrame, columns: list, password: str) -> pd.DataFrame:
    """Hash specified columns in a DataFrame."""
    df = df.copy()
    for col in columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: hash_value(x, password))
        else:
            print(f"Warning: Column '{col}' not found in DataFrame")
    return df


def process_file(input_path: str, output_path: str, columns: list, password: str):
    """Read CSV, hash specified columns, and save to output."""
    print(f"Processing: {input_path}")
    df = pd.read_csv(input_path)

    # Show which columns will be hashed
    existing_cols = [c for c in columns if c in df.columns]
    print(f"  Hashing columns: {existing_cols}")

    df_hashed = hash_columns(df, columns, password)
    df_hashed.to_csv(output_path, index=False)
    print(f"  Saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Hash-protect ID columns in CSV files using HMAC-SHA256"
    )
    parser.add_argument("input", help="Input CSV file or directory")
    parser.add_argument("-o", "--output", help="Output file/directory (default: adds '_hashed' suffix)")
    parser.add_argument("-p", "--password", required=True, help="Password/key for HMAC hashing")
    parser.add_argument(
        "-c", "--columns",
        nargs="+",
        default=["post_id", "author_id", "comment_id", "author"],
        help="Columns to hash (default: post_id author_id comment_id author)"
    )

    args = parser.parse_args()
    input_path = Path(args.input)

    if input_path.is_file():
        # Single file
        if args.output:
            output_path = args.output
        else:
            output_path = input_path.parent / f"{input_path.stem}_hashed{input_path.suffix}"
        process_file(str(input_path), str(output_path), args.columns, args.password)

    elif input_path.is_dir():
        # Directory - process all CSVs
        output_dir = Path(args.output) if args.output else input_path / "hashed"
        output_dir.mkdir(exist_ok=True)

        for csv_file in input_path.glob("*.csv"):
            output_path = output_dir / f"{csv_file.stem}_hashed.csv"
            process_file(str(csv_file), str(output_path), args.columns, args.password)
    else:
        print(f"Error: {input_path} not found")
        return 1

    print("\nDone!")
    return 0


if __name__ == "__main__":
    exit(main())
