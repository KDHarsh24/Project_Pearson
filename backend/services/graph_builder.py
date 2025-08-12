import json
from collections import defaultdict, Counter
from sqlalchemy.orm import Session
from db.models import Document, Chunk

# Very lightweight entity extraction based on enrichment metadata fields.
# For hackathon speed we leverage stored meta_json.

ENTITY_FIELDS = ["parties", "judges", "acts", "sections"]


def build_entity_graph_summary(db: Session, limit: int = 25):
    nodes = Counter()
    edges = Counter()
    q = db.query(Document).limit(500)
    for doc in q:
        try:
            meta = json.loads(doc.meta_json or '{}')
        except Exception:
            meta = {}
        entities = []
        for field in ENTITY_FIELDS:
            values = meta.get(field) or []
            # Normalize simple strings only
            for v in values[:50]:
                if isinstance(v, str) and 2 < len(v) < 120:
                    entities.append((field, v.strip()))
        # Count nodes
        for _, v in entities:
            nodes[v] += 1
        # Build co-occurrence edges (undirected)
        unique_vals = sorted(set(v for _, v in entities))
        for i in range(len(unique_vals)):
            for j in range(i+1, len(unique_vals)):
                a, b = unique_vals[i], unique_vals[j]
                edge_key = tuple(sorted([a, b]))
                edges[edge_key] += 1
    top_nodes = nodes.most_common(limit)
    top_edges = [ {"source": a, "target": b, "weight": w} for (a,b), w in edges.most_common(limit*3) ]
    return {
        "nodes": [ {"id": n, "count": c} for n, c in top_nodes ],
        "edges": top_edges,
        "entity_fields": ENTITY_FIELDS
    }
