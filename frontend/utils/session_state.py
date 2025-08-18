"""
Session state management for the Visual Document Analysis RAG System
"""

import streamlit as st
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import json

class SessionManager:
    """Manages application session state with proper initialization and cleanup"""
    
    def __init__(self):
        self.init_session_state()
    
    def init_session_state(self):
        """Initialize all session state variables with default values"""
        
        # Application state
        if "app_initialized" not in st.session_state:
            st.session_state.app_initialized = False
        
        if "current_page" not in st.session_state:
            st.session_state.current_page = "🏠 Home"
        
        if "theme" not in st.session_state:
            st.session_state.theme = "dark"
        
        # File management
        if "uploaded_files" not in st.session_state:
            st.session_state.uploaded_files = []
        
        if "pending_files" not in st.session_state:
            st.session_state.pending_files = []
        
        if "processing_queue" not in st.session_state:
            st.session_state.processing_queue = []
        
        # Processing status
        if "processing_status" not in st.session_state:
            st.session_state.processing_status = {}
        
        if "extracted_content" not in st.session_state:
            st.session_state.extracted_content = []
        
        if "processing_history" not in st.session_state:
            st.session_state.processing_history = []
        
        # Query and results
        if "query_history" not in st.session_state:
            st.session_state.query_history = []
        
        if "current_query" not in st.session_state:
            st.session_state.current_query = ""
        
        if "query_results" not in st.session_state:
            st.session_state.query_results = {}
        
        # UI state
            # Sidebar state removed - navigation now in header
        
        if "show_advanced_options" not in st.session_state:
            st.session_state.show_advanced_options = False
        
        if "selected_filters" not in st.session_state:
            st.session_state.selected_filters = {}
        
        # Performance and caching
        if "cache_timestamp" not in st.session_state:
            st.session_state.cache_timestamp = datetime.now().isoformat()
        
        if "last_activity" not in st.session_state:
            st.session_state.last_activity = datetime.now().isoformat()
        
        # Error handling
        if "error_log" not in st.session_state:
            st.session_state.error_log = []
        
        if "warning_log" not in st.session_state:
            st.session_state.warning_log = []
        
        # Analytics
        if "user_actions" not in st.session_state:
            st.session_state.user_actions = []
        
        if "session_start_time" not in st.session_state:
            st.session_state.session_start_time = datetime.now().isoformat()
        
        # First visit tracking
        if "first_visit" not in st.session_state:
            st.session_state.first_visit = True
        
        # Mark as initialized
        st.session_state.app_initialized = True
    
    def update_activity(self):
        """Update the last activity timestamp"""
        st.session_state.last_activity = datetime.now().isoformat()
    
    def add_file(self, file_data: Dict[str, Any]) -> str:
        """Add a file to the pending files list"""
        file_id = f"file_{len(st.session_state.pending_files)}_{datetime.now().timestamp()}"
        file_data["id"] = file_id
        file_data["uploaded_at"] = datetime.now().isoformat()
        file_data["status"] = "pending"
        
        st.session_state.pending_files.append(file_data)
        self.update_activity()
        return file_id
    
    def remove_file(self, file_id: str) -> bool:
        """Remove a file from the pending files list"""
        for i, file_data in enumerate(st.session_state.pending_files):
            if file_data.get("id") == file_id:
                st.session_state.pending_files.pop(i)
                self.update_activity()
                return True
        return False
    
    def update_file_status(self, file_id: str, status: str, progress: float = 0.0):
        """Update the status of a file"""
        for file_data in st.session_state.pending_files:
            if file_data.get("id") == file_id:
                file_data["status"] = status
                file_data["progress"] = progress
                file_data["updated_at"] = datetime.now().isoformat()
                break
        
        self.update_activity()
    
    def add_processing_result(self, file_id: str, result: Dict[str, Any]):
        """Add processing result for a file"""
        st.session_state.processing_status[file_id] = result
        st.session_state.processing_history.append({
            "file_id": file_id,
            "timestamp": datetime.now().isoformat(),
            "result": result
        })
        self.update_activity()
    
    def add_query(self, query: str, results: Optional[Dict[str, Any]] = None):
        """Add a query to the history"""
        query_entry = {
            "id": f"query_{len(st.session_state.query_history)}_{datetime.now().timestamp()}",
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "results": results
        }
        
        st.session_state.query_history.append(query_entry)
        st.session_state.current_query = query
        if results:
            st.session_state.query_results = results
        
        self.update_activity()
    
    def add_error(self, error_message: str, error_type: str = "error", details: Optional[Dict] = None):
        """Add an error to the error log"""
        error_entry = {
            "message": error_message,
            "type": error_type,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        
        st.session_state.error_log.append(error_entry)
        self.update_activity()
    
    def add_warning(self, warning_message: str, details: Optional[Dict] = None):
        """Add a warning to the warning log"""
        warning_entry = {
            "message": warning_message,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        
        st.session_state.warning_log.append(warning_entry)
        self.update_activity()
    
    def track_action(self, action: str, details: Optional[Dict] = None):
        """Track user actions for analytics"""
        action_entry = {
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "page": st.session_state.current_page,
            "details": details or {}
        }
        
        st.session_state.user_actions.append(action_entry)
        self.update_activity()
    
    def get_file_by_id(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get file data by ID"""
        for file_data in st.session_state.pending_files:
            if file_data.get("id") == file_id:
                return file_data
        return None
    
    def get_processing_status(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get processing status for a file"""
        return st.session_state.processing_status.get(file_id)
    
    def clear_processing_queue(self):
        """Clear the processing queue"""
        st.session_state.processing_queue.clear()
        self.update_activity()
    
    def clear_error_log(self):
        """Clear the error log"""
        st.session_state.error_log.clear()
        self.update_activity()
    
    def clear_warning_log(self):
        """Clear the warning log"""
        st.session_state.warning_log.clear()
        self.update_activity()
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        session_duration = datetime.now() - datetime.fromisoformat(st.session_state.session_start_time)
        
        return {
            "session_duration": str(session_duration),
            "total_files": len(st.session_state.pending_files),
            "processed_files": len(st.session_state.processing_status),
            "total_queries": len(st.session_state.query_history),
            "total_errors": len(st.session_state.error_log),
            "total_warnings": len(st.session_state.warning_log),
            "total_actions": len(st.session_state.user_actions),
            "last_activity": st.session_state.last_activity
        }
    
    def export_session_data(self) -> str:
        """Export session data as JSON"""
        export_data = {
            "session_info": self.get_session_stats(),
            "uploaded_files": st.session_state.uploaded_files,
            "processing_history": st.session_state.processing_history,
            "query_history": st.session_state.query_history,
            "error_log": st.session_state.error_log,
            "warning_log": st.session_state.warning_log,
            "user_actions": st.session_state.user_actions
        }
        
        return json.dumps(export_data, indent=2, default=str)
    
    def cleanup_old_data(self, max_age_hours: int = 24):
        """Clean up old data to prevent memory issues"""
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        
        # Clean up old processing history
        st.session_state.processing_history = [
            entry for entry in st.session_state.processing_history
            if datetime.fromisoformat(entry["timestamp"]).timestamp() > cutoff_time
        ]
        
        # Clean up old user actions (keep last 100)
        if len(st.session_state.user_actions) > 100:
            st.session_state.user_actions = st.session_state.user_actions[-100:]
        
        self.update_activity()
    
    def reset_session(self):
        """Reset the entire session (use with caution)"""
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        self.init_session_state()

# Global session manager instance
session_manager = SessionManager()

def get_session_manager() -> SessionManager:
    """Get the global session manager instance"""
    return session_manager
