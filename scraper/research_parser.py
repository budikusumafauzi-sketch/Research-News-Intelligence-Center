import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# arXiv Atom feed namespace
ARXIV_NS = {
    'atom': 'http://www.w3.org/2005/Atom',
    'arxiv': 'http://arxiv.org/schemas/atom'
}

# Target research categories
ARXIV_CATEGORIES = ['cs.AI', 'cs.LG', 'cs.CL', 'cs.CV', 'cs.CR', 'stat.ML']

class ResearchParser:

    @staticmethod
    def fetch_arxiv(max_results=50):
        """
        Fetches recent papers from arXiv across all target categories
        using the public Atom API. Returns normalized paper dictionaries.

        Architectural decision: Uses urllib (stdlib) instead of adding
        a new dependency. arXiv returns Atom XML which is parsed via
        ElementTree — no third-party XML library required.
        """
        papers = []

        for category in ARXIV_CATEGORIES:
            params = urllib.parse.urlencode({
                'search_query': f'cat:{category}',
                'start': 0,
                'max_results': max_results,
                'sortBy': 'submittedDate',
                'sortOrder': 'descending'
            })
            url = f'http://export.arxiv.org/api/query?{params}'

            try:
                with urllib.request.urlopen(url, timeout=15) as response:
                    raw_xml = response.read()
            except Exception as e:
                logger.warning(f"arXiv request failed for category {category}: {e}")
                continue

            try:
                root = ET.fromstring(raw_xml)
            except ET.ParseError as e:
                logger.warning(f"arXiv XML parse error for category {category}: {e}")
                continue

            entries = root.findall('atom:entry', ARXIV_NS)
            for entry in entries:
                paper = ResearchParser._normalize_arxiv_entry(entry)
                if paper:
                    papers.append(paper)

            logger.info(f"arXiv: fetched {len(entries)} entries for category {category}.")

        return papers

    @staticmethod
    def _normalize_arxiv_entry(entry):
        """
        Converts a single arXiv Atom <entry> element into the
        standardized paper dictionary consumed by ResearchService.
        Returns None if required fields are missing.
        """
        try:
            title_el = entry.find('atom:title', ARXIV_NS)
            abstract_el = entry.find('atom:summary', ARXIV_NS)
            published_el = entry.find('atom:published', ARXIV_NS)

            title = title_el.text.strip().replace('\n', ' ') if title_el is not None else None
            abstract = abstract_el.text.strip().replace('\n', ' ') if abstract_el is not None else None

            if not title or not abstract:
                return None

            # Collect author names into a comma-separated string
            author_els = entry.findall('atom:author/atom:name', ARXIV_NS)
            authors = ', '.join(a.text.strip() for a in author_els if a.text)

            # Extract DOI from the arxiv:doi element (optional)
            doi_el = entry.find('arxiv:doi', ARXIV_NS)
            doi = doi_el.text.strip() if doi_el is not None and doi_el.text else None

            # Parse ISO 8601 publication date
            published_at = datetime.utcnow()
            if published_el is not None and published_el.text:
                try:
                    published_at = datetime.strptime(
                        published_el.text.strip()[:19], '%Y-%m-%dT%H:%M:%S'
                    )
                except ValueError:
                    pass

            return {
                'title': title,
                'abstract': abstract,
                'authors': authors or 'Unknown',
                'doi': doi,
                'published_at': published_at,
                'source_name': 'arXiv'
            }
        except Exception as e:
            logger.warning(f"Failed to normalize arXiv entry: {e}")
            return None
