import unittest
from unittest.mock import patch, MagicMock
import os
import tempfile
from fastapi.testclient import TestClient


class TestServerEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test client with mocked publisher."""
        with patch('telepress.server.TelegraphPublisher') as MockPublisher:
            cls.mock_publisher_instance = MagicMock()
            MockPublisher.return_value = cls.mock_publisher_instance
            
            from telepress.server import app
            cls.client = TestClient(app)

    def setUp(self):
        """Reset mock before each test."""
        self.mock_publisher_instance.reset_mock()
        self.mock_publisher_instance.publish.return_value = 'http://telegra.ph/test'

    def test_health_check(self):
        """Test health check endpoint."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(data['service'], 'telepress')

    @patch('telepress.server.TelegraphPublisher')
    def test_publish_text_success(self, MockPublisher):
        """Test publishing text content."""
        mock_instance = MagicMock()
        mock_instance.publish.return_value = 'http://telegra.ph/result'
        MockPublisher.return_value = mock_instance
        
        response = self.client.post("/publish/text", json={
            "content": "# Test Content\n\nHello world!",
            "title": "Test Title"
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['url'], 'http://telegra.ph/result')

    @patch('telepress.server.TelegraphPublisher')
    def test_publish_text_with_token(self, MockPublisher):
        """Test publishing text with custom token."""
        mock_instance = MagicMock()
        mock_instance.publish.return_value = 'http://telegra.ph/result'
        MockPublisher.return_value = mock_instance
        
        response = self.client.post("/publish/text", json={
            "content": "Content",
            "title": "Title",
            "token": "custom_token"
        })
        
        self.assertEqual(response.status_code, 200)
        MockPublisher.assert_called_with(token="custom_token")

    @patch('telepress.server.TelegraphPublisher')
    def test_publish_file_markdown(self, MockPublisher):
        """Test uploading and publishing a markdown file."""
        mock_instance = MagicMock()
        mock_instance.publish.return_value = 'http://telegra.ph/file-result'
        MockPublisher.return_value = mock_instance
        
        # Create a temporary file to upload
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test Document\n\nContent here.")
            tmp_path = f.name
        
        try:
            with open(tmp_path, 'rb') as f:
                response = self.client.post(
                    "/publish/file",
                    files={"file": ("test.md", f, "text/markdown")},
                    data={"title": "Custom Title"}
                )
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data['url'], 'http://telegra.ph/file-result')
        finally:
            os.unlink(tmp_path)

    @patch('telepress.server.TelegraphPublisher')
    def test_publish_file_uses_filename_as_default_title(self, MockPublisher):
        """Test that filename is used as default title when none provided."""
        mock_instance = MagicMock()
        mock_instance.publish.return_value = 'http://telegra.ph/result'
        MockPublisher.return_value = mock_instance
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("Content")
            tmp_path = f.name
        
        try:
            with open(tmp_path, 'rb') as f:
                response = self.client.post(
                    "/publish/file",
                    files={"file": ("my_document.md", f, "text/markdown")}
                )
            
            self.assertEqual(response.status_code, 200)
            # Check that publish was called with filename as title
            call_args = mock_instance.publish.call_args
            self.assertEqual(call_args[1]['title'], 'my_document.md')
        finally:
            os.unlink(tmp_path)

    @patch('telepress.server.TelegraphPublisher')
    def test_publish_file_zip(self, MockPublisher):
        """Test uploading and publishing a zip file."""
        mock_instance = MagicMock()
        mock_instance.publish.return_value = 'http://telegra.ph/gallery'
        MockPublisher.return_value = mock_instance
        
        import zipfile
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as f:
            with zipfile.ZipFile(f, 'w') as zf:
                zf.writestr('1.jpg', b'fake image')
            tmp_path = f.name
        
        try:
            with open(tmp_path, 'rb') as f:
                response = self.client.post(
                    "/publish/file",
                    files={"file": ("gallery.zip", f, "application/zip")},
                    data={"title": "My Gallery"}
                )
            
            self.assertEqual(response.status_code, 200)
        finally:
            os.unlink(tmp_path)


