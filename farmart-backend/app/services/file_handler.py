class FileHandler:
    """
    Handles file uploads (images, documents).
    Placeholder implementation so backend runs.
    """

    def upload(self, file):
        return {
            "status": "success",
            "url": "https://example.com/dummy-file.jpg"
        }

    def delete(self, file_url):
        return {
            "status": "success",
            "deleted": True
        }


# Singleton instance
file_handler = FileHandler()
