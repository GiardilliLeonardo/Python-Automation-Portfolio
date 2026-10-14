# Task: Databricks Expert Needed – Fix Out-of-Memory Error in Multi-Step Pipeline

import gc
from typing import List
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window


def create_optimized_spark_session(app_name: str = "PipelineOOMFix") -> SparkSession:
    """Inizializza la SparkSession con configurazioni anti
