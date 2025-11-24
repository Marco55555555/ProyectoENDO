import pandas as pd
import logging
from textblob import TextBlob

def analyze_sentiment(text):
    if pd.isna(text):
        return 0
    return TextBlob(text).sentiment.polarity

def transform_data(sales_df, social_df):
    logging.info("Procesando y uniendo datasets...")

    # 1. NORMALIZACIÓN DE FECHAS
    sales_df["date"] = pd.to_datetime(sales_df["date"])
    social_df["date"] = pd.to_datetime(social_df["date"])

    # 2. ANALIZAR SENTIMIENTO
    social_df["sentiment"] = social_df["post_text"].apply(analyze_sentiment)

    # 3. PROMEDIO DE SENTIMIENTO POR FECHA
    avg_sentiment = (
        social_df.groupby("date")["sentiment"]
        .mean()
        .reset_index()
    )

    # 4. MERGE CON DATASET DE VENTAS
    merged_df = pd.merge(sales_df, avg_sentiment, on="date", how="left")

    # 5. CREAR COLUMNA DE VENTAS
    merged_df["actual_selling_price"] = pd.to_numeric(
        merged_df["actual_selling_price"], errors="coerce"
    )
    merged_df["quantity_sold"] = pd.to_numeric(
        merged_df["quantity_sold"], errors="coerce"
    )

    merged_df["sales"] = (
        merged_df["actual_selling_price"] * merged_df["quantity_sold"]
    )

    logging.info("Transformación completada.")

    return merged_df