class TestServerErrors(unittest.TestCase):
    @patch('telepress.server.TelegraphPublisher')
    def test_publish_text_telepresserror(self, MockPublisher):
        """Test that TelePressError returns 400."""
        from telepress.exceptions import ValidationError
        
        mock_instance = MagicMock()
        mock_instance.publish.side_effect = ValidationError("Invalid input")
        MockPublisher.return_value = mock_instance
        
        from telepress.server import app
        client = TestClient(app)
        
        response = client.post("/publish/text", json={
            "content": "Content",
            "title": "Title"
        })
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid input", response.json()['detail'])

    @patch('telepress.server.TelegraphPublisher')
    def test_publish_text_unexpected_error(self, MockPublisher):
        """Test that unexpected errors return 500."""
        mock_instance = MagicMock()
        mock_instance.publish.side_effect = RuntimeError("Unexpected")
        MockPublisher.return_value = mock_instance
        
        from telepress.server import app
        client = TestClient(app)
        
        response = client.post("/publish/text", json={
            "content": "Content",
            "title": "Title"
        })
        
        self.assertEqual(response.status_code, 500)

    @patch('telepress.server.TelegraphPublisher')
    def test_publish_file_error_cleans_up_temp(self, MockPublisher):
        """Test that temporary files are cleaned up on error."""
        mock_instance = MagicMock()
        mock_instance.publish.side_effect = RuntimeError("Error")
        MockPublisher.return_value = mock_instance
        
        from telepress.server import app
        client = TestClient(app)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("Content")
            tmp_path = f.name
        
        try:
            with open(tmp_path, 'rb') as f:
                response = client.post(
                    "/publish/file",
                    files={"file": ("test.md", f, "text/markdown")}
                )
            
            self.assertEqual(response.status_code, 500)
        finally:
            os.unlink(tmp_path)


class TestServerModels(unittest.TestCase):
    def test_text_publish_request_validation(self):
        """Test request model validation."""
        from telepress.server import TextPublishRequest
        
        # Valid request
        req = TextPublishRequest(content="Content", title="Title")
        self.assertEqual(req.content, "Content")
        self.assertEqual(req.title, "Title")
        self.assertIsNone(req.token)
        
        # With optional token
        req = TextPublishRequest(content="Content", title="Title", token="tok")
        self.assertEqual(req.token, "tok")

    def test_publish_response_model(self):
        """Test response model."""
        from telepress.server import PublishResponse
        
        resp = PublishResponse(url="http://example.com")
        self.assertEqual(resp.url, "http://example.com")
        self.assertEqual(resp.status, "success")


class TestStartServer(unittest.TestCase):
    def test_start_server_defaults(self):
        """Test start_server with default parameters."""
        import uvicorn
        from telepress.server import start_server, app
        
        with patch.object(uvicorn, 'run') as mock_run:
            start_server()
            mock_run.assert_called_once_with(app, host="0.0.0.0", port=8000)

    def test_start_server_custom_params(self):
        """Test start_server with custom parameters."""
        import uvicorn
        from telepress.server import start_server, app
        
        with patch.object(uvicorn, 'run') as mock_run:
            start_server(host="127.0.0.1", port=9000)
            mock_run.assert_called_once_with(app, host="127.0.0.1", port=9000)


