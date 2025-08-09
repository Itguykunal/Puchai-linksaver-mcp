# Puchai-linksaver-mcp

A Python MCP server tool to save, manage, and fetch web links using Puch AI’s MCP framework.  
Supports adding, listing, updating, and deleting links with markdown content extraction.

---
## How to Use on Puch AI

To start using the Link Saver MCP on Puch AI, use this command in chat:


```

/mcp use eLt2pGMdOu

````

## or 
https://puch.ai/mcp/wHeThy0jj5



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

## Example Conversation (CRUD Operations)

Here’s how interacting with **Puchai-linksaver-mcp** looks in a real chat with Puch AI:

---

**You:**

> Save this link: [https://leetcode.com/problems/subarray-sum-equals-k/description/](https://leetcode.com/problems/subarray-sum-equals-k/description/) with title "leetcode" and description "solve this question before 12th Aug"

**Puch AI:**
✅ Link added successfully!
**ID:** 1

**Title:** leetcode

**URL:** [https://leetcode.com/problems/subarray-sum-equals-k/description/](https://leetcode.com/problems/subarray-sum-equals-k/description/)

**Description** solve this question before 12th Aug

---

**You:**

> Save this link: [https://github.com/TurboML-Inc/mcp-starter?tab=readme-ov-file](https://github.com/TurboML-Inc/mcp-starter?tab=readme-ov-file)

**Puch AI:**
✅ Link added successfully!

**ID:** 2

**Title:** Link 2

**URL:** [https://github.com/TurboML-Inc/mcp-starter?tab=readme-ov-file](https://github.com/TurboML-Inc/mcp-starter?tab=readme-ov-file)

---

**You:**

> Show me all my links

**Puch AI:**
📋 **Your saved links:**

```
ID: 1  
Title: leetcode  
URL: https://leetcode.com/problems/subarray-sum-equals-k/description/  
Description: solve this question before 12th Aug  
Created: 2025-08-09

ID: 2  
Title: Link 2  
URL: https://github.com/TurboML-Inc/mcp-starter?tab=readme-ov-file  
Created: 2025-08-09

Total: 2 links
```

---

**You:**

> Update link 1 with https://github.com

**Puch AI:**
✅ Link updated successfully!

**ID:** 1

**Title:** leetcode

**URL:** [https://github.com](https://github.com)

---

**You:**

> Delete link 2

**Puch AI:**

🗑️ Link deleted successfully!

---

This example shows how easy it is to add, view, update, delete, and fetch links using natural language with Puch AI and your Link Saver MCP server! 

---

## Tips

- **Be natural** — talk to Puch AI like a friend  
- **Use link IDs** — refer to links by their numbers for updates or deletions  
- **No special commands needed** — Puch AI automatically chooses the right tool  
- **Links persist** — all saved links are stored in the `links_db.json` file  

---

## For developement - Setup & Run

1. Install dependencies (e.g., via `pip install -r requirements.txt`)  
2. Run the server:  

```bash

   python links_mcp.py

```
3. In a new terminal, run ngrok to expose port 8085:

```bash

    ngrok http 8085
```
4. Ngrok will show a public forwarding URL like: 

```nginx

     https://example.ngrok.io -> http://localhost:8085

```

5. Use the ngrok URL (https://example.ngrok.io) in your Puch AI MCP usage, for example:

```bash

    /mcp connect https://example.ngrok.io <bearer_token>

```

---

By itguykunal
