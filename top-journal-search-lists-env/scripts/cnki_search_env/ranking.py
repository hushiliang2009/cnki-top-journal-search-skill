from __future__ import annotations

from copy import deepcopy
from collections.abc import Iterable
from pathlib import Path

from .catalog_adapter import DEFAULT_CATALOG, lookup_journals
from .models import PaperRecord
from .professional import TOPIC_FIELD_PRIORITY


def annotate_and_sort_records(
    records: Iterable[PaperRecord], *, catalog: Path = DEFAULT_CATALOG,
) -> list[PaperRecord]:
    materialized = list(records)
    matches = lookup_journals(catalog, [item.journal_raw for item in materialized])
    for record, match in zip(materialized, matches, strict=True):
        record.journal_matched_title = match["matched_title"]
        record.journal_match_status = match["status"]
        record.journal_match_method = match["match_method"]
        record.priority_level = match["priority_level"]
        record.priority_group = match["priority_group"]
        record.environment_subfields = list(match["environment_subfields"])
        record.source_catalogs = list(match["source_catalogs"])
        record.subject_categories = list(match["subject_categories"])
        record.formal_evidence = list(match["formal_evidence"])
        record.index_memberships = list(match["index_memberships"])
        record.ncs_internal_rank = match["ncs_internal_rank"]
        record.journal_id = match["journal_id"]
        record.aliases = list(match["aliases"])
        record.index_subject_categories = deepcopy(match["index_subject_categories"])
        record.source_memberships = deepcopy(match["source_memberships"])
        record.catalog_version = match["catalog_version"]
        record.catalog_date = match["catalog_date"]
        record.revision_date = match["revision_date"]
        record.manual_review_required = bool(match["manual_review_required"])
    field_rank = {
        field: index
        for index, field in enumerate(TOPIC_FIELD_PRIORITY, start=1)
    }
    return sorted(
        materialized,
        key=lambda item: (
            item.priority_level is None,
            item.priority_level or 999,
            item.ncs_internal_rank or 999,
            field_rank.get(item.topic_match_field or "", 999),
            item.result_rank,
        ),
    )
