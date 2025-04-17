import unittest
from unittest.mock import patch, MagicMock
from app.services import news


class TestNewsService(unittest.TestCase):

    @patch('app.services.news.requests.get')
    def test_get_recent_stock_news_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "articles": [
                {
                    "title": "Market Rally",
                    "description": "Stocks are up.",
                    "url": "https://example.com/article",
                    "urlToImage": "https://cdn.example.com/news.jpg"
                },
                {
                    "title": "Tech Stocks Surge",
                    "description": "Tech is leading gains.",
                    "url": "https://example.com/tech",
                    "urlToImage": "https://example.com/favicon.ico"
                }
            ]
        }

        articles = news.get_recent_stock_news(count=2)
        self.assertEqual(len(articles), 2)

        # First article keeps its image
        self.assertEqual(articles[0]['image_url'], "https://cdn.example.com/news.jpg")

        # Second article should use fallback
        self.assertEqual(articles[1]['image_url'], "/static/default-news.jpg")

    @patch('app.services.news.requests.get', side_effect=Exception("API error"))
    def test_get_recent_stock_news_failure(self, mock_get):
        articles = news.get_recent_stock_news(count=3)
        self.assertEqual(articles, [])  # Should gracefully fall back to empty list


if __name__ == '__main__':
    unittest.main()
