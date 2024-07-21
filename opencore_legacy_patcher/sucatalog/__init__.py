"""
sucatalog: Python module for querying Apple's Software Update Catalog, supporting Tiger through Sequoia.

-------------------

## Usage

### Get Software Update Catalog URL

```python
>>> import sucatalog

>>> # Defaults to PublicRelease seed
>>> url = sucatalog.CatalogURL().url
"https://swscan.apple.com/.../index-15-14-13-12-10.16-10.15-10.14-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog"

>>> url = sucatalog.CatalogURL(seed=sucatalog.SeedType.DeveloperSeed).url
"https://swscan.apple.com/.../index-15seed-15-14-13-12-10.16-10.15-10.14-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog"

>>> url = sucatalog.CatalogURL(version=sucatalog.CatalogVersion.HIGH_SIERRA).url
"https://swscan.apple.com/.../index-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog"
```


### Parse Software Update Catalog - InstallAssistants only

>>> import sucatalog

>>> # Pass contents of URL (as dictionary)
>>> catalog = plistlib.loads(requests.get(url).content)

>>> products = sucatalog.CatalogProducts(catalog).products
[
    {
        'Build': '22G720',
        'Catalog': <SeedType.PublicRelease: ''>,
        'InstallAssistant': {
            'IntegrityDataSize': 42008,
            'IntegrityDataURL': 'https://swcdn.apple.com/.../InstallAssistant.pkg.integrityDataV1',
            'Size': 12210304673,
            'URL': 'https://swcdn.apple.com/.../InstallAssistant.pkg'
        },
        'PostDate': datetime.datetime(2024, 5, 20, 17, 18, 21),
        'ProductID': '052-96247',
        'Title': 'macOS Ventura',
        'Version': '13.6.7'
    }
]

### Parse Software Update Catalog - All products

By default, `CatalogProducts` will only return InstallAssistants. To get all products, set `install_assistants_only=False`.

>>> import sucatalog

>>> # Pass contents of URL (as dictionary)
>>> products = sucatalog.CatalogProducts(catalog, install_assistants_only=False).products
[
    {
        'Build': None,
        'Catalog': None,
        'Packages': [
            {
                'MetadataURL': 'https://swdist.apple.com/.../iLifeSlideshow_v2.pkm',
                'Size': 116656956,
                'URL': 'http://swcdn.apple.com/.../iLifeSlideshow_v2.pkg'
            },
            {
                'MetadataURL': 'https://swdist.apple.com/.../iPhoto9.2.3ContentUpdate.pkm',
                'Size': 59623907,
                'URL': 'http://swcdn.apple.com/.../iPhoto9.2.3ContentUpdate.pkg'
            },
            {
                'MetadataURL': 'https://swdist.apple.com/.../iPhoto9.2.3Update.pkm',
                'Size': 197263405,
                'URL': 'http://swcdn.apple.com/.../iPhoto9.2.3Update.pkg'
            }
        ],
        'PostDate': datetime.datetime(2019, 10, 23, 0, 2, 42),
        'ProductID': '041-85230',
        'Title': 'iPhoto Update',
        'Version': '9.2.3'
    },
    {
        'Build': None,
        'Catalog': None,
        'Packages': [
            {
                'Digest': '9aba109078feec7ea841529e955440b63d7755a0',
                'MetadataURL': 'https://swdist.apple.com/.../iPhoto9.4.3Update.pkm',
                'Size': 555246460,
                'URL': 'http://swcdn.apple.com/.../iPhoto9.4.3Update.pkg'
            },
            {
                'Digest': '0bb013221ca2df5e178d950cb229f41b8e680d00',
                'MetadataURL': 'https://swdist.apple.com/.../iPhoto9.4.3ContentUpdate.pkm',
                'Size': 213073666,
                'URL': 'http://swcdn.apple.com/.../iPhoto9.4.3ContentUpdate.pkg'
            }
        ],
        'PostDate': datetime.datetime(2019, 10, 13, 3, 23, 14),
        'ProductID': '041-88859',
        'Title': 'iPhoto Update',
        'Version': '9.4.3'
    }
]
"""

from .url       import CatalogURL
from .constants import CatalogVersion, SeedType
from .products  import CatalogProducts