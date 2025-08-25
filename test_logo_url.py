"""
Test script for the get_logo_url tool.
"""

from sample_agent.agent import get_logo_url

if __name__ == "__main__":
    # Test with default filename
    logo_url = get_logo_url()
    print(f"Logo URL with default filename: {logo_url}")
    
    # Test with custom filename
    custom_logo_url = get_logo_url("logo_acAI_icone_transparente_300dpi.png")
    print(f"Logo URL with custom filename: {custom_logo_url}")
