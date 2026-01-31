#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
NEWTON MISSION CONTROL TESTS
Tests for the Mission Control dashboard home page.

This test verifies that:
1. Mission Control files exist
2. The home page endpoint will serve Mission Control
═══════════════════════════════════════════════════════════════════════════════
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from pathlib import Path


class TestMissionControlSetup:
    """Tests for Mission Control static files and configuration."""

    def test_mission_control_directory_exists(self):
        """Test that the mission-control directory exists."""
        root_dir = Path(__file__).parent.parent
        mission_control_dir = root_dir / "mission-control"
        assert mission_control_dir.exists(), "mission-control directory should exist"
        assert mission_control_dir.is_dir(), "mission-control should be a directory"

    def test_mission_control_index_html_exists(self):
        """Test that mission-control/index.html exists."""
        root_dir = Path(__file__).parent.parent
        index_file = root_dir / "mission-control" / "index.html"
        assert index_file.exists(), "mission-control/index.html should exist"
        
        # Verify it contains expected content
        content = index_file.read_text()
        assert "Newton Mission Control" in content, "index.html should contain 'Newton Mission Control'"

    def test_mission_control_styles_exists(self):
        """Test that mission-control/styles.css exists."""
        root_dir = Path(__file__).parent.parent
        styles_file = root_dir / "mission-control" / "styles.css"
        assert styles_file.exists(), "mission-control/styles.css should exist"
        
        # Verify it contains CSS
        content = styles_file.read_text()
        assert "color" in content.lower() or "font" in content.lower(), "styles.css should contain CSS"

    def test_mission_control_app_js_exists(self):
        """Test that mission-control/app.js exists."""
        root_dir = Path(__file__).parent.parent
        app_js_file = root_dir / "mission-control" / "app.js"
        assert app_js_file.exists(), "mission-control/app.js should exist"
        
        # Verify it contains JavaScript
        content = app_js_file.read_text()
        assert "function" in content or "const" in content, "app.js should contain JavaScript"

    def test_mission_control_config_js_exists(self):
        """Test that mission-control/config.js exists."""
        root_dir = Path(__file__).parent.parent
        config_file = root_dir / "mission-control" / "config.js"
        assert config_file.exists(), "mission-control/config.js should exist"
        
        # Verify it contains the endpoint configuration
        content = config_file.read_text()
        assert "ENDPOINTS" in content, "config.js should contain ENDPOINTS configuration"

    def test_mission_control_dir_constant_defined(self):
        """Test that MISSION_CONTROL_DIR is defined in newton_supercomputer."""
        from newton_supercomputer import MISSION_CONTROL_DIR
        assert MISSION_CONTROL_DIR is not None, "MISSION_CONTROL_DIR should be defined"
        assert MISSION_CONTROL_DIR.exists(), "MISSION_CONTROL_DIR should point to existing directory"

    def test_home_page_serves_mission_control(self):
        """Test that the serve_home function returns Mission Control content."""
        import asyncio
        from newton_supercomputer import serve_home
        
        # Call the async function using asyncio.run()
        response = asyncio.run(serve_home())
        
        # Check response content
        assert response.status_code == 200, "Home page should return 200"
        assert "Newton Mission Control" in response.body.decode(), \
            "Home page should contain 'Newton Mission Control'"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
