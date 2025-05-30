# 🔍 TG IOC Monitor

A Telegram-based Indicator of Compromise (IOC) monitoring and collection system that automatically detects and stores IP addresses, domain names, and URLs from Telegram messages.

## 📋 Features

- **Real-time IOC Detection**: Automatically identifies IP addresses, domains, and URLs in Telegram messages
- **TLD Validation**: Validates domains against official IANA Top-Level Domain list
- **SQLite Database**: Persistent storage with comprehensive metadata
- **Duplicate Prevention**: Prevents storing duplicate IOCs from the same message
- **Rich Context**: Stores chat information, sender details, and message content
- **Search & Export**: Query and export IOCs for threat intelligence analysis
- **Command-line Management**: Full database management through CLI tools
- **Web GUI**: User-friendly web interface for IOC management

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Telegram API credentials (API_ID and API_HASH)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/GGal1leo/TG_IOC.git
cd TG_IOC
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables:
```bash
cp .env.example .env
# Edit .env and add your Telegram API credentials
```

4. Run the monitor:
```bash
python main.py
```

5. Launch the Web GUI (optional):
```bash
python web_gui.py
```
Then open http://localhost:5000 in your browser.

## ⚙️ Configuration

Create a `.env` file with your Telegram API credentials:

```env
API_ID=your_api_id_here
API_HASH=your_api_hash_here
```

Get your API credentials from [my.telegram.org](https://my.telegram.org/auth)

## 🗄️ Database Schema

The system stores IOCs with the following information:

| Field | Description |
|-------|-------------|
| `ioc_value` | The actual IOC (IP, domain, or URL) |
| `ioc_type` | Type of IOC (`ip`, `domain`, `url`) |
| `source_chat_id` | Telegram chat ID where IOC was found |
| `source_chat_title` | Name/title of the source chat |
| `source_message_id` | Message ID containing the IOC |
| `message_content` | Full text of the message |
| `sender_id` | User ID of the message sender |
| `sender_username` | Username of the message sender |
| `detected_at` | Timestamp when IOC was detected |

## 🛠️ Management Tools

### Command Line Interface
Use the `ioc_manager.py` script to interact with your IOC database:

### Show Statistics
```bash
python ioc_manager.py stats
```

### List Recent IOCs
```bash
# List all IOCs (last 20)
python ioc_manager.py list

# List specific type with custom limit
python ioc_manager.py list --type domain --limit 50
```

### Search IOCs
```bash
python ioc_manager.py search "malicious.com"
```

### Export to CSV
```bash
python ioc_manager.py export --output my_iocs.csv
```

### List Unique IOCs
```bash
# All unique IOCs
python ioc_manager.py unique

# Unique IPs only
python ioc_manager.py unique --type ip
```

## 📊 IOC Types Detected

### IP Addresses
- IPv4 addresses (0.0.0.0 to 255.255.255.255)
- Validates against standard IP format

### Domain Names
- Validates against official IANA TLD list
- Supports subdomains and international domains
- Filters out invalid TLD combinations

### URLs
- HTTP and HTTPS links
- Captures full URL with parameters
- Detects shortened URLs and redirects

## 🔧 Technical Details

### Dependencies
- **telethon**: Telegram client library
- **python-dotenv**: Environment variable management
- **requests**: HTTP requests for TLD list fetching
- **sqlite3**: Built-in database (no additional installation needed)

### Architecture
- `main.py`: Core monitoring and detection engine
- `database.py`: SQLite database abstraction layer
- `ioc_manager.py`: Command-line database management tool

### Data Flow
1. Monitor connects to Telegram using user credentials
2. Processes all incoming messages in real-time
3. Applies regex patterns to detect potential IOCs
4. Validates domains against current TLD list
5. Stores unique IOCs with full context in SQLite database
6. Provides real-time feedback and statistics

## 🛡️ Security Considerations

- **User Session**: Operates as a user client, not a bot
- **Local Storage**: All data stored locally in SQLite database
- **No External APIs**: Only fetches official TLD list from IANA
- **Read Acknowledgment**: Marks messages as read after processing

## 📈 Use Cases

- **Threat Intelligence**: Collect IOCs from threat actor channels
- **Security Research**: Monitor malware distribution channels
- **Incident Response**: Track indicators across communication platforms
- **OSINT**: Open source intelligence gathering from public channels

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is intended for legitimate security research and threat intelligence purposes only. Users are responsible for ensuring compliance with applicable laws and Telegram's Terms of Service. The authors are not responsible for any misuse of this software.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the existing issues on GitHub
2. Create a new issue with detailed information
3. Provide logs and error messages when possible

---

**Made with ❤️ for the cybersecurity community**

---

### Web GUI Interface
Launch the web interface for a user-friendly IOC management experience:

```bash
python web_gui.py
```

The web interface provides:
- **Dashboard**: Real-time statistics and recent IOCs
- **IOC Browser**: Searchable table with filtering options
- **Advanced Search**: Powerful search with suggestions
- **Analytics**: Charts and insights about collected data
- **Export Tools**: One-click CSV export functionality

Access the web interface at: http://localhost:5000

#### Web GUI Features:
- 📊 **Interactive Dashboard** with live statistics
- 🔍 **Advanced Search** with real-time filtering
- 📈 **Analytics Charts** showing IOC distribution and trends
- 📋 **Sortable Tables** with copy-to-clipboard functionality
- 📤 **One-click Export** to CSV format
- 📱 **Responsive Design** for mobile and desktop
- ⚡ **Real-time Updates** with auto-refresh capabilities
