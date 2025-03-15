"""
Oracle APEX Tools
This module provides tools for creating and manipulating Oracle APEX applications.
"""

from typing import List, Dict, Any
from langchain.tools import StructuredTool
from langchain_core.pydantic_v1 import BaseModel, Field

# Define tool schemas

class CreateAPEXAppInput(BaseModel):
    """Input schema for creating an APEX application."""
    app_name: str = Field(..., description="Name of the APEX application")
    app_alias: str = Field(..., description="Alias for the APEX application (used in URLs)")
    schema_name: str = Field(..., description="Database schema to use for the application")
    auth_scheme: str = Field("APEX_ACCESS_CONTROL", description="Authentication scheme to use")
    pages: List[Dict[str, Any]] = Field([], description="List of pages to create initially")

class CreateAPEXPageInput(BaseModel):
    """Input schema for creating an APEX page."""
    app_id: int = Field(..., description="ID of the APEX application")
    page_name: str = Field(..., description="Name of the page")
    page_title: str = Field(..., description="Title of the page")
    page_mode: str = Field("Normal", description="Page mode (Normal, Modal Dialog, etc.)")
    page_type: str = Field(..., description="Type of page (Form, Report, Chart, etc.)")
    source_table: str = Field(None, description="Source table for the page (for form/report pages)")
    items: List[Dict[str, Any]] = Field([], description="List of page items to create")
    regions: List[Dict[str, Any]] = Field([], description="List of page regions to create")

