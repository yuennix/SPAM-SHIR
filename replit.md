# Facebook Tools Suite - CLI Application

## Overview
This is a comprehensive command-line interface (CLI) toolkit for Facebook account management and automation. The suite integrates features from multiple sources to provide 8 powerful tools:

1. **Spam Share** - Automatically share Facebook posts with multi-threading support (publicly visible)
2. **Token Getter** - Generate Facebook access tokens from user credentials (single account)
3. **Link to UID|Password Converter** - Convert Facebook profile links to uid|password format
4. **Cookie Extractor** - Extract Facebook session cookies (bulk processing)
5. **AppState Generator** - Generate Facebook AppState JSON (bulk processing)
6. **C_USER Extractor** - Extract C_USER values (bulk processing)
7. **All Data Export** - Get everything (token, cookie, AppState, C_USER) in one operation
8. **Exit** - Exit the application

## Recent Changes
- **November 17, 2025 (Latest Update)**:
  - **MASSIVE INTEGRATION**: Merged all features from yuennix/FB-TOOLS repository
    - Added Link to UID|Password Converter (extracts UID from Facebook profile links)
    - Added Cookie Extractor with bulk processing support
    - Added AppState Generator for JSON format export
    - Added C_USER Extractor for session management
    - Added All-in-One Data Export (gets everything at once)
    - Now has 8 total features in one comprehensive suite
  - **Installed BeautifulSoup4** for HTML parsing in link-to-UID conversion
  - **Enhanced Menu**: Redesigned main menu to display all 8 features clearly
  - **Bulk Processing**: Added support for processing multiple accounts at once
  - **File Export**: Added timestamped file saving for all bulk operations
  
- **November 17, 2025 (Earlier)**:
  - **CRITICAL FIX**: Changed shares to be publicly visible instead of hidden
    - Set `published=1` (was 0 - hidden/unpublished)
    - Added `privacy=EVERYONE` for public visibility on social media
    - Shares now appear on the Facebook link and are publicly accessible
  - **MAJOR UPDATE**: Integrated advanced share implementation with multi-threading support
  - Added `FacebookPoster` class using Graph API v13.0 for reliable sharing
  - Implemented concurrent sharing with ThreadPoolExecutor (up to 50 workers)
  - Fixed HTTP 400 errors by using proper URL parameter encoding
  - Added detailed statistics: success/failure tracking, duration timing
  - Enhanced error handling with specific HTTP status codes and Facebook error messages
  - Fixed syntax error in main entry point
  - Integrated improved token getter from yuennix/token_getter repository
  - Created requirements.txt with all dependencies
  - Set up Python 3.11 environment

## Project Architecture

### Dependencies
- **requests**: HTTP library for API calls
- **colorama**: Terminal color support
- **rich**: Rich text and beautiful formatting in terminal
- **beautifulsoup4**: HTML parsing for link-to-UID conversion
- **concurrent.futures**: Multi-threading support for parallel operations
- **json**: JSON formatting for AppState export
- **base64/marshal**: Cookie loading for UID extraction

### Main Components

#### Core Functions
- **main_menu()**: Main application menu with 8 features
- **get_facebook_token()**: Core token generation using b-api.facebook.com
- **load_cookie()**: Load Facebook cookie for UID extraction

#### Spam Share Module
- **FacebookPoster**: Class for Facebook post sharing using Graph API v13.0
- **share_with_threading()**: Multi-threaded sharing with configurable worker pool (1-50 workers)
- **spam_share()**: Facebook post sharing interface with public visibility

#### Single Account Features
- **token_getter()**: Single account token generation with full session info

#### Link Conversion
- **link_to_uid_converter()**: Convert Facebook profile links to uid|password format
- **get_uid_from_link()**: Extract UID from Facebook profile URL using BeautifulSoup

#### Bulk Processing Features
- **bulk_processor()**: Universal bulk processor for multiple accounts
- **display_bulk_results()**: Format and display bulk processing results
- **save_bulk_results()**: Save results to timestamped files

### Key Features

#### 1. Spam Share
- Multi-threading support for faster sharing (up to 50 concurrent workers)
- Real-time success/failure tracking
- Duration and performance statistics
- Input validation and error handling
- Support for both post IDs and full URLs
- **Privacy settings: PUBLIC (EVERYONE)** - Shares are publicly visible
- **Published status: Published (visible shares)** - Posts appear on social media

#### 2. Token Getter (Single Account)
- Uses b-api.facebook.com endpoint for reliability
- Returns tokens in uid|token format
- Displays full session information (cookies, c_user, datr)
- Supports email, phone, or UID as login credentials
- Perfect for single account quick access

#### 3. Link to UID|Password Converter
- Convert Facebook profile URLs to uid|password format
- Supports multiple link formats (www, m, mbasic)
- Bulk conversion support
- Auto-extracts UID from profile links
- Save results to file option
- **Security**: Requires user to provide their own Facebook cookie (no remote credentials)

