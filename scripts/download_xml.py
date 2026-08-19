import ssl
import urllib.request
from pathlib import Path

ssl_context = ssl._create_unverified_context()

url = "https://www.six-group.com/dam/download/financial-information/data-center/iso-currrency/lists/list-one.xml"
current_dir = Path(__file__).parent
output_path = current_dir / "list-one.xml"


def download_xml():
    print(f"Downloading ISO 4217 XML from {url}...")

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=ssl_context) as response:
        with open(output_path, "wb") as file:
            file.write(response.read())

    print(f"Success! Saved to {output_path}")


if __name__ == "__main__":
    download_xml()