def create_apex_application(
    app_name: str, 
    app_alias: str, 
    schema_name: str, 
    auth_scheme: str = "APEX_ACCESS_CONTROL",
    pages: List[Dict[str, Any]] = []
) -> Dict[str, Any]:
    """
    Generate code to create an Oracle APEX application.
    
    Args:
        app_name: Name of the APEX application
        app_alias: Alias for the APEX application (used in URLs)
        schema_name: Database schema to use for the application
        auth_scheme: Authentication scheme to use
        pages: List of pages to create initially
        
    Returns:
        Dictionary containing application details and creation scripts
    """
    # In a real implementation, this would generate actual APEX API calls or scripts
    # Here we're just creating a template/example
    
    app_id = 100  # Placeholder for actual app ID
    
    # Create the application script
    script = f"""-- Oracle APEX Application Creation Script
-- Application: {app_name}
-- Alias: {app_alias}
-- Schema: {schema_name}

BEGIN
    -- Set up application installation parameters
    apex_application_install.set_application_id({app_id});
    apex_application_install.set_application_alias('{app_alias}');
    apex_application_install.set_schema('{schema_name}');
    apex_application_install.set_application_name('{app_name}');
    
    -- Create the application
    wwv_flow_api.create_flow(
        p_id => {app_id},
        p_owner => '{schema_name}',
        p_name => '{app_name}',
        p_alias => '{app_alias}',
        p_page_view_logging => 'YES',
        p_checksum_salt => 'APEX_{app_id}_SALT',
        p_max_session_length_sec => 28800
    );
    
    -- Set up authentication scheme
    wwv_flow_api.create_authentication(
        p_id => wwv_flow_api.id({app_id}),
        p_flow_id => wwv_flow_api.id({app_id}),
        p_name => '{auth_scheme}',
        p_scheme_type => 'NATIVE_APEX_ACCOUNTS',
        p_invalid_session_type => 'LOGIN',
        p_use_secure_cookie_yn => 'N',
        p_cookie_name => 'ORA_WWV_APP_{app_id}'
    );
    
    -- Create Global Page (Page 0)
    wwv_flow_api.create_page(
        p_id => 0,
        p_flow_id => wwv_flow_api.id({app_id}),
        p_page_mode => 'Normal',
        p_step_title => 'Global Page',
        p_step_sub_title => 'Global Page',
        p_step_sub_title_type => 'TEXT_WITH_SUBSTITUTIONS',
        p_first_item => '',
        p_include_apex_css_js_yn => 'Y',
        p_autocomplete_on_off => 'OFF',
        p_step_template => wwv_flow_api.id(716607780903788372),
        p_page_is_public_y_n => 'N',
        p_protection_level => 'D',
        p_cache_page_yn => 'N',
        p_last_upd_yyyymmddhh24miss => '20220101000000'
    );
    
    -- Create Home Page (Page 1)
    wwv_flow_api.create_page(
        p_id => 1,
        p_flow_id => wwv_flow_api.id({app_id}),
        p_page_mode => 'Normal',
        p_step_title => 'Home',
        p_step_sub_title_type => 'TEXT_WITH_SUBSTITUTIONS',
        p_first_item => '',
        p_include_apex_css_js_yn => 'Y',
        p_autocomplete_on_off => 'OFF',
        p_step_template => wwv_flow_api.id(716607780903788372),
        p_page_is_public_y_n => 'N',
        p_protection_level => 'C',
        p_cache_page_yn => 'N',
        p_last_upd_yyyymmddhh24miss => '20220101000000'
    );
"""

    # Add pages if specified
    for i, page in enumerate(pages, start=2):  # Start from page 2 (after Home)
        page_name = page.get('name', f'Page {i}')
        page_type = page.get('type', 'Normal')
        source_table = page.get('source_table', '')
        
        script += f"""
    -- Create {page_name} (Page {i})
    wwv_flow_api.create_page(
        p_id => {i},
        p_flow_id => wwv_flow_api.id({app_id}),
        p_page_mode => 'Normal',
        p_step_title => '{page_name}',
        p_step_sub_title_type => 'TEXT_WITH_SUBSTITUTIONS',
        p_first_item => '',
        p_include_apex_css_js_yn => 'Y',
        p_autocomplete_on_off => 'OFF',
        p_step_template => wwv_flow_api.id(716607780903788372),
        p_page_is_public_y_n => 'N',
        p_protection_level => 'C',
        p_cache_page_yn => 'N',
        p_last_upd_yyyymmddhh24miss => '20220101000000'
    );
"""
        
        if page_type.lower() == 'report' and source_table:
            script += f"""
    -- Create Report Region on Page {i}
    wwv_flow_api.create_page_plug(
        p_id => wwv_flow_api.id({app_id}),
        p_flow_id => wwv_flow_api.id({app_id}),
        p_page_id => {i},
        p_plug_name => '{page_name} Report',
        p_region_name => '',
        p_plug_template => wwv_flow_api.id(716676055535817183),
        p_plug_display_sequence => 10,
        p_plug_display_column => 1,
        p_plug_display_point => 'BODY',
        p_query_type => 'SQL',
        p_plug_source => 'SELECT * FROM {source_table}',
        p_plug_source_type => 'NATIVE_IR',
        p_plug_query_options => 'DERIVED_REPORT_COLUMNS',
        p_prn_output_show_link => 'Y',
        p_prn_content_disposition => 'ATTACHMENT',
        p_prn_document_header => '{page_name} Report',
        p_prn_units => 'INCHES',
        p_prn_paper_size => 'LETTER',
        p_prn_width_units => 'PERCENTAGE',
        p_prn_width => 11,
        p_prn_height => 8.5,
        p_prn_orientation => 'HORIZONTAL',
        p_plug_customized => 'N'
    );
"""
        
        elif page_type.lower() == 'form' and source_table:
            script += f"""
    -- Create Form Region on Page {i}
    wwv_flow_api.create_page_plug(
        p_id => wwv_flow_api.id({app_id}),
        p_flow_id => wwv_flow_api.id({app_id}),
        p_page_id => {i},
        p_plug_name => '{page_name} Form',
        p_region_name => '',
        p_plug_template => wwv_flow_api.id(716676747173817184),
        p_plug_display_sequence => 10,
        p_plug_display_column => 1,
        p_plug_display_point => 'BODY',
        p_plug_query_options => 'DERIVED_REPORT_COLUMNS',
        p_attribute_01 => 'N',
        p_attribute_02 => 'TEXT',
        p_attribute_03 => 'Y'
    );
    
    -- Create Form Buttons
    wwv_flow_api.create_page_button(
        p_id => wwv_flow_api.id({app_id}),
        p_flow_id => wwv_flow_api.id({app_id}),
        p_page_id => {i},
        p_button_sequence => 30,
        p_button_plug_id => wwv_flow_api.id({app_id}),
        p_button_name => 'SAVE',
        p_button_action => 'SUBMIT',
        p_button_template_id => wwv_flow_api.id(716679261081817186),
        p_button_is_hot => 'Y',
        p_button_image_alt => 'Save',
        p_button_position => 'REGION_TEMPLATE_CREATE',
        p_button_condition_type => 'NEVER',
        p_grid_new_row => 'Y'
    );
"""
    
    script += """
END;
/
"""
    
    return {
        "app_id": app_id,
        "app_name": app_name,
        "app_alias": app_alias,
        "schema_name": schema_name,
        "auth_scheme": auth_scheme,
        "script": script,
        "pages": [{"id": 0, "name": "Global Page"}, {"id": 1, "name": "Home"}] + pages
    }

