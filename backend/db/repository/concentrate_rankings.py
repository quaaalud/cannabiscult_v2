#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 21:10:27 2023

@author: dale
"""

from typing import List
from sqlalchemy.orm import Session
from schemas.concentrate_rankings import (
    CreateHiddenConcentrateRanking,
    CreateConcentrateRanking,
    HiddenConcentrateRanking,
)
from db.models.concentrate_rankings import (
    Hidden_Concentrate_Ranking,
    Vibe_Concentrate_Ranking,
    Concentrate_Ranking,
)
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import plotly.express as px


def create_concentrate_ranking(ranking: CreateConcentrateRanking, db: Session):
    ranking_data_dict = ranking.dict()
    created_ranking = Concentrate_Ranking(**ranking_data_dict)

    db.add(created_ranking)

    db.commit()
    db.refresh(created_ranking)

    return created_ranking


def create_hidden_concentrate_ranking(hidden_ranking: CreateHiddenConcentrateRanking, db: Session):
    ranking_data_dict = hidden_ranking.dict()
    created_ranking = Hidden_Concentrate_Ranking(**ranking_data_dict)
    try:
        db.add(created_ranking)
    except:
        db.rollback()
    else:
        db.commit()
        db.refresh(created_ranking)
    finally:
        return created_ranking


def create_vibe_concentrate_ranking(ranking: CreateConcentrateRanking, db: Session):
    ranking_data_dict = ranking.dict()
    created_ranking = Vibe_Concentrate_Ranking(**ranking_data_dict)
    try:
        db.add(created_ranking)
    except:
        db.rollback()
    else:
        db.commit()
        db.refresh(created_ranking)
    finally:
        return created_ranking


def return_all_hidden_concentrate_rankings(db: Session):
    try:
        return db.query(Hidden_Concentrate_Ranking).all()
    except:
        print("No concentrate ranking results returned")
        pass


class ConcentrateMysteryVotes:

    strains_dict = {
        "CP1": "Fruit Gusherz - Vivid",
        "CP2": "Papaya - Local",
        "CP3": "Mississippi Nights - Vibe",
    }

    def __init__(self, votes_path: str, voters_data_path: str = None):
        self.raw_data = self.import_data(Path(votes_path))
        self.all_ratings_over_time = self._average_ratings_over_time(self.raw_data)
        self.votes_by_user = self._group_ratings_by_user_and_strain(self.raw_data)
        self.strain_rankings = self._group_strain_and_rank_by_total(self.raw_data)
        self.voters_favorite_strains = self.find_favorite_strains(self.votes_by_user)
        if voters_data_path:
            self.voters_raw_data = self.import_data(Path(voters_data_path))
            self.filter_voters_data()

    @classmethod
    def import_data(cls, rankings: List[HiddenConcentrateRanking]) -> pd.DataFrame:
        # Convert list of objects to a DataFrame
        data = [
            {
                "strain": ranking.strain,
                "color_rating": ranking.color_rating,
                "consistency_rating": ranking.consistency_rating,
                # ... include other relevant fields
                "date_posted": ranking.date_posted,
            }
            for ranking in rankings
        ]

        df = pd.DataFrame(data)

        # Replace strain names using the dictionary
        df["strain"] = df["strain"].apply(lambda x: cls.strains_dict.get(x, x))

        return df.sort_values("date_posted")

    @staticmethod
    def _clean_date_col(df: pd.DataFrame, date_col: str = "date_posted") -> pd.DataFrame:
        df["datetime"] = df["date_posted"].copy()
        df["date_posted"] = df["datetime"].copy().dt.strftime("%Y-%m-%d %H:%M:%S")
        df["datetime"] = df["datetime"].copy().astype(str)
        return df.sort_values("date_posted")

    @classmethod
    def _clean_df_after_import(cls, df: pd.DataFrame) -> pd.DataFrame:
        df = cls._clean_date_col(df)
        try:
            df["strain"] = df["strain"].copy().replace(cls.strains_dict)
            return df.drop_duplicates(subset=["strain", "connoisseur", "id"]).drop(
                columns=["id"],
            )
        except KeyError:
            return (
                df.drop_duplicates(subset=["id", "email"])
                .drop(
                    columns=["id"],
                )
                .rename(
                    columns={
                        "email": "connoisseur",
                    }
                )
            )

    def filter_voters_data(self):
        connoisseur_values = self.raw_data["connoisseur"].unique()
        self.voters_raw_data = self.voters_raw_data[
            self.voters_raw_data["connoisseur"].isin(connoisseur_values)
        ]

    @staticmethod
    def _average_ratings_over_time(
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        groupby_cols = [col for col in df.columns if "_rating" in col]
        temp_df = df[["date_posted", "strain", *groupby_cols]].copy()
        data_df = temp_df.groupby(
            [
                "date_posted",
                "strain",
            ],
            as_index=True,
        ).mean()
        data_df["total_rating"] = data_df.mean(axis=1)
        for col in ["total_rating", *groupby_cols]:
            data_df[col] = round(data_df[col].copy(), 2)
        return data_df.reset_index()

    @staticmethod
    def _group_ratings_by_user_and_strain(
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        groupby_cols = [col for col in df.columns if "_rating" in col]
        temp_df = df[["connoisseur", "strain", *groupby_cols]].copy()
        data_df = temp_df.groupby(
            [
                "connoisseur",
                "strain",
            ],
            as_index=True,
        ).mean()
        data_df["total_rating"] = data_df.mean(axis=1)
        for col in ["total_rating", *groupby_cols]:
            data_df[col] = round(data_df[col].copy(), 2)
        return data_df.reset_index()

    @staticmethod
    def _group_strain_and_rank_by_total(
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        groupby_cols = [col for col in df.columns if "_rating" in col]
        temp_df = df[["strain", *groupby_cols]].copy()
        data_df = temp_df.groupby(
            [
                "strain",
            ],
            as_index=True,
        ).mean()
        data_df["total_rating"] = data_df.mean(axis=1)

        for col in ["total_rating", *groupby_cols]:
            data_df[col] = round(data_df[col].copy(), 2)
        return data_df.sort_values("total_rating").reset_index()

    @staticmethod
    def _merge_users_and_results(
        voting_results_df: pd.DataFrame, users_data_df: pd.DataFrame
    ) -> pd.DataFrame:
        temp_users_df = users_data_df.copy().drop(
            columns=[
                "date_posted",
                "datetime",
            ]
        )
        return pd.merge(
            voting_results_df, temp_users_df, how="inner", on="connoisseur"
        ).drop_duplicates(
            subset=[
                "strain",
                "connoisseur",
            ],
            keep="last",
        )

    @staticmethod
    def find_favorite_strains(
        df: pd.DataFrame, user_col: str = "connoisseur", strain_col: str = "strain"
    ):
        grouped_df = df.copy().groupby([user_col, strain_col]).mean().reset_index()
        favorite_strains = grouped_df.loc[grouped_df.groupby(user_col)["total_rating"].idxmax()][
            [user_col, strain_col]
        ]
        return favorite_strains.set_index(user_col)[strain_col]

    @staticmethod
    def _plot_all_ratings_over_time(data_df: pd.DataFrame, date_col: str = "date_posted"):
        df = data_df.copy()
        color_palette = sns.color_palette("husl", len(df.columns))
        df[date_col] = pd.to_datetime(df[date_col])
        vote_columns = [
            col for col in df.columns if col.endswith("_rating") and col != "total_rating"
        ]
        unique_strains = df["strain"].unique()
        for strain in unique_strains:
            strain_df = df[df["strain"] == strain]
            plt.figure(figsize=(14, 6))
            plt.title(f"Time-series Plot for {strain}")

            for idx, col in enumerate(vote_columns):
                sns.lineplot(x=date_col, y=col, data=strain_df, label=col, color=color_palette[idx])
            plt.xlabel("Time")
            plt.ylabel("Vote Value")
            plt.legend(title="Vote Categories")
            plt.show()

    @staticmethod
    def _plot_all_ratings_cumulative_over_time(
        data_df: pd.DataFrame, date_col: str = "date_posted"
    ):
        df = data_df.copy()
        color_palette = sns.color_palette("husl", len(df.columns))
        df[date_col] = pd.to_datetime(df[date_col])
        vote_columns = [
            col for col in df.columns if col.endswith("_rating") and col != "total_rating"
        ]
        unique_strains = df["strain"].unique()
        for strain in unique_strains:
            strain_df = df[df["strain"] == strain].sort_values(by=date_col)
            plt.figure(figsize=(14, 6))

            plt.title(f"Time-series Plot for {strain} (Cumulative Moving Average)")

            for idx, col in enumerate(vote_columns):
                strain_df[f"{col}_cma"] = strain_df[col].expanding().mean()
                sns.lineplot(
                    x="date_posted",
                    y=f"{col}_cma",
                    data=strain_df,
                    label=col,
                    color=color_palette[idx],
                )
            plt.xlabel("Date Posted")
            plt.ylabel("Cumulative Moving Average of Vote Value")
            plt.legend(title="Vote Categories")
            plt.show()

    @staticmethod
    def plot_methods_of_consumption_by_strain(data_df: pd.DataFrame):
        try:
            df = data_df.copy()
            plt.figure(figsize=(14, 6))
            plt.title("Methods of Consumption by Strain")
            sns.countplot(data=df, x="strain", hue="method_of_consumption", palette="husl")
            plt.ylabel("Count")
            plt.xlabel("Strain")
            plt.legend(title="Methods of Consumption")
            plt.show()
        except ValueError:
            pass

    @staticmethod
    def plot_average_ratings_by_users(data_df: pd.DataFrame):
        df = data_df.copy()
        vote_columns = [
            col for col in df.columns if col.endswith("_rating") and col != "total_rating"
        ]
        plt.figure(figsize=(14, 6))
        plt.title("Distribution of Average Votes Across Users")
        sns.boxplot(data=df[vote_columns], palette="husl")
        plt.ylabel("Average Vote Value")
        plt.xlabel("Vote Categories")
        plt.show()

    @staticmethod
    def plot_popular_strains_by_users(data_df: pd.DataFrame):
        df = data_df.copy()
        plt.figure(figsize=(14, 6))
        plt.title("Popular Strains Among Users")
        sns.countplot(data=df, y="strain", order=df["strain"].value_counts().index, palette="husl")
        plt.ylabel("Strain")
        plt.xlabel("Count")
        plt.show()

    @staticmethod
    def plot_top_strains_by_category(data_df: pd.DataFrame):
        df = data_df.copy()
        vote_columns = [
            col for col in df.columns if col.endswith("_rating") and col != "total_rating"
        ]
        plt.figure(figsize=(14, 6))
        plt.title("Top Strains in Each Vote Category")
        sns.barplot(
            data=df.melt(
                id_vars="strain",
                value_vars=vote_columns,
                var_name="Vote Category",
                value_name="Average Vote",
            ),
            x="Vote Category",
            y="Average Vote",
            hue="strain",
            palette="husl",
        )
        plt.ylabel("Average Vote Value")
        plt.xlabel("Vote Categories")
        plt.legend(title="Strains", bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_geographical_distribution(data_df: pd.DataFrame):
        df = data_df.copy()
        plt.figure(figsize=(14, 6))
        plt.title("Geographical Distribution of Voters")
        sns.countplot(
            data=df, x="zip_code", order=df["zip_code"].value_counts().index, palette="husl"
        )
        plt.ylabel("Count")
        plt.xlabel("Zip Code")
        plt.xticks(rotation=45)
        plt.show()

    @staticmethod
    def plot_rating_correlation(data_df: pd.DataFrame):
        plt.figure(figsize=(10, 8))
        sns.heatmap(data_df.corr(), annot=True, cmap="coolwarm")
        plt.title("Correlation Heatmap of Ratings")
        plt.show()

    # New function: Box Plot for Rating Distributions
    @staticmethod
    def plot_rating_distributions(data_df: pd.DataFrame):
        plt.figure(figsize=(14, 6))
        sns.boxplot(data=data_df)
        plt.title("Distribution of Ratings Across Strains")
        plt.ylabel("Ratings")
        plt.xlabel("Rating Categories")
        plt.show()

    @staticmethod
    def plot_detailed_rating_distributions(data_df: pd.DataFrame):
        plt.figure(figsize=(14, 6))
        sns.violinplot(data=data_df)
        plt.title("Detailed Distribution of Ratings Across Strains")
        plt.ylabel("Ratings")
        plt.xlabel("Rating Categories")
        plt.show()

    @staticmethod
    def plot_strain_comparison(data_df: pd.DataFrame):
        vote_categories = [col for col in data_df.columns if "_rating" in col]
        for category in vote_categories:
            plt.figure(figsize=(10, 6))
            sns.barplot(data=data_df, x="strain", y=category, palette="viridis")
            plt.title(f"Strain Comparison in {category}")
            plt.ylabel("Average Rating")
            plt.xlabel("Strain")
            plt.show()

    @staticmethod
    def plot_user_preferences(data_df: pd.DataFrame):
        user_pref = data_df.groupby(["connoisseur", "strain"]).mean()["total_rating"]
        user_pref.unstack().plot(kind="bar", stacked=True, figsize=(14, 8))
        plt.title("User Preferences for Different Strains")
        plt.ylabel("Total Vote")
        plt.xlabel("User")
        plt.legend(title="Strains", bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.show()

    # Function for Visualizing All Users' Votes
    @staticmethod
    def plot_users_vs_votes(data_df: pd.DataFrame):
        plt.figure(figsize=(14, 10))
        sns.heatmap(
            data_df.pivot_table(index="connoisseur", columns="strain", values="total_rating"),
            annot=True,
            cmap="coolwarm",
        )
        plt.title("Heatmap of User Votes for Each Strain")
        plt.ylabel("User")
        plt.xlabel("Strain")
        plt.show()

    @staticmethod
    def generate_interactive_plot(data_df: pd.DataFrame) -> dict:
        fig = px.bar(data_df, x="Strain", y="Votes", color="Strain")
        return fig.to_json()
