from clickhouse_client import get_result


def show_result(adid):

    if not adid:
        return "Advertising ID required"

    try:
        df = get_result(adid)
    except Exception as e:
        return str(e)

    if df is None or df.empty:
        return None

    return df