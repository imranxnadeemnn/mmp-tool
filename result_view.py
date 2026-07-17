from clickhouse_client import get_results


def show_result():
    try:
        df = get_results()
    except Exception as e:
        return str(e)

    if df is None or df.empty:
        return None

    return df
