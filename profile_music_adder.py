#!/usr/bin/env python3

import asyncio
import os
import sys
import yaml
from pyrogram import Client
from pyrogram.file_id import FileId
from pyrogram.raw import functions, types
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text

console = Console()
CONFIG_FILE = "config.yml"
DEFAULT_DELAY = 3


def load_config():
    if not os.path.isfile(CONFIG_FILE):
        console.print(f"[yellow]{CONFIG_FILE} not found! Creating new configuration...[/]")
        api_id = int(Prompt.ask("Enter your API ID", default="1234567"))
        api_hash = Prompt.ask("Enter your API Hash")
        phone = Prompt.ask("Enter your phone number (with country code)")
        cfg = {
            "api_id": api_id,
            "api_hash": api_hash,
            "phone": phone,
            "chat_id": -1000000000000,
            "start_msg": 1,
            "end_msg": 100,
            "delay": DEFAULT_DELAY,
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            yaml.dump(cfg, f, sort_keys=False)
        return cfg

    with open(CONFIG_FILE, encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        yaml.dump(cfg, f, sort_keys=False)


async def _real_gen_session(cfg: dict) -> str:
    async with Client(
        "my_account",
        api_id=cfg["api_id"],
        api_hash=cfg["api_hash"],
        phone_number=cfg["phone"],
        workdir=".",
    ) as app:
        me = await app.get_me()
        ss = await app.export_session_string()

    banner = Text.from_markup(
        f"[bold green]Logged-in successfully as {me.first_name} "
        f"(@{me.username}) – let's make your music shelf nicer![/]"
    )
    console.print(Panel(banner, expand=False))
    return ss


def generate_session_string() -> str:
    cfg = load_config()

    try:
        loop = asyncio.get_running_loop()
        console.print("[red]Error: Cannot generate session string while event loop is running.[/]")
        console.print("[yellow]Please run this script from a regular Python environment (not Jupyter/IPython).[/]")
        console.print("[yellow]Or generate the session string separately and add it to config.yml manually.[/]")
        sys.exit(1)
    except RuntimeError:
        return asyncio.run(_real_gen_session(cfg))


async def generate_session_string_async(cfg: dict) -> str:
    return await _real_gen_session(cfg)


def setup_configuration():
    cfg = load_config()

    if not cfg.get("session_string"):
        console.print("[cyan]Generating session string...[/]")
        
        try:
            asyncio.get_running_loop()
            console.print("[red]Cannot generate session automatically in this environment.[/]")
            console.print("[yellow]Please either:[/]")
            console.print("[yellow]1. Run this script from command line (not Jupyter/IPython)[/]")
            console.print("[yellow]2. Or manually add your session string to config.yml[/]")
            
            manual_session = Prompt.ask("Enter session string manually (or press Enter to exit)", default="")
            if not manual_session.strip():
                console.print("[red]Session string required. Exiting.[/]")
                sys.exit(1)
            cfg["session_string"] = manual_session.strip()
            
        except RuntimeError:
            cfg["session_string"] = generate_session_string()
            
        save_config(cfg)
        console.print("[green]Session string saved to config.yml[/]")

    if Confirm.ask("Do you want to customize the settings?", default=False):
        console.print("[cyan]Current settings:[/]")
        console.print(f"  Chat ID: {cfg.get('chat_id', 'Not set')}")
        console.print(f"  Start message: {cfg.get('start_msg', 1)}")
        console.print(f"  End message: {cfg.get('end_msg', 100)}")
        console.print(f"  Delay: {cfg.get('delay', DEFAULT_DELAY)} seconds")

        if Confirm.ask("Change chat ID?"):
            cfg["chat_id"] = int(Prompt.ask("Enter chat ID", default=str(cfg.get("chat_id", -1000000000000))))
        if Confirm.ask("Change start message ID?"):
            cfg["start_msg"] = int(Prompt.ask("Enter start message ID", default=str(cfg.get("start_msg", 1))))
        if Confirm.ask("Change end message ID?"):
            cfg["end_msg"] = int(Prompt.ask("Enter end message ID", default=str(cfg.get("end_msg", 100))))
        if Confirm.ask("Change delay between adds?"):
            cfg["delay"] = int(Prompt.ask("Enter delay in seconds", default=str(cfg.get("delay", DEFAULT_DELAY))))
        save_config(cfg)
        console.print("[green]Settings updated![/]")

    return cfg


async def add_audio_to_profile(app: Client, audio) -> bool:
    try:
        decoded = FileId.decode(audio.file_id)
        await app.invoke(
            functions.account.SaveMusic(
                id=types.InputDocument(
                    id=decoded.media_id,
                    access_hash=decoded.access_hash,
                    file_reference=decoded.file_reference,
                ),
                unsave=False,
            )
        )
        return True
    except Exception as e:
        console.print(f"[red]Failed to add: {e}[/]")
        return False


async def main():
    cfg = setup_configuration()

    if cfg.get("chat_id") == -1000000000000:
        console.print("[red]Please set a valid chat ID in the configuration[/]")
        sys.exit(1)

    CHAT_ID = cfg["chat_id"]
    START_MSG = cfg["start_msg"]
    END_MSG = cfg["end_msg"]
    DELAY = cfg["delay"]

    console.print(f"[cyan]Starting with settings:[/]")
    console.print(f"  Chat ID: {CHAT_ID}")
    console.print(f"  Messages: {START_MSG}–{END_MSG}")
    console.print(f"  Delay: {DELAY} seconds")

    if not Confirm.ask("Continue?"):
        console.print("[yellow]Operation cancelled[/]")
        return

    async with Client(
        "my_account",
        api_id=cfg["api_id"],
        api_hash=cfg["api_hash"],
        session_string=cfg["session_string"],
        workdir=".",
    ) as app:

        console.print(f"[cyan]Fetching messages {START_MSG}–{END_MSG}…[/]")
        messages = await app.get_messages(CHAT_ID, list(range(START_MSG, END_MSG + 1)))

        added = skipped = 0
        for msg in messages:
            if not msg or not msg.audio:
                skipped += 1
                console.print(f"[dim]⚠️  {msg.id if msg else 'N/A'}  skipped (no audio)[/]")
                continue

            ok = await add_audio_to_profile(app, msg.audio)
            if ok:
                console.print(f"[green]✅  {msg.id}  added[/]")
                added += 1
            else:
                console.print(f"[dim]⚠️  {msg.id}  skipped[/]")
                skipped += 1

            await asyncio.sleep(DELAY)

        console.print(f"[green]Completed! Added: {added}, Skipped: {skipped}[/]")


async def session_generator_main():
    cfg = load_config()
    session_string = await generate_session_string_async(cfg)
    cfg["session_string"] = session_string
    save_config(cfg)
    console.print("[green]Session string generated and saved to config.yml[/]")


if __name__ == "__main__":
    try:
        if sys.platform.startswith("win"):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        if len(sys.argv) > 1 and sys.argv[1] == "--generate-session":
            asyncio.run(session_generator_main())
        else:
            asyncio.run(main())
            
    except KeyboardInterrupt:
        console.print("\n[bold red]Aborted by user[/]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/]")