#### 4. Cookie Extractor (Bulk)
- Process multiple accounts simultaneously
- Extract session cookies for all accounts
- Real-time success/failure indicators
- Timestamped file export
- Copy-ready output format

#### 5. AppState Generator (Bulk)
- Generate AppState JSON for multiple accounts
- Compatible with automation tools
- Includes all session cookies in JSON format
- Bulk processing with progress tracking
- Auto-save to timestamped files

#### 6. C_USER Extractor (Bulk)
- Extract C_USER and DATR values
- Process multiple accounts at once
- Essential for session management
- uid|c_user format output
- File export with timestamps

#### 7. All Data Export (Bulk)
- Get everything in one operation
- Includes: Token, Cookie, AppState, C_USER
- Most comprehensive data export
- Perfect for backup or migration
- Organized output with clear sections

### File Structure
```
.
├── ewan.py              # Main application file
├── requirements.txt     # Python dependencies
├── .gitignore          # Git ignore patterns
└── replit.md           # This file
```

## Usage Guide

### 1. Spam Share
**Purpose**: Share Facebook posts publicly with multi-threading support

**Workflow**:
1. Select "1. Spam Share" from menu
2. Enter access token
3. Enter post ID or full URL
4. Enter number of shares
5. Choose multi-threading (y/n, default=y)
6. Set number of workers (1-50, default=10)
7. View real-time progress and statistics

**Features**:
- Publicly visible shares (EVERYONE privacy)
- Multi-threaded for speed
- Real-time success/failure tracking
- Duration statistics

### 2. Token Getter (Single Account)
**Purpose**: Get access token and session data for one account

**Workflow**:
1. Select "2. Token Getter" from menu
2. Enter email/phone/uid
3. Enter password
4. View results: token, cookie, c_user, datr

**Output Format**: `uid|token`

### 3. Link to UID|Password Converter
**Purpose**: Convert Facebook profile links to uid|password format

**Workflow**:
1. Select "3. Link to UID|Pass" from menu
2. Enter your Facebook cookie (get from browser's developer tools)
   - Press F12 in browser → Application tab → Cookies → facebook.com
   - Copy the full cookie string
3. Enter password (used for all accounts)
4. Paste Facebook profile links (one per line)
5. Press Enter twice to process
6. View results in uid|password format
7. Optionally save to file

**Supported Link Formats**:
- `https://www.facebook.com/username`
- `https://m.facebook.com/profile.php?id=123456`
- `https://facebook.com/username`

**Note**: This feature requires your own Facebook session cookie for security reasons. No remote credentials are used.

### 4. Cookie Extractor (Bulk)
**Purpose**: Extract cookies from multiple accounts

**Workflow**:
1. Select "4. Get Cookie" from menu
2. Paste uid|password pairs (one per line)
3. Press Enter twice to process
4. View cookie strings
5. Optionally save to timestamped file

**Output**: Cookie strings ready to use

### 5. AppState Generator (Bulk)
**Purpose**: Generate AppState JSON for automation tools

**Workflow**:
1. Select "5. Get AppState" from menu
2. Paste uid|password pairs (one per line)
3. Press Enter twice to process
4. View JSON AppState
5. Optionally save to timestamped file

**Output**: JSON format AppState arrays

### 6. C_USER Extractor (Bulk)
**Purpose**: Extract C_USER and DATR values

**Workflow**:
1. Select "6. Get C_USER" from menu
2. Paste uid|password pairs (one per line)
3. Press Enter twice to process
4. View uid|c_user pairs
5. Optionally save to timestamped file

**Output**: `uid|c_user` format

### 7. All Data Export (Bulk)
**Purpose**: Get token, cookie, AppState, and C_USER all at once

**Workflow**:
1. Select "7. Get All Data" from menu
2. Paste uid|password pairs (one per line)
3. Press Enter twice to process
4. View comprehensive data for each account
5. Optionally save to timestamped file

**Output**: Complete data package per account

### Input Formats
- **uid|password**: `email@example.com|yourpassword` or `+1234567890|yourpassword` or `100012345678|yourpassword`
- **Profile Links**: Any Facebook profile URL
- **Access Token**: Full Facebook access token string

## Technical Details

### Token Generation
The token getter uses Facebook's b-api.facebook.com endpoint with the following parameters:
- SDK version 2
- Session cookie generation enabled
- Locale: en_US
- Android user agent

### API Endpoints
- Token Generation: `https://b-api.facebook.com/method/auth.login`
- Post Sharing: `https://graph.facebook.com/v13.0/me/feed` (Graph API v13.0)

### Performance
- **Multi-threaded mode**: Can handle 10-50 concurrent shares
- **Single-threaded mode**: Sequential sharing with 0.5s delay
- **Recommended settings**: 10-20 workers for balanced performance
- **Higher workers**: Faster but may trigger rate limits

## Notes
- This is a CLI application designed to run in a terminal environment
- The application uses Rich library for enhanced terminal UI
- All credentials are processed locally and not stored
