"""
UI Helper utilities for the Visual Document Analysis RAG System
"""

import streamlit as st
from typing import Dict, List, Any, Optional, Callable
from config.settings import theme_config, ui_config

def create_card(title: str, content: str, icon: str = "📄", subtitle: str = "", 
                actions: Optional[List[Dict[str, Any]]] = None) -> str:
    """Create a modern card component"""
    
    actions_html = ""
    if actions:
        actions_html = '<div class="card-actions">'
        for action in actions:
            # Use Streamlit-native st.button for interactivity in the main app, not HTML onclick
            actions_html += f'<button class="btn btn-{action.get("type", "secondary")}">{action["label"]}</button>'
        actions_html += '</div>'
    
    return f"""
    <div class="card">
        <div class="card-header">
            <div class="card-icon">{icon}</div>
            <div>
                <h3 class="card-title">{title}</h3>
                {f'<p class="card-subtitle">{subtitle}</p>' if subtitle else ''}
            </div>
        </div>
        <div class="card-content">
            {content}
        </div>
        {actions_html}
    </div>
    """

def create_metric_card(value: Any, label: str, icon: str, color: str = "primary") -> str:
    """Create a metric card component"""
    return f"""
    <div class="metric-card">
        <div class="metric-icon" style="background: {color};">{icon}</div>
        <div class="metric-content">
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
    </div>
    """

def create_status_badge(status: str, text: str) -> str:
    """Create a status badge component"""
    status_colors = {
        "success": "var(--success-500)",
        "warning": "var(--warning-500)",
        "error": "var(--error-500)",
        "info": "var(--primary-500)"
    }
    
    color = status_colors.get(status, "var(--text-muted)")
    return f'<span class="status-badge" style="background: {color}; color: white;">{text}</span>'

def create_progress_bar(progress: float, text: str = "", height: str = "8px") -> str:
    """Create a custom progress bar component"""
    return f"""
    <div class="progress-container">
        <div class="progress-bar" style="width: {progress}%; height: {height};"></div>
        {f'<div class="progress-text">{text}</div>' if text else ''}
    </div>
    """

def create_tabs(tab_names: List[str], active_tab: int = 0) -> str:
    """Create custom tab navigation"""
    tabs_html = '<div class="tabs-container">'
    tabs_html += '<div class="tabs-header">'
    
    for i, name in enumerate(tab_names):
        active_class = "active" if i == active_tab else ""
        tabs_html += f'<button class="tab-button {active_class}">{name}</button>'
    
    tabs_html += '</div></div>'
    return tabs_html

def create_upload_zone(drop_text: str = "Drag & drop files here", 
                      hint_text: str = "or click to browse", 
                      supported_formats: Optional[List[str]] = None) -> str:
    """Create a modern file upload zone"""
    
    formats_html = ""
    if supported_formats:
        formats_html = '<div class="upload-badges">'
        for fmt in supported_formats:
            formats_html += f'<span class="badge">{fmt.upper()}</span>'
        formats_html += '</div>'
    
    return f"""
    <div class="upload-area" id="upload-zone">
        <div class="upload-icon">📁</div>
        <div class="upload-text">{drop_text}</div>
        <div class="upload-hint">{hint_text}</div>
        {formats_html}
    </div>
    """

def create_chat_message(role: str, content: str, timestamp: str = "", 
                       avatar: str = "", metadata: Optional[Dict] = None) -> str:
    """Create a chat message component"""
    
    role_class = "user" if role == "user" else "assistant"
    avatar_content = avatar if avatar else ("👤" if role == "user" else "🤖")
    
    metadata_html = ""
    if metadata:
        metadata_html = '<div class="message-metadata">'
        for key, value in metadata.items():
            metadata_html += f'<span class="meta-item">{key}: {value}</span>'
        metadata_html += '</div>'
    
    return f"""
    <div class="message {role_class}">
        <div class="message-avatar">{avatar_content}</div>
        <div class="message-content">
            <div class="message-text">{content}</div>
            {f'<div class="message-time">{timestamp}</div>' if timestamp else ''}
            {metadata_html}
        </div>
    </div>
    """

def create_filter_panel(filters: List[Dict[str, Any]]) -> str:
    """Create a filter panel component"""
    filters_html = '<div class="filter-panel">'
    
    for filter_item in filters:
        filter_type = filter_item.get("type", "text")
        label = filter_item.get("label", "")
        placeholder = filter_item.get("placeholder", "")
        
        if filter_type == "select":
            options = filter_item.get("options", [])
            options_html = "".join([f'<option value="{opt}">{opt}</option>' for opt in options])
            filters_html += f"""
            <div class="filter-item">
                <label>{label}</label>
                <select class="filter-select">{options_html}</select>
            </div>
            """
        elif filter_type == "slider":
            min_val = filter_item.get("min", 0)
            max_val = filter_item.get("max", 100)
            default_val = filter_item.get("default", min_val)
            filters_html += f"""
            <div class="filter-item">
                <label>{label}</label>
                <input type="range" min="{min_val}" max="{max_val}" value="{default_val}" class="filter-slider">
            </div>
            """
        else:  # text input
            filters_html += f"""
            <div class="filter-item">
                <label>{label}</label>
                <input type="text" placeholder="{placeholder}" class="filter-input">
            </div>
            """
    
    filters_html += '</div>'
    return filters_html

