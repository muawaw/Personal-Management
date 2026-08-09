import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from backend.dashboard.dashboard import (
        DASHBOARD_FILTER_PRESETS,
        DASHBOARD_PAGE_SIZE_DEFAULT,
        get_dashboard_data,
        get_dashboard_data_paginated,
        get_dashboard_date_filter_range,
        get_dashboard_summary,
    )
else:
    from .dashboard import (
        DASHBOARD_FILTER_PRESETS,
        DASHBOARD_PAGE_SIZE_DEFAULT,
        get_dashboard_data,
        get_dashboard_data_paginated,
        get_dashboard_date_filter_range,
        get_dashboard_summary,
    )

__all__ = [
    "DASHBOARD_FILTER_PRESETS",
    "DASHBOARD_PAGE_SIZE_DEFAULT",
    "get_dashboard_data",
    "get_dashboard_data_paginated",
    "get_dashboard_date_filter_range",
    "get_dashboard_summary",
]


if __name__ == "__main__":
    print("Dashboard package initialized.")
    print("Import it with: from backend.dashboard import get_dashboard_data")
