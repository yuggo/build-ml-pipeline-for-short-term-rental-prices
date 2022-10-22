#!/usr/bin/env python
"""
Performs basic cleaning on the data and save the results in Weights & Biases
"""
import argparse
import logging
import wandb
import pandas as pd

from wandb_utils.log_artifact import log_artifact

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    # artifact_local_path = run.use_artifact(args.input_artifact).file()

    ######################
    # YOUR CODE HERE     #
    ######################
    logger.info("Reading data")
    artifact = run.use_artifact(args.raw_data)
    artifact_path = artifact.file()

    df = pd.read_csv(artifact_path)

    logger.info("Cleaning data")
    idx = df['price'].between(args.min_price, args.max_price)
    df = df[idx].copy()
    # Convert last_review to datetime
    df['last_review'] = pd.to_datetime(df['last_review'])

    # new fix for data check range issues
    idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx].copy()

    logger.info("Saving data")
    df.to_csv("clean_sample.csv", index=False)

    logger.info("Loging clean data artifact")
    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description
    )

    artifact.add_file("clean_sample.csv")
    run.log_artifact(artifact)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="This step cleans the data")


    parser.add_argument(
        "--raw_data",
        type=str,
        help="Name of the raw data to use",
        required=True
    )

    parser.add_argument(
        "--output_artifact",
        type=str,
        help="Name of the cleaned data",
        required=True
    )

    parser.add_argument(
        "--output_type",
        type=str,
        help="The type of the output artifact used to categorize the artifact in Weights&Biases",
        required=True
    )

    parser.add_argument(
        "--output_description",
        type=str,
        help="The description of the output.",
        required=True
    )

    parser.add_argument(
        "--min_price",
        type=float,
        help="The minimum of the range used to treat outliers",
        required=True
    )

    parser.add_argument(
        "--max_price",
        type=float,
        help="The maximum of the range used to treat outliers",
        required=True
    )
    args = parser.parse_args()

    go(args)
