"""
LoveAdvisor V4 - Analysis Record Store Service (Local File Storage)
Phase 3: User Behavior Tracking & Data Loop - MTU-158

This module provides a minimal file-based persistence for AnalysisRecord objects.
It implements the contract for saving analysis records to a local JSON Lines file.

Implementation: Local JSON Lines file storage (append-only).
- No database connection
- Simple file-based storage
- UTF-8 encoding, time fields serialized to ISO format
- Minimal exception protection (failures logged but don't crash process)

Storage location: data/analysis_records.jsonl (relative to project root)
"""

import json
import os
from pathlib import Path
from typing import Optional
from app.schemas.analysis_record_models import AnalysisRecord
from app.schemas.request_models import AnalysisRequest
from app.schemas.result_models import AnalysisResult

# Configuration constants
PROJECT_ROOT = Path(__file__).parent.parent.parent  # app/services -> app -> project root
STORAGE_DIR = PROJECT_ROOT / "data"
STORAGE_FILE = STORAGE_DIR / "analysis_records.jsonl"


class AnalysisRecordStore:
    """
    Minimal file-based persistence for AnalysisRecord objects.

    This class implements the contract for saving analysis records to a local
    JSON Lines file (append-only). Each record is written as a JSON object on
    a separate line.

    Current implementation: Local JSON Lines file storage
    """

    @staticmethod
    def save_record(record: AnalysisRecord) -> None:
        """
        Save an analysis record to local JSON Lines file.

        This method appends the record as a JSON object to the storage file.
        The file is created if it doesn't exist. The directory is created if needed.
        Uses UTF-8 encoding and ensures datetime fields are serialized properly.

        Args:
            record: AnalysisRecord instance to save

        Returns:
            None

        Note:
            - Minimal exception protection: logs errors but doesn't crash
            - Uses append mode ("a") to add new records
            - Each record is written as a JSON line (ending with newline)
        """
        try:
            # Ensure storage directory exists
            STORAGE_DIR.mkdir(exist_ok=True)

            # Convert record to JSON string (Pydantic applies json_encoders for datetime)
            record_json = record.json(ensure_ascii=False)

            # Write as JSON line (single line JSON object with newline)
            with open(STORAGE_FILE, "a", encoding="utf-8") as f:
                f.write(record_json)
                f.write("\n")  # Newline delimiter for JSON Lines format

        except Exception as e:
            # Minimal exception protection: log but don't crash
            # In production, you might want to use proper logging
            print(f"[AnalysisRecordStore] Failed to save record: {e}")
            # Optionally re-raise if you want caller to handle, but per requirements:
            # "单条失败不影响进程崩溃" - single failure shouldn't crash process
            # So we just swallow the exception after logging

    @classmethod
    def save_record_from_request_and_result(
        cls,
        request: AnalysisRequest,
        result: AnalysisResult,
        request_id: Optional[str] = None
    ) -> None:
        """
        Convenience method: build and save a record from request and result.

        This method combines record building with the save operation,
        providing a higher-level API for common usage patterns.

        Args:
            request: AnalysisRequest instance
            result: AnalysisResult instance
            request_id: Optional request ID override

        Returns:
            None
        """
        record = AnalysisRecord.from_request_and_result(
            request=request,
            result=result,
            request_id=request_id
        )
        cls.save_record(record)

    @staticmethod
    def read_latest_records(limit: int = 10) -> list[AnalysisRecord]:
        """
        Read the latest analysis records from the local JSON Lines file.

        This method reads the storage file, parses each line as an AnalysisRecord,
        and returns the most recent records (by file order, assuming append-only).

        Args:
            limit: Maximum number of records to return (default 10)

        Returns:
            List of AnalysisRecord instances, ordered from oldest to newest.
            Returns empty list if file doesn't exist, is empty, or parsing fails.

        Note:
            - Minimal exception protection: returns empty list on any error
            - File is read from beginning to end; recent records are at the end
            - Each line must be valid JSON that can be parsed as AnalysisRecord
        """
        try:
            # Check if file exists
            if not STORAGE_FILE.exists():
                return []

            records = []
            with open(STORAGE_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:  # Skip empty lines
                        continue
                    try:
                        # Parse JSON line and create AnalysisRecord
                        record_dict = json.loads(line)
                        record = AnalysisRecord(**record_dict)
                        records.append(record)
                    except (json.JSONDecodeError, Exception) as e:
                        # Skip malformed lines but continue processing others
                        print(f"[AnalysisRecordStore] Failed to parse line: {e}")
                        continue

            # Return the most recent `limit` records (last N entries)
            return records[-limit:] if records else []
        except Exception as e:
            # Catch any unexpected errors and return empty list
            print(f"[AnalysisRecordStore] Failed to read records: {e}")
            return []


# Convenience function for direct usage
def save_analysis_record(record: AnalysisRecord) -> None:
    """
    Convenience function for saving analysis records.

    This is a thin wrapper around AnalysisRecordStore.save_record() for
    simpler import and usage in API endpoints.

    Args:
        record: AnalysisRecord instance to save

    Returns:
        None
    """
    AnalysisRecordStore.save_record(record)