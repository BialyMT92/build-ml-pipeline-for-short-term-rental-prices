#!/usr/bin/env python
import argparse
import logging
import pandas as pd
import wandb

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")

    logger.info("Downloading artifact")
    artifact = run.use_artifact(args.input_artifact)
    artifact_path = artifact.file()

    df = pd.read_csv(artifact_path)

    # Drop outliers
    min_price = args.min_price
    max_price = args.max_price
    idx = df['price'].between(min_price, max_price)
    df = df[idx].copy()
    idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx].copy()
    # Convert last_review to datetime
    df['last_review'] = pd.to_datetime(df['last_review'])

    filename = "clean_sample.csv"
    df.to_csv(filename, index=False)

    artifact = wandb.Artifact(
        name=args.output_artifact,
        type=args.output_type,
        description=args.output_description
    )

    artifact.add_file(filename)

    logger.info("Logging artifact")
    run.log_artifact(artifact)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Preprocess a dataset",
        fromfile_prefix_chars="@",
    )

    parser.add_argument(
        "--input_artifact",
        type=str,
        help="Fully-qualified name for the input artifact",
        required=True,
    )

    parser.add_argument(
        "--output_artifact", type=str, help="Name for the output artifact", required=True
    )

    parser.add_argument(
        "--output_type", type=str, help="Type for the artifact", required=True
    )

    parser.add_argument(
        "--output_description",
        type=str,
        help="Description for the artifact",
        required=True,
    )

    parser.add_argument(
        "--min_price",
        type=float,
        help="Minimum rental price for filtering",
        required=True,
    )

    parser.add_argument(
        "--max_price",
        type=float,
        help="Maximum rental price for filtering",
        required=True,
    )

    args = parser.parse_args()

    go(args)
