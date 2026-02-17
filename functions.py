import pandas as pd
import os

_DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "space_missions.csv")
_df = None


def _load_data():
    global _df
    if _df is None:
        _df = pd.read_csv(_DATA_PATH)
        _df['Date'] = pd.to_datetime(_df['Date'], format='%Y-%m-%d', errors='coerce')
        _df['Price'] = pd.to_numeric(
            _df['Price'].astype(str).str.replace(',', '').str.replace('$', '').str.strip(),
            errors='coerce'
        )
    return _df


def getMissionCountByCompany(companyName: str) -> int:
    if not isinstance(companyName, str):
        return 0
    df = _load_data()
    return int(df[df['Company'] == companyName].shape[0])


def getSuccessRate(companyName: str) -> float:
    if not isinstance(companyName, str):
        return 0.0
    df = _load_data()
    company_df = df[df['Company'] == companyName]
    if company_df.empty:
        return 0.0
    successes = company_df[company_df['MissionStatus'] == 'Success'].shape[0]
    return round((successes / company_df.shape[0]) * 100, 2)


def getMissionsByDateRange(startDate: str, endDate: str) -> list:
    if not isinstance(startDate, str) or not isinstance(endDate, str):
        return []
    df = _load_data()
    try:
        start = pd.to_datetime(startDate)
        end = pd.to_datetime(endDate)
    except Exception:
        return []
    if start > end:
        return []
    mask = (df['Date'] >= start) & (df['Date'] <= end)
    result = df[mask].sort_values('Date')
    return result['Mission'].tolist()


def getTopCompaniesByMissionCount(n: int) -> list:
    if isinstance(n, bool) or not isinstance(n, int) or n <= 0:
        return []
    df = _load_data()
    counts = df.groupby('Company').size().reset_index(name='count')
    counts = counts.sort_values(['count', 'Company'], ascending=[False, True])
    return [(row['Company'], int(row['count'])) for _, row in counts.head(n).iterrows()]


def getMissionStatusCount() -> dict:
    df = _load_data()
    result = {
        "Success": 0,
        "Failure": 0,
        "Partial Failure": 0,
        "Prelaunch Failure": 0
    }
    status_counts = df['MissionStatus'].value_counts().to_dict()
    for key, val in status_counts.items():
        result[key] = int(val)
    return result


def getMissionsByYear(year: int) -> int:
    if isinstance(year, bool) or not isinstance(year, int):
        return 0
    df = _load_data()
    return int(df[df['Date'].dt.year == year].shape[0])


def getMostUsedRocket() -> str:
    df = _load_data()
    counts = df.groupby('Rocket').size().reset_index(name='count')
    counts = counts.sort_values(['count', 'Rocket'], ascending=[False, True])
    return str(counts.iloc[0]['Rocket'])


def getAverageMissionsPerYear(startYear: int, endYear: int) -> float:
    if isinstance(startYear, bool) or isinstance(endYear, bool):
        return 0.0
    if not isinstance(startYear, int) or not isinstance(endYear, int):
        return 0.0
    num_years = endYear - startYear + 1
    if num_years <= 0:
        return 0.0
    df = _load_data()
    mask = (df['Date'].dt.year >= startYear) & (df['Date'].dt.year <= endYear)
    total = df[mask].shape[0]
    return round(total / num_years, 2)
