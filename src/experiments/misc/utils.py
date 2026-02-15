from pathlib import Path
import pandas as pd


def load_dataset(
    path: Path,
    *,
    file_format: str | None = None,
    columns: list[str] | None = None,
) -> pd.DataFrame:
    """
    Load a dataset from disk.

    Parameters
    ----------
    path : Path
        Path to the dataset file.
    file_format : str, optional
        File format override ("parquet", "csv", "json").
        If None, inferred from file extension.
    columns : list[str], optional
        Subset of columns to load.

    Returns
    -------
    pd.DataFrame
        Loaded dataset.

    Raises
    ------
    FileNotFoundError
        If the dataset file does not exist.
    ValueError
        If the file format is unsupported.
    """

    if not path.exists():
        raise FileNotFoundError(f"Dataset not found at: {path}")

    fmt = file_format or path.suffix.replace(".", "").lower()

    if fmt == "parquet":
        return pd.read_parquet(path, columns=columns)

    if fmt == "csv":
        return pd.read_csv(path, usecols=columns)

    if fmt == "json":
        return pd.read_json(path)

    raise ValueError(f"Unsupported dataset format: {fmt}")


def log_dataset_metadata(
    name: str,
    version: str,
    path: str,
    n_rows: int,
    n_cols: int,
):
    import mlflow

    mlflow.log_param("dataset_name", name)
    mlflow.log_param("dataset_version", version)
    mlflow.log_param("dataset_path", path)
    mlflow.log_param("dataset_rows", n_rows)
    mlflow.log_param("dataset_cols", n_cols)