def create_data_table(data: List[Dict[str, Any]], columns: Optional[List[str]] = None, 
                     sortable: bool = True, searchable: bool = True) -> str:
    """Create a custom data table component"""
    
    if not data:
        return '<div class="empty-table">No data available</div>'
    
    if not columns:
        columns = list(data[0].keys()) if data else []
    
    table_html = '<div class="data-table">'
    
    # Search bar
    if searchable:
        table_html += '<div class="table-search"><input type="text" placeholder="Search..." class="search-input"></div>'
    
    # Table header
    table_html += '<div class="table-header">'
    for col in columns:
        sort_class = "sortable" if sortable else ""
        table_html += f'<div class="table-cell header {sort_class}">{col}</div>'
    table_html += '</div>'
    
    # Table body
    table_html += '<div class="table-body">'
    for row in data:
        table_html += '<div class="table-row">'
        for col in columns:
            value = row.get(col, "")
            table_html += f'<div class="table-cell">{value}</div>'
        table_html += '</div>'
    table_html += '</div>'
    
    table_html += '</div>'
    return table_html

def create_loading_spinner(text: str = "Loading...", size: str = "medium") -> str:
    """Create a loading spinner component"""
    size_class = f"spinner-{size}"
    return f"""
    <div class="loading-container">
        <div class="spinner {size_class}"></div>
        <div class="loading-text">{text}</div>
    </div>
    """

def create_error_message(message: str, details: Optional[str] = None, 
                       retry_action: Optional[str] = None) -> str:
    """Create an error message component"""
    
    details_html = f'<div class="error-details">{details}</div>' if details else ""
    retry_html = f'<button class="btn btn-primary retry-btn" onclick="{retry_action}">Retry</button>' if retry_action else ""
    
    return f"""
    <div class="error-message">
        <div class="error-icon">❌</div>
        <div class="error-content">
            <div class="error-text">{message}</div>
            {details_html}
            {retry_html}
        </div>
    </div>
    """

def create_success_message(message: str, details: Optional[str] = None) -> str:
    """Create a success message component"""
    
    details_html = f'<div class="success-details">{details}</div>' if details else ""
    
    return f"""
    <div class="success-message">
        <div class="success-icon">✅</div>
        <div class="success-content">
            <div class="success-text">{message}</div>
            {details_html}
        </div>
    </div>
    """

def create_breadcrumb(items: List[Dict[str, str]]) -> str:
    """Create a breadcrumb navigation component"""
    breadcrumb_html = '<div class="breadcrumb">'
    
    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        separator = " > " if not is_last else ""
        
        if is_last:
            breadcrumb_html += f'<span class="breadcrumb-item current">{item["label"]}</span>'
        else:
            breadcrumb_html += f'<a href="#" class="breadcrumb-item">{item["label"]}</a>'
        
        breadcrumb_html += separator
    
    breadcrumb_html += '</div>'
    return breadcrumb_html

def create_tooltip(text: str, tooltip_text: str) -> str:
    """Create a tooltip component"""
    return f"""
    <div class="tooltip-container">
        <span class="tooltip-trigger">{text}</span>
        <div class="tooltip-content">{tooltip_text}</div>
    </div>
    """

def create_modal(title: str, content: str, actions: List[Dict[str, Any]], 
                modal_id: str = "modal") -> str:
    """Create a modal component"""
    
    actions_html = ""
    for action in actions:
        action_type = action.get("type", "secondary")
        action_class = f"btn btn-{action_type}"
        # Use Streamlit-native st.button for interactivity in the main app, not HTML onclick
        actions_html += f'<button class="{action_class}">{action["label"]}</button>'
    
    return f"""
    <div class="modal" id="{modal_id}">
        <div class="modal-content">
            <div class="modal-header">
                <h3>{title}</h3>
                <button class="modal-close">&times;</button>
            </div>
            <div class="modal-body">
                {content}
            </div>
            <div class="modal-footer">
                {actions_html}
            </div>
        </div>
    </div>
    """

def create_notification(message: str, notification_type: str = "info", 
                       duration: int = 5000) -> str:
    """Create a notification component"""
    
    type_icons = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌"
    }
    
    icon = type_icons.get(notification_type, "ℹ️")
    
    return f"""
    <div class="notification notification-{notification_type}" data-duration="{duration}">
        <div class="notification-icon">{icon}</div>
        <div class="notification-content">{message}</div>
        <button class="notification-close">&times;</button>
    </div>
    """