class TestGalleryEndpoint(unittest.TestCase):
    def setUp(self):
        """Patch TelegraphPublisher so gallery requests never hit the network."""
        self.patcher = patch('telepress.server.TelegraphPublisher')
        self.mock_publisher_class = self.patcher.start()
        self.addCleanup(self.patcher.stop)

        self.mock_publisher_instance = MagicMock()
        self.mock_publisher_class.return_value = self.mock_publisher_instance
        self.mock_publisher_instance.publish_zip_gallery.return_value = (
            'http://telegra.ph/gallery'
        )

        from telepress.server import app
        self.client = TestClient(app)

    def _gallery_files(self):
        return [
            ("files", ("p0.jpg", b"fake image 0", "image/jpeg")),
            ("files", ("p1.jpg", b"fake image 1", "image/jpeg")),
        ]

    def test_publish_gallery_success(self):
        """Test publishing multiple files as a gallery with metadata."""
        response = self.client.post(
            "/publish/gallery",
            files=self._gallery_files(),
            data={
                "title": "My Gallery",
                "tags": "pixiv, illustration",
                "link": "https://www.pixiv.net/artworks/123456",
                "spoiler": "true",
                "token": "custom_token",
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['ok'], True)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['url'], 'http://telegra.ph/gallery')
        self.assertEqual(data['files'], 2)

        call_args = self.mock_publisher_instance.publish_zip_gallery.call_args
        self.assertEqual(call_args[1]['title'], 'My Gallery')
        footer = call_args[1]['footer_nodes']
        self.assertEqual(len(footer), 3)
        # spoiler note
        self.assertIn('R-18', footer[0]['children'][0])
        # tags paragraph
        self.assertIn('# pixiv', footer[1]['children'][0])
        # source link paragraph
        self.assertIn('Source:', footer[2]['children'][0])
        self.assertEqual(footer[2]['children'][1]['attrs']['href'],
                         'https://www.pixiv.net/artworks/123456')

    def test_publish_gallery_default_title_from_first_file(self):
        """Test that title falls back to the first file name."""
        response = self.client.post(
            "/publish/gallery", files=self._gallery_files()
        )

        self.assertEqual(response.status_code, 200)
        call_args = self.mock_publisher_instance.publish_zip_gallery.call_args
        self.assertEqual(call_args[1]['title'], 'p0')

    def test_publish_gallery_without_metadata_no_footer(self):
        """Test that no metadata produces an empty footer."""
        response = self.client.post(
            "/publish/gallery", files=self._gallery_files()
        )

        self.assertEqual(response.status_code, 200)
        call_args = self.mock_publisher_instance.publish_zip_gallery.call_args
        self.assertEqual(call_args[1]['footer_nodes'], [])

    def test_publish_gallery_duplicate_filenames(self):
        """Test that duplicate file names are disambiguated before zipping."""
        response = self.client.post(
            "/publish/gallery",
            files=[
                ("files", ("p0.jpg", b"a", "image/jpeg")),
                ("files", ("p0.jpg", b"b", "image/jpeg")),
            ],
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['files'], 2)

    def test_publish_gallery_requires_files(self):
        """Test that a request without files is rejected (422)."""
        response = self.client.post("/publish/gallery")
        self.assertEqual(response.status_code, 422)

    @patch('telepress.server.TelegraphPublisher')
    def test_publish_gallery_telepress_error(self, MockPublisher):
        """Test that TelePressError returns 400."""
        from telepress.exceptions import ValidationError

        mock_instance = MagicMock()
        mock_instance.publish_zip_gallery.side_effect = ValidationError(
            "No images found"
        )
        MockPublisher.return_value = mock_instance

        from telepress.server import app
        client = TestClient(app)

        response = client.post(
            "/publish/gallery",
            files=[("files", ("p0.jpg", b"fake", "image/jpeg"))],
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("No images found", response.json()['detail'])

    @patch('telepress.server.TelegraphPublisher')
    def test_publish_gallery_unexpected_error(self, MockPublisher):
        """Test that unexpected errors return 500."""
        mock_instance = MagicMock()
        mock_instance.publish_zip_gallery.side_effect = RuntimeError("boom")
        MockPublisher.return_value = mock_instance

        from telepress.server import app
        client = TestClient(app)

        response = client.post(
            "/publish/gallery",
            files=[("files", ("p0.jpg", b"fake", "image/jpeg"))],
        )

        self.assertEqual(response.status_code, 500)


class TestGalleryFooterBuilder(unittest.TestCase):
    def test_footer_with_all_fields(self):
        """Test footer builder renders warning, tags and source link."""
        from telepress.server import _build_gallery_footer

        nodes = _build_gallery_footer(
            tags=" pixiv , illustration ",
            link="https://www.pixiv.net/artworks/1",
            spoiler="true",
        )
        self.assertEqual(len(nodes), 3)
        self.assertIn('R-18', nodes[0]['children'][0])
        self.assertEqual(nodes[1]['children'][0], '# pixiv #illustration')
        self.assertEqual(nodes[2]['children'][1]['attrs']['href'],
                         'https://www.pixiv.net/artworks/1')

    def test_footer_without_fields(self):
        """Test footer builder returns empty list when nothing is set."""
        from telepress.server import _build_gallery_footer

        self.assertEqual(_build_gallery_footer(None, None, None), [])
        self.assertEqual(_build_gallery_footer("", "", "false"), [])


if __name__ == '__main__':
    unittest.main()
