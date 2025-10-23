"""Unit tests for session management."""

import json

from mealie_parser.models.session_state import SessionState
from mealie_parser.session_manager import SessionManager


class TestSessionState:
    """Tests for SessionState dataclass."""

    def test_create_default_session(self):
        """Test creating session with defaults."""
        state = SessionState()
        assert state.session_id
        assert state.created_at
        assert state.mode == "batch"
        assert state.processed_patterns == []
        assert state.skipped_patterns == []

    def test_to_dict_serialization(self):
        """Test session state serialization."""
        state = SessionState(mode="batch")
        state.add_processed_pattern("tsp")
        state.add_skipped_pattern("cup")

        data = state.to_dict()
        assert data["mode"] == "batch"
        assert "tsp" in data["processed_patterns"]
        assert "cup" in data["skipped_patterns"]
        assert "session_id" in data
        assert "created_at" in data

    def test_from_dict_deserialization(self):
        """Test session state deserialization."""
        data = {
            "session_id": "test-123",
            "created_at": "2025-01-01T00:00:00",
            "last_updated": "2025-01-01T01:00:00",
            "mode": "batch",
            "processed_patterns": ["tsp", "tbsp"],
            "skipped_patterns": ["cup"],
            "created_units": {"tsp": "unit-123"},
            "created_foods": {},
            "current_operation": None,
        }

        state = SessionState.from_dict(data)
        assert state.session_id == "test-123"
        assert state.mode == "batch"
        assert len(state.processed_patterns) == 2
        assert "tsp" in state.processed_patterns

    def test_round_trip_serialization(self):
        """Test serialization and deserialization roundtrip."""
        original = SessionState(mode="batch")
        original.add_processed_pattern("tsp")
        original.add_created_unit("tsp", "unit-456")

        data = original.to_dict()
        restored = SessionState.from_dict(data)

        assert restored.session_id == original.session_id
        assert restored.mode == original.mode
        assert restored.processed_patterns == original.processed_patterns
        assert restored.created_units == original.created_units

    def test_add_processed_pattern(self):
        """Test adding processed pattern."""
        state = SessionState()
        initial_time = state.last_updated

        state.add_processed_pattern("tsp")

        assert "tsp" in state.processed_patterns
        assert len(state.processed_patterns) == 1
        assert state.last_updated > initial_time

    def test_add_processed_pattern_no_duplicates(self):
        """Test adding same pattern twice doesn't create duplicates."""
        state = SessionState()
        state.add_processed_pattern("tsp")
        state.add_processed_pattern("tsp")

        assert len(state.processed_patterns) == 1

    def test_add_skipped_pattern(self):
        """Test adding skipped pattern."""
        state = SessionState()
        state.add_skipped_pattern("cup")

        assert "cup" in state.skipped_patterns
        assert len(state.skipped_patterns) == 1

    def test_add_created_unit(self):
        """Test recording created unit."""
        state = SessionState()
        state.add_created_unit("tsp", "unit-123")

        assert state.created_units["tsp"] == "unit-123"

    def test_add_created_food(self):
        """Test recording created food."""
        state = SessionState()
        state.add_created_food("chicken", "food-456")

        assert state.created_foods["chicken"] == "food-456"

    def test_total_processed_property(self):
        """Test total_processed calculated correctly."""
        state = SessionState()
        state.add_processed_pattern("tsp")
        state.add_processed_pattern("tbsp")
        state.add_skipped_pattern("cup")

        assert state.total_processed == 3

    def test_summary_property(self):
        """Test summary string generation."""
        state = SessionState()
        state.add_processed_pattern("tsp")
        state.add_skipped_pattern("cup")
        state.add_created_unit("tsp", "unit-123")

        summary = state.summary
        assert "1 processed" in summary
        assert "1 skipped" in summary
        assert "1 units created" in summary


