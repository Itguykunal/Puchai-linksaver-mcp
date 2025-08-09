from typing import Annotated, List, Dict, Any
from fastmcp import FastMCP
from fastmcp.server.auth.providers.bearer import BearerAuthProvider, RSAKeyPair
import markdownify
from mcp import ErrorData, McpError
from mcp.server.auth.provider import AccessToken
from mcp.types import INTERNAL_ERROR, INVALID_PARAMS, TextContent
from pydantic import AnyUrl, Field
import readabilipy
import json
import os
import asyncio
import logging
from datetime import datetime

# ------------------------------
#  CONFIGURATION
# ------------------------------
TOKEN = "a01b4e70fa61"  # Your application key for Puch AI
LINKS_FILE = "links_db.json"  # Changed to use existing file

# Configure logging to reduce noise
logging.basicConfig(level=logging.WARNING)
logging.getLogger("mcp").setLevel(logging.ERROR)
logging.getLogger("fastmcp").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)

# ------------------------------

class SimpleBearerAuthProvider(BearerAuthProvider):
    def __init__(self, token: str):
        k = RSAKeyPair.generate()
        super().__init__(
            public_key=k.public_key, jwks_uri=None, issuer=None, audience=None
        )
        self.token = token

    async def load_access_token(self, token: str) -> AccessToken | None:
        if token == self.token:
            return AccessToken(
                token=token,
                client_id="unknown",
                scopes=[],
                expires_at=None,
            )
        return None

class RichToolDescription:
    def __init__(self, description: str, use_when: str, side_effects: str | None):
        self.description = description
        self.use_when = use_when
        self.side_effects = side_effects
    def model_dump_json(self):
        import json
        return json.dumps(self.__dict__)

class LinkStorage:
    """Handle link storage operations with user isolation"""
    
    @staticmethod
    def get_user_file(user_phone: str) -> str:
        """Get the file path for a specific user"""
        # Create user_links directory if it doesn't exist
        links_dir = "user_links"  # Hardcoded directory name
        os.makedirs(links_dir, exist_ok=True)
        # Use user's phone number as filename (secure and unique)
        return os.path.join(links_dir, f"user_{user_phone}.json")
    
    @staticmethod
    def load_links(user_phone: str) -> Dict[str, Any]:
        """Load links from user-specific JSON file"""
        user_file = LinkStorage.get_user_file(user_phone)
        default_data = {"links": [], "next_id": 1}
        
        if not os.path.exists(user_file):
            LinkStorage.save_links(user_phone, default_data)
            return default_data
        
        try:
            with open(user_file, 'r') as f:
                data = json.load(f)
                
            # Ensure required keys exist
            if "links" not in data:
                data["links"] = []
            if "next_id" not in data:
                data["next_id"] = 1
                
            # Fix next_id if it's wrong
            if data["links"] and data["next_id"] <= max(link.get("id", 0) for link in data["links"]):
                data["next_id"] = max(link.get("id", 0) for link in data["links"]) + 1
                
            return data
            
        except (json.JSONDecodeError, FileNotFoundError, Exception):
            # If anything goes wrong, create fresh file
            LinkStorage.save_links(user_phone, default_data)
            return default_data
    
    @staticmethod
    def save_links(user_phone: str, data: Dict[str, Any]) -> None:
        """Save links to user-specific JSON file"""
        try:
            # Ensure the directory exists
            links_dir = "user_links"  # Hardcoded directory name
            os.makedirs(links_dir, exist_ok=True)
            user_file = LinkStorage.get_user_file(user_phone)
            with open(user_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving links for user {user_phone}: {e}")
            raise e  # Re-raise to help with debugging
    
    @staticmethod
    def find_link_by_id(user_phone: str, link_id: int) -> tuple[Dict[str, Any], int]:
        """Find link by ID and return link data and its index for specific user"""
        data = LinkStorage.load_links(user_phone)
        for i, link in enumerate(data["links"]):
            if link.get("id") == link_id:
                return link, i
        return None, -1

def get_current_user_phone() -> str:
    """Get the current user's phone number from MCP context"""
    # For now, we'll use the owner's phone as default
    # In a real MCP environment, this would come from the authenticated user context
    # The MCP protocol should provide user identification
    try:
        # Hardcoded phone number for now - will be replaced with dynamic user identification
        owner_phone = "917903824329"  # Your phone number with country code
        return owner_phone
    except Exception as e:
        print(f"Error getting user phone: {e}")
        return "917903824329"  # Fallback

class Fetch:
    IGNORE_ROBOTS_TXT = True
    USER_AGENT = "LinkSaver/1.0 (Autonomous)"

    @classmethod
    async def fetch_url(cls, url: str, user_agent: str, force_raw: bool = False):
        from httpx import AsyncClient, HTTPError
        async with AsyncClient() as client:
            try:
                response = await client.get(
                    url,
                    follow_redirects=True,
                    headers={"User-Agent": user_agent},
                    timeout=30,
                )
            except HTTPError as e:
                raise McpError(
                    ErrorData(
                        code=INTERNAL_ERROR, message=f"Failed to fetch {url}: {e!r}"
                    )
                )
            if response.status_code >= 400:
                raise McpError(
                    ErrorData(
                        code=INTERNAL_ERROR,
                        message=f"Failed to fetch {url} - status code {response.status_code}",
                    )
                )

            page_raw = response.text
        content_type = response.headers.get("content-type", "")
        is_page_html = (
            "<html" in page_raw[:100] or "text/html" in content_type or not content_type
        )

        if is_page_html and not force_raw:
            return cls.extract_content_from_html(page_raw), ""
        return (
            page_raw,
            f"Content type {content_type} cannot be simplified to markdown, but here is the raw content:\n",
        )

    @staticmethod
    def extract_content_from_html(html: str) -> str:
        ret = readabilipy.simple_json.simple_json_from_html_string(
            html, use_readability=True
        )
        if not ret["content"]:
            return "<error>Page failed to be simplified from HTML</error>"
        content = markdownify.markdownify(
            ret["content"], heading_style=markdownify.ATX
        )
        return content

# Initialize MCP with better error handling
try:
    mcp = FastMCP(
        "Link Saver MCP Server",
        auth=SimpleBearerAuthProvider(TOKEN),
    )
except Exception as e:
    print(f"Warning: MCP initialization issue (continuing anyway): {e}")
    mcp = FastMCP("Link Saver MCP Server")

# Link Management Tools

AddLinkToolDescription = RichToolDescription(
    description="Add a new link to the saved links collection.",
    use_when="When user wants to save a URL with optional title and description.",
    side_effects="Creates a new entry in the links database.",
)

@mcp.tool(description=AddLinkToolDescription.model_dump_json())
async def add_link(
    url: Annotated[str, Field(description="URL to save")],
    title: Annotated[str, Field(description="Title for the link")] = "",
    description: Annotated[str, Field(description="Description of the link")] = ""
) -> str:
    """Add a new link to the collection"""
    if not url.strip():
        raise McpError(ErrorData(code=INVALID_PARAMS, message="URL is required"))
    
    try:
        # Get current user's phone number for user-specific storage
        user_phone = get_current_user_phone()
        print(f"DEBUG: Using user phone: {user_phone}")
        
        # Clean and validate URL
        clean_url = url.strip()
        if not clean_url.startswith(('http://', 'https://')):
            clean_url = 'https://' + clean_url
        
        print(f"DEBUG: Loading links for user: {user_phone}")
        data = LinkStorage.load_links(user_phone)
        print(f"DEBUG: Loaded data: {data}")
        
        # Calculate the correct new ID (always sequential)
        new_id = len(data["links"]) + 1
        
        new_link = {
            "id": new_id,
            "url": clean_url,
            "title": title.strip() if title else f"Link {new_id}",
            "description": description.strip(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        data["links"].append(new_link)
        data["next_id"] = new_id + 1  # Set next_id for future additions
        
        print(f"DEBUG: Saving data for user: {user_phone}")
        LinkStorage.save_links(user_phone, data)
        print(f"DEBUG: Save successful")
        
        return f"Link saved successfully!\nID: {new_id}\nTitle: {new_link['title']}\nURL: {new_link['url']}"
    
    except Exception as e:
        error_msg = f"Error saving link: {str(e)}"
        print(f"DEBUG ERROR: {error_msg}")
        return error_msg

ListLinksToolDescription = RichToolDescription(
    description="List all saved links with their IDs, titles, and URLs.",
    use_when="When user wants to see all saved links.",
    side_effects="None - read-only operation.",
)

@mcp.tool(description=ListLinksToolDescription.model_dump_json())
async def list_links() -> str:
    """List all saved links for the current user"""
    try:
        # Get current user's phone number for user-specific storage
        user_phone = get_current_user_phone()
        data = LinkStorage.load_links(user_phone)
        
        if not data.get("links"):
            return "No links saved yet. Add your first link to get started!"
        
        # Use simple, safe formatting
        result = "Your Saved Links:\n"
        for link in data["links"]:
            result += f"\nID: {link.get('id', 'Unknown')}\n"
            result += f"Title: {link.get('title', 'No title')}\n"
            result += f"URL: {link.get('url', 'No URL')}\n"
            if link.get('description'):
                result += f"Description: {link['description']}\n"
            result += f"Created: {link.get('created_at', 'Unknown')[:10]}\n"
        
        result += f"\nTotal: {len(data['links'])} links"
        return result
    
    except Exception as e:
        return f"Error: Unable to retrieve links - {str(e)}"

UpdateLinkToolDescription = RichToolDescription(
    description="Update an existing link's title, URL, or description.",
    use_when="When user wants to modify a saved link.",
    side_effects="Updates the link in the database.",
)

@mcp.tool(description=UpdateLinkToolDescription.model_dump_json())
async def update_link(
    link_id: Annotated[int, Field(description="ID of the link to update")],
    url: Annotated[str, Field(description="New URL (optional)")] = "",
    title: Annotated[str, Field(description="New title (optional)")] = "",
    description: Annotated[str, Field(description="New description (optional)")] = ""
) -> str:
    """Update an existing link for the current user"""
    user_phone = get_current_user_phone()
    data = LinkStorage.load_links(user_phone)
    link, index = LinkStorage.find_link_by_id(user_phone, link_id)
    
    if not link:
        raise McpError(ErrorData(code=INVALID_PARAMS, message=f"Link with ID {link_id} not found"))
    
    # Update fields if provided
    if url.strip():
        link["url"] = url.strip()
    if title.strip():
        link["title"] = title.strip()
    if description.strip():
        link["description"] = description.strip()
    
    link["updated_at"] = datetime.now().isoformat()
    
    data["links"][index] = link
    LinkStorage.save_links(user_phone, data)
    
    return f"✅ Link updated successfully!\nID: {link['id']}\nTitle: {link['title']}\nURL: {link['url']}"

DeleteLinkToolDescription = RichToolDescription(
    description="Delete a saved link by its ID. All links after the deleted one will be renumbered automatically.",
    use_when="When user wants to remove a saved link.",
    side_effects="Permanently removes the link from the database and renumbers remaining links.",
)

@mcp.tool(description=DeleteLinkToolDescription.model_dump_json())
async def delete_link(
    link_id: Annotated[int, Field(description="ID of the link to delete")]
) -> str:
    """Delete a link by ID and reindex all remaining links for the current user"""
    user_phone = get_current_user_phone()
    data = LinkStorage.load_links(user_phone)
    link, index = LinkStorage.find_link_by_id(user_phone, link_id)
    
    if not link:
        raise McpError(ErrorData(code=INVALID_PARAMS, message=f"Link with ID {link_id} not found"))
    
    # Store deleted link info for the response
    deleted_link = data["links"][index].copy()
    
    # Remove the link
    data["links"].pop(index)
    
    # Reindex all remaining links
    for i, link in enumerate(data["links"]):
        link["id"] = i + 1  # Start from 1
        link["updated_at"] = datetime.now().isoformat()
    
    # Update next_id to be one more than the total count
    data["next_id"] = len(data["links"]) + 1
    
    LinkStorage.save_links(user_phone, data)
    
    result = f"🗑️ Link deleted successfully!\n"
    result += f"Deleted: {deleted_link['title']} ({deleted_link['url']})\n"
    result += f"Remaining links have been renumbered. Total links now: {len(data['links'])}"
    
    return result

# Validation Tool (Required for public sharing)

ValidateToolDescription = RichToolDescription(
    description="Validate the MCP server connection and authentication.",
    use_when="When the system needs to verify server connectivity and auth.",
    side_effects="None - validation check only.",
)

@mcp.tool(description=ValidateToolDescription.model_dump_json())
async def validate() -> str:
    """Validate MCP server connection and return server owner's phone number"""
    try:
        # According to Puch AI docs, validate tool must return owner's phone number
        # in format: {country_code}{number} (e.g., 919876543210 for +91-9876543210)
        
        # Return phone number as required by Puch AI for authentication
        return "917903824329"  # Your phone number with India country code
        
    except Exception as e:
        # Even on error, we should return the phone number for auth
        return "917903824329"

# Health Check Tool (Additional tool for public sharing)

HealthToolDescription = RichToolDescription(
    description="Check the health status of the MCP server.",
    use_when="When checking if the server is running properly.",
    side_effects="None - health check only.",
)

@mcp.tool(description=HealthToolDescription.model_dump_json())
async def health() -> str:
    """Health check endpoint"""
    try:
        # Test basic functionality with current user
        user_phone = get_current_user_phone()
        data = LinkStorage.load_links(user_phone)
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected",
            "user_links_count": len(data.get("links", [])),
            "uptime": "active"
        }
        
        return f"🟢 Server Health: {health_status['status']}\n" \
               f"Database: {health_status['database']}\n" \
               f"Your Links: {health_status['user_links_count']} stored\n" \
               f"Checked: {health_status['timestamp'][:19]}"
        
    except Exception as e:
        return f"🔴 Server Health: unhealthy - {str(e)}"

# Fetch Tools

PuchMcpToolDescription = RichToolDescription(
    description="Fetch content from puch.ai/mcp specifically.",
    use_when="When user wants to see the content from puch.ai/mcp.",
    side_effects="None - read-only operation.",
)

@mcp.tool(description=PuchMcpToolDescription.model_dump_json())
async def fetch_puch_mcp() -> list[TextContent]:
    """Fetch content from puch.ai/mcp"""
    url = "https://puch.ai/mcp"
    content, prefix = await Fetch.fetch_url(url, Fetch.USER_AGENT)
    return [TextContent(type="text", text=f"{prefix}Contents of {url}:\n{content}")]

FetchToolDescription = RichToolDescription(
    description="Fetch content from any URL and return it as markdown.",
    use_when="When user wants to read content from a webpage.",
    side_effects="None - read-only operation.",
)

@mcp.tool(description=FetchToolDescription.model_dump_json())
async def fetch(
    url: Annotated[AnyUrl, Field(description="URL to fetch")],
    max_length: int = 5000,
    start_index: int = 0,
    raw: bool = False,
) -> list[TextContent]:
    """Fetch content from a URL"""
    url_str = str(url).strip()
    if not url:
        raise McpError(ErrorData(code=INVALID_PARAMS, message="URL is required"))

    content, prefix = await Fetch.fetch_url(url_str, Fetch.USER_AGENT, force_raw=raw)
    original_length = len(content)
    if start_index >= original_length:
        content = "<error>No more content available.</error>"
    else:
        truncated_content = content[start_index : start_index + max_length]
        if not truncated_content:
            content = "<error>No more content available.</error>"
        else:
            content = truncated_content
            actual_content_length = len(truncated_content)
            remaining_content = original_length - (start_index + actual_content_length)
            if actual_content_length == max_length and remaining_content > 0:
                next_start = start_index + actual_content_length
                content += f"\n\n<error>Content truncated. Call the fetch tool with a start_index of {next_start} to get more content.</error>"
    return [TextContent(type="text", text=f"{prefix}Contents of {url}:\n{content}")]

async def main():
    try:
        print("Starting MCP server...")
        # Add a small delay to ensure proper initialization
        await asyncio.sleep(0.1)
        
        await mcp.run_async(
            "streamable-http",
            host="0.0.0.0",
            port=8085,
        )
    except Exception as e:
        print(f"Server error (but continuing): {e}")
        # Fallback: try again with basic configuration
        try:
            await mcp.run_async(
                "streamable-http",
                host="127.0.0.1",
                port=8085,
            )
        except Exception as e2:
            print(f"Fallback also failed: {e2}")

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Startup error: {e}")
        print("Check if port 8085 is already in use or try a different port")