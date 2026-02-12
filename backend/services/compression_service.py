from PIL import Image
import io
import base64
import hashlib

class ImageCompressor:
    """Efficient image compression for screenshots"""

    def __init__(self, quality=60, max_width=1280, max_height=720):
        self.quality = quality
        self.max_width = max_width
        self.max_height = max_height

    def compress_base64(self, base64_str):
        """
        Compress base64 encoded image
        Returns: (compressed_base64, hash, size_kb)
        """
        try:
            # Decode base64
            img_data = base64.b64decode(base64_str)

            # Open image
            img = Image.open(io.BytesIO(img_data))

            # Convert RGBA to RGB if needed
            if img.mode == 'RGBA':
                img = img.convert('RGB')

            # Resize if too large
            if img.width > self.max_width or img.height > self.max_height:
                img.thumbnail((self.max_width, self.max_height), Image.Resampling.LANCZOS)

            # Compress to JPEG
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=self.quality, optimize=True)
            compressed_data = buffer.getvalue()

            # Calculate hash for deduplication
            img_hash = hashlib.sha256(compressed_data).hexdigest()

            # Encode to base64
            compressed_base64 = base64.b64encode(compressed_data).decode('utf-8')

            # Calculate size in KB
            size_kb = len(compressed_data) / 1024

            return compressed_base64, img_hash, size_kb

        except Exception as e:
            print(f"Compression error: {e}")
            return None, None, 0

    def batch_compress(self, base64_images):
        """Compress multiple images in parallel"""
        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(self.compress_base64, base64_images))

        return results

# Global compressor instance
compressor = ImageCompressor(quality=60, max_width=1280, max_height=720)