class TestSessionManager:
    """Tests for SessionManager."""

    def test_save_and_load_session(self, tmp_path, monkeypatch):
        """Test saving and loading session."""
        # Use temporary directory
        temp_session_file = tmp_path / "session-state.json"
        monkeypatch.setattr("mealie_parser.session_manager.SESSION_FILE", temp_session_file)
        monkeypatch.setattr("mealie_parser.session_manager.SESSION_DIR", tmp_path)

        # Create and save session
        original = SessionState(mode="batch")
        original.add_processed_pattern("tsp")
        original.add_created_unit("tsp", "unit-123")

        SessionManager.save_session(original)
        assert temp_session_file.exists()

        # Load session
        loaded = SessionManager.load_session()
        assert loaded is not None
        assert loaded.mode == "batch"
        assert "tsp" in loaded.processed_patterns
        assert loaded.created_units["tsp"] == "unit-123"

    def test_load_nonexistent_session(self, tmp_path, monkeypatch):
        """Test loading when no session file exists."""
        temp_session_file = tmp_path / "nonexistent.json"
        monkeypatch.setattr("mealie_parser.session_manager.SESSION_FILE", temp_session_file)

        loaded = SessionManager.load_session()
        assert loaded is None

    def test_load_corrupted_session(self, tmp_path, monkeypatch):
        """Test loading corrupted JSON file."""
        temp_session_file = tmp_path / "corrupted.json"
        monkeypatch.setattr("mealie_parser.session_manager.SESSION_FILE", temp_session_file)
        monkeypatch.setattr("mealie_parser.session_manager.SESSION_DIR", tmp_path)

        # Write invalid JSON
        with temp_session_file.open("w") as f:
            f.write("{invalid json")

        loaded = SessionManager.load_session()
        assert loaded is None

    def test_clear_session(self, tmp_path, monkeypatch):
        """Test clearing session file."""
        temp_session_file = tmp_path / "session.json"
        monkeypatch.setattr("mealie_parser.session_manager.SESSION_FILE", temp_session_file)
        monkeypatch.setattr("mealie_parser.session_manager.SESSION_DIR", tmp_path)

        # Create session file
        state = SessionState()
        SessionManager.save_session(state)
        assert temp_session_file.exists()

        # Clear session
        SessionManager.clear_session()
        assert not temp_session_file.exists()

    def test_clear_nonexistent_session(self, tmp_path, monkeypatch):
        """Test clearing when no session exists."""
        temp_session_file = tmp_path / "nonexistent.json"
        monkeypatch.setattr("mealie_parser.session_manager.SESSION_FILE", temp_session_file)

        # Should not raise error
        SessionManager.clear_session()

    def test_session_exists_true(self, tmp_path, monkeypatch):
        """Test session_exists returns True when file exists."""
        temp_session_file = tmp_path / "session.json"
        monkeypatch.setattr("mealie_parser.session_manager.SESSION_FILE", temp_session_file)
        monkeypatch.setattr("mealie_parser.session_manager.SESSION_DIR", tmp_path)

        state = SessionState()
        SessionManager.save_session(state)

        assert SessionManager.session_exists() is True

    def test_session_exists_false(self, tmp_path, monkeypatch):
        """Test session_exists returns False when no file."""
        temp_session_file = tmp_path / "nonexistent.json"
        monkeypatch.setattr("mealie_parser.session_manager.SESSION_FILE", temp_session_file)

        assert SessionManager.session_exists() is False

    def test_atomic_write(self, tmp_path, monkeypatch):
        """Test atomic write prevents partial writes."""
        temp_session_file = tmp_path / "session.json"
        monkeypatch.setattr("mealie_parser.session_manager.SESSION_FILE", temp_session_file)
        monkeypatch.setattr("mealie_parser.session_manager.SESSION_DIR", tmp_path)

        state = SessionState(mode="batch")
        SessionManager.save_session(state)

        # Verify temp file doesn't exist after save
        temp_file = temp_session_file.with_suffix(".tmp")
        assert not temp_file.exists()

        # Verify main file exists and is valid JSON
        assert temp_session_file.exists()
        with temp_session_file.open() as f:
            data = json.load(f)
        assert data["mode"] == "batch"

    def test_ensure_session_dir_creates_directory(self, tmp_path, monkeypatch):
        """Test ensure_session_dir creates directory if missing."""
        session_dir = tmp_path / "new_dir"
        monkeypatch.setattr("mealie_parser.session_manager.SESSION_DIR", session_dir)

        assert not session_dir.exists()
        SessionManager.ensure_session_dir()
        assert session_dir.exists()
