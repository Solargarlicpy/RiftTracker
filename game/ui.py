import os
import time

WIDTH = 60

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def box(lines, title=None):
    inner = WIDTH - 2
    top = f"╔{'═' * inner}╗"
    bot = f"╚{'═' * inner}╝"
    mid = f"╠{'═' * inner}╣"
    out = [top]
    if title:
        out.append(f"║{title.center(inner)}║")
        out.append(mid)
    for line in lines:
        out.append(f"║{str(line):<{inner}}║")
    out.append(bot)
    return "\n".join(out)

def divider(char="─"):
    print(char * WIDTH)

def header(title):
    print(f"\n{'═' * WIDTH}")
    print(f"  {title}")
    print(f"{'═' * WIDTH}")

def slow_print(text, delay=0.025):
    for ch in text:
        print(ch, end='', flush=True)
        time.sleep(delay)
    print()

def prompt(msg=">> "):
    return input(f"\n{msg}").strip()

def menu(options, title=None):
    if title:
        header(title)
    for i, opt in enumerate(options, 1):
        print(f"  [{i}] {opt}")
    while True:
        choice = prompt()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return int(choice) - 1
        print(f"  Enter 1-{len(options)}")

def confirm(msg):
    print(f"\n{msg} [y/n]")
    return prompt().lower().startswith('y')

def pause():
    input("\n  [Press Enter to continue]")

def color(text, code):
    codes = {
        'red': '\033[91m', 'green': '\033[92m', 'yellow': '\033[93m',
        'blue': '\033[94m', 'magenta': '\033[95m', 'cyan': '\033[96m',
        'bold': '\033[1m', 'dim': '\033[2m', 'reset': '\033[0m'
    }
    return f"{codes.get(code,'')}{text}{codes['reset']}"

def hp_bar(current, maximum, width=20):
    pct = current / maximum if maximum > 0 else 0
    filled = int(width * pct)
    bar = '█' * filled + '░' * (width - filled)
    c = 'green' if pct > 0.5 else ('yellow' if pct > 0.25 else 'red')
    return f"[{color(bar, c)}] {current}/{maximum}"

def xp_bar(current, needed, width=20):
    pct = current / needed if needed > 0 else 0
    filled = int(width * pct)
    bar = '▓' * filled + '░' * (width - filled)
    return f"[{color(bar, 'blue')}] {current}/{needed}"