def create_apex_page(
    app_id: int,
    page_name: str,
    page_title: str,
    page_mode: str = "Normal",
    page_type: str = "Standard",
    source_table: str = None,
    items: List[Dict[str, Any]] = [],
    regions: List[Dict[str, Any]] = []
) -> Dict[str, Any]:
    """
    Generate code to create an Oracle APEX page.
    
    Args:
        app_id: ID of the APEX application
        page_name: Name of the page
        page_title: Title of the page
        page_mode: Page mode (Normal, Modal Dialog, etc.)
        page_type: Type of page (Form, Report, Chart, etc.)
        source_table: Source table for the page (for form/report pages)
        items: List of page items to create
        regions: List of page regions to create
        
    Returns:
        Dictionary containing page details and creation scripts
    """
    # In a real implementation, this would generate actual APEX API calls or scripts
    # Here we're just creating a template/example
    
    page_id = 10  # Placeholder for actual page ID
    
    # Create the page script
    script = f"""-- Oracle APEX Page Creation Script
-- Application: {app_id}
-- Page: {page_id} - {page_name}
-- Type: {page_type}

BEGIN
    -- Create the page
    wwv_flow_api.create_page(
        p_id => {page_id},
        p_flow_id => wwv_flow_api.id({app_id}),
        p_page_mode => '{page_mode}',
        p_step_title => '{page_title}',
        p_step_sub_title_type => 'TEXT_WITH_SUBSTITUTIONS',
        p_first_item => '',
        p_include_apex_css_js_yn => 'Y',
        p_autocomplete_on_off => 'OFF',
        p_step_template => wwv_flow_api.id(716607780903788372),
        p_page_is_public_y_n => 'N',
        p_protection_level => 'C',
        p_cache_page_yn => 'N',
        p_last_upd_yyyymmddhh24miss => '20220101000000'
    );
"""
    
    # Add regions based on page type
    if page_type.lower() == 'report' and source_table:
        script += f"""
    -- Create Report Region
    wwv_flow_api.create_page_plug(
        p_id => wwv_flow_api.id({app_id}),
        p_flow_id => wwv_flow_api.id({app_id}),
        p_page_id => {page_id},
        p_plug_name => '{page_name} Report',
        p_region_name => '',
        p_plug_template => wwv_flow_api.id(716676055535817183),
        p_plug_display_sequence => 10,
        p_plug_display_column => 1,
        p_plug_display_point => 'BODY',
        p_query_type => 'SQL',
        p_plug_source => 'SELECT * FROM {source_table}',
        p_plug_source_type => 'NATIVE_IR',
        p_plug_query_options => 'DERIVED_REPORT_COLUMNS',
        p_prn_output_show_link => 'Y',
        p_prn_content_disposition => 'ATTACHMENT',
        p_prn_document_header => '{page_name} Report',
        p_prn_units => 'INCHES',
        p_prn_paper_size => 'LETTER',
        p_prn_width_units => 'PERCENTAGE',
        p_prn_width => 11,
        p_prn_height => 8.5,
        p_prn_orientation => 'HORIZONTAL',
        p_plug_customized => 'N'
    );
"""
    
    elif page_type.lower() == 'form' and source_table:
        script += f"""
    -- Create Form Region
    wwv_flow_api.create_page_plug(
        p_id => wwv_flow_api.id({app_id}),
        p_flow_id => wwv_flow_api.id({app_id}),
        p_page_id => {page_id},
        p_plug_name => '{page_name} Form',
        p_region_name => '',
        p_plug_template => wwv_flow_api.id(716676747173817184),
        p_plug_display_sequence => 10,
        p_plug_display_column => 1,
        p_plug_display_point => 'BODY',
        p_plug_query_options => 'DERIVED_REPORT_COLUMNS',
        p_attribute_01 => 'N',
        p_attribute_02 => 'TEXT',
        p_attribute_03 => 'Y'
    );
    
    -- Create Form Source
    wwv_flow_api.create_form_source(
        p_id => wwv_flow_api.id({app_id}),
        p_flow_id => wwv_flow_api.id({app_id}),
        p_page_id => {page_id},
        p_plugin_id => wwv_flow_api.id(716623932180817002),
        p_table_name => '{source_table}',
        p_primary_key => NULL,
        p_unique_key => NULL,
        p_insert_check => NULL,
        p_update_check => NULL,
        p_delete_check => NULL
    );
    
    -- Create Form Buttons
    wwv_flow_api.create_page_button(
        p_id => wwv_flow_api.id({app_id}),
        p_flow_id => wwv_flow_api.id({app_id}),
        p_page_id => {page_id},
        p_button_sequence => 30,
        p_button_plug_id => wwv_flow_api.id({app_id}),
        p_button_name => 'SAVE',
        p_button_action => 'SUBMIT',
        p_button_template_id => wwv_flow_api.id(716679261081817186),
        p_button_is_hot => 'Y',
        p_button_image_alt => 'Save',
        p_button_position => 'REGION_TEMPLATE_CREATE',
        p_button_condition_type => 'NEVER',
        p_grid_new_row => 'Y'
    );
    
    wwv_flow_api.create_page_button(
        p_id => wwv_flow_api.id({app_id}),
        p_flow_id => wwv_flow_api.id({app_id}),
        p_page_id => {page_id},
        p_button_sequence => 10,
        p_button_plug_id => wwv_flow_api.id({app_id}),
        p_button_name => 'CANCEL',
        p_button_action => 'REDIRECT_PAGE',
        p_button_template_id => wwv_flow_api.id(716679069077817185),
        p_button_image_alt => 'Cancel',
        p_button_position => 'REGION_TEMPLATE_CLOSE',
        p_button_redirect_url => 'f?p=&APP_ID.:1:&SESSION.::&DEBUG.:RP:',
        p_grid_new_row => 'Y'
    );
"""
    
    # Add custom regions if specified
    for i, region in enumerate(regions, start=1):
        region_name = region.get('name', f'Region {i}')
        region_type = region.get('type', 'Static Content')
        region_source = region.get('source', '')
        
        script += f"""
    -- Create Custom Region: {region_name}
    wwv_flow_api.create_page_plug(
        p_id => wwv_flow_api.id({app_id}),
        p_flow_id => wwv_flow_api.id({app_id}),
        p_page_id => {page_id},
        p_plug_name => '{region_name}',
        p_region_name => '',
        p_plug_template => wwv_flow_api.id(716676747173817184),
        p_plug_display_sequence => {20 + i * 10},
        p_plug_display_column => 1,
        p_plug_display_point => 'BODY',
        p_plug_source => '{region_source}',
        p_plug_source_type => '{region_type}',
        p_plug_query_options => 'DERIVED_REPORT_COLUMNS',
        p_attribute_01 => 'N',
        p_attribute_02 => 'TEXT',
        p_attribute_03 => 'Y'
    );
"""
    
    # Add items if specified
    for i, item in enumerate(items, start=1):
        item_name = item.get('name', f'P{page_id}_ITEM{i}')
        item_label = item.get('label', f'Item {i}')
        item_type = item.get('type', 'TEXT')
        
        script += f"""
    -- Create Page Item: {item_name}
    wwv_flow_api.create_page_item(
        p_id => wwv_flow_api.id({app_id}),
        p_flow_id => wwv_flow_api.id({app_id}),
        p_page_id => {page_id},
        p_name => '{item_name}',
        p_data_type => 'VARCHAR2',
        p_is_required => 'N',
        p_accept_processing => 'REPLACE_EXISTING',
        p_item_sequence => {i * 10},
        p_item_plug_id => wwv_flow_api.id({app_id}),
        p_use_cache_before_default => 'YES',
        p_item_default_type => 'STATIC',
        p_prompt => '{item_label}',
        p_source => '',
        p_source_type => 'STATIC',
        p_display_as => '{item_type}',
        p_begin_on_new_line => 'YES',
        p_begin_on_new_field => 'YES',
        p_colspan => 1,
        p_rowspan => 1,
        p_grid_column => NULL,
        p_label_alignment => 'RIGHT',
        p_field_alignment => 'LEFT-CENTER',
        p_field_template => wwv_flow_api.id(716680073818817187),
        p_is_persistent => 'Y',
        p_attribute_01 => 'Y',
        p_attribute_02 => 'N',
        p_attribute_04 => 'TEXT',
        p_attribute_05 => 'BOTH'
    );
"""
    
    script += """
END;
/
"""
    
    return {
        "page_id": page_id,
        "app_id": app_id,
        "page_name": page_name,
        "page_title": page_title,
        "page_mode": page_mode,
        "page_type": page_type,
        "source_table": source_table,
        "script": script,
        "items": items,
        "regions": regions
    }

def create_apex_app_tool():
    """Create a tool for generating Oracle APEX applications."""
    return StructuredTool.from_function(
        func=create_apex_application,
        name="create_apex_application",
        description="Generate code to create an Oracle APEX application",
        args_schema=CreateAPEXAppInput
    )

def create_apex_page_tool():
    """Create a tool for generating Oracle APEX pages."""
    return StructuredTool.from_function(
        func=create_apex_page,
        name="create_apex_page",
        description="Generate code to create an Oracle APEX page",
        args_schema=CreateAPEXPageInput
    )