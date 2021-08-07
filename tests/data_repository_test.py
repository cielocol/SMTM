import requests
import unittest
from datetime import datetime
from smtm import DataRepository
from unittest.mock import *


class DataRepositoryTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @patch("requests.get")
    def test__fetch_from_upbit_up_to_200_should_call_get_correctly(self, mock_get):
        dummy_response = MagicMock()
        expected_value = [
            {
                "market": "mango",
                "candle_date_time_utc": "2020-03-10T13:52:00",
                "candle_date_time_kst": "2020-03-10T22:52:00",
                "opening_price": 9777000.00000000,
                "high_price": 9778000.00000000,
                "low_price": 9763000.00000000,
                "trade_price": 9778000.00000000,
                "timestamp": 1583848334534,
                "candle_acc_trade_price": 11277224.71063000,
                "candle_acc_trade_volume": 1.15377852,
                "unit": 1,
            },
            {
                "market": "mango",
                "candle_date_time_utc": "2020-03-10T13:52:00",
                "candle_date_time_kst": "2020-03-10T22:52:00",
                "opening_price": 8777000.00000000,
                "high_price": 8778000.00000000,
                "low_price": 8763000.00000000,
                "trade_price": 8778000.00000000,
                "timestamp": 1583848334534,
                "candle_acc_trade_price": 11277224.71063000,
                "candle_acc_trade_volume": 1.15377852,
                "unit": 1,
            },
        ]
        dummy_response.json.return_value = expected_value
        mock_get.return_value = dummy_response

        end = "2020-03-20T00:00:00"
        repo = DataRepository()
        data = repo._fetch_from_upbit_up_to_200(end, 41760, "mango")
        mock_get.assert_called_once_with(
            "https://api.upbit.com/v1/candles/minutes/1",
            params={"market": "mango", "to": "2020-03-19T15:00:00Z", "count": 41760},
        )
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["opening_price"], 8777000.00000000)
        self.assertEqual(data[0]["high_price"], 8778000.00000000)
        self.assertEqual(data[0]["low_price"], 8763000.00000000)
        self.assertEqual(data[0]["closing_price"], 8778000.00000000)
        self.assertEqual(data[1]["opening_price"], 9777000.00000000)
        self.assertEqual(data[1]["high_price"], 9778000.00000000)
        self.assertEqual(data[1]["low_price"], 9763000.00000000)
        self.assertEqual(data[1]["closing_price"], 9778000.00000000)

    @patch("requests.get")
    def test__fetch_from_upbit_up_to_200_NOT_throw_UserWarning_when_receive_invalid_data(
        self, mock_get
    ):
        end = "2020-03-20T00:00:00"
        repo = DataRepository()
        dummy_response = MagicMock()
        dummy_response.json.side_effect = ValueError()
        mock_get.return_value = dummy_response

        with self.assertRaises(UserWarning):
            data = repo._fetch_from_upbit_up_to_200(end, 200, "mango")
            self.assertIsNone(data)

    @patch("requests.get")
    def test__fetch_from_upbit_up_to_200_NOT_throw_UserWarning_when_receive_response_error(
        self, mock_get
    ):
        end = "2020-03-20T00:00:00"
        repo = DataRepository()
        dummy_response = MagicMock()
        dummy_response.json.return_value = [{"market": "apple"}, {"market": "banana"}]
        dummy_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "HTTPError dummy exception"
        )
        mock_get.return_value = dummy_response

        with self.assertRaises(UserWarning):
            data = repo._fetch_from_upbit_up_to_200(end, 200, "mango")
            self.assertIsNone(data)

    @patch("smtm.DateConverter.to_end_min")
    def test__fetch_from_upbit_should_call__fetch_from_upbit_up_to_200(self, mock_to_end_min):
        start = "2020-03-20T00:00:00"
        end = "2020-03-21T00:00:00"
        repo = DataRepository()
        repo._fetch_from_upbit_up_to_200 = MagicMock(side_effect=[["a", "b"], ["c", "d"], ["e"]])
        mock_to_end_min.return_value = [
            ("2020-03-20T00:00:00", 200),
            ("2020-03-20T00:00:00", 200),
            ("2020-03-20T00:00:00", 110),
        ]
        result = repo._fetch_from_upbit(start, end, "mango")

        mock_to_end_min.assert_called_once_with(start=start, end=end, max_count=200)
        self.assertEqual(result, ["a", "b", "c", "d", "e"])