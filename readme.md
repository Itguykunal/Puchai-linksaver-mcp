# Puchai-linksaver-mcp

A Python MCP server tool to save, manage, and fetch web links using Puch AI’s MCP framework.  
Supports adding, listing, updating, and deleting links with markdown content extraction.

---
## How to Use on Puch AI

To start using the Link Saver MCP on Puch AI, use this command in chat:


```

/mcp use wHeThy0jj5

````

or

```

[https://puch.ai/mcp/wHeThy0jj5](https://puch.ai/mcp/wHeThy0jj5)

````

Anyone can connect using this command and start saving and managing links!

---

## How to Use Your Link Saver Tools

Just chat naturally with Puch AI, and it will automatically use your tools when needed.

### 🔗 Adding Links  
Examples:  
- Save this link: https://github.com  
- Add https://stackoverflow.com with title "Stack Overflow" and description "Programming Q&A site"  
- Store this URL: https://google.com called Google Search  

### 📋 Viewing Your Links  
Ask:  
- Show me all my saved links  
- List my bookmarks  
- What links do I have?  

### ✏️ Updating Links  
Say:  
- Update link 1 with title "New Title"  
- Change the description of link 2 to "Updated description"  
- Modify link 3's URL to https://newurl.com  

### 🗑️ Deleting Links  
Tell it:  
- Delete link 1  
- Remove link number 3  
- Delete the link with ID 2  

### 🌐 Fetching Content  
Request:  
- Fetch content from https://news.ycombinator.com  
- Get the content from puch.ai/mcp  
- Show me what's on https://example.com  

---

## Example Conversation

**You:**  
> Save this link: https://claude.ai with title "Claude AI" and description "AI assistant"

**Puch AI:**  
✅ Link added successfully!  
ID: 1  
Title: Claude AI  
URL: https://claude.ai  

**You:**  
> Show me all my links

**Puch AI:**  
📋 **Saved Links:**  
1. Claude AI  
   🔗 https://claude.ai  
   📝 AI assistant  
   📅 Created: 2025-08-09 12:30:45  

**You:**  
> Update link 1 with description "Best AI assistant ever"

**Puch AI:**  
✅ Link updated successfully!  
ID: 1  
Title: Claude AI  
URL: https://claude.ai  

---

## Tips

- **Be natural** — talk to Puch AI like a friend  
- **Use link IDs** — refer to links by their numbers for updates or deletions  
- **No special commands needed** — Puch AI automatically chooses the right tool  
- **Links persist** — all saved links are stored in the `links_db.json` file  

---

## Setup & Run

1. Install dependencies (e.g., via `pip install -r requirements.txt`)  
2. Run the server:  
   ```bash
   python your_script_name.py
````

3. Connect Puch AI to this MCP server and start chatting!

---

Made with ❤️ using Puch AI MCP framework.
