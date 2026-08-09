import os
from datetime import date, timedelta

import pytest

from backend.dashboard.dashboard import (
    DASHBOARD_FILTER_PRESETS,
    get_dashboard_data,
    get_dashboard_date_filter_range,
    get_dashboard_summary,
)


def test_dashboard_filter_presets():
    assert "current_month" in DASHBOARD_FILTER_PRESETS
    assert "previous_month" in DASHBOARD_FILTER_PRESETS
    assert "last_3_months" in DASHBOARD_FILTER_PRESETS
    assert "last_6_months" in DASHBOARD_FILTER_PRESETS
    assert "last_year" in DASHBOARD_FILTER_PRESETS
    assert "all_time" in DASHBOARD_FILTER_PRESETS


def test_get_dashboard_date_filter_range_current_month():
    result = get_dashboard_date_filter_range("current_month")
    assert result["start_date"] is not None
    assert result["end_date"] == date.today().isoformat()


def test_get_dashboard_date_filter_range_previous_month():
    result = get_dashboard_date_filter_range("previous_month")
    assert result["start_date"] is not None
    assert result["end_date"] is not None
    assert result["start_date"] < result["end_date"]


def test_get_dashboard_date_filter_range_all_time():
    result = get_dashboard_date_filter_range("all_time")
    assert result["start_date"] is None
    assert result["end_date"] is None


def test_get_dashboard_data_invalid_date():
    with pytest.raises(ValueError):
        get_dashboard_data(start_date="not-a-date")


def test_get_dashboard_summary_invalid_date():
    with pytest.raises(ValueError):
        get_dashboard_summary(end_date="2024-02-30")
