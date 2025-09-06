# Telegram Profile Music Adder

A Python tool to automatically add audio tracks from a Telegram channel to your Telegram profile's music section, making your music shelf more organized and visually appealing.

## Features

- 🔐 Secure login with Telegram API
- ⚙️ Easy configuration setup
- 🎵 Batch add music from channels to your profile
- ⏱️ Customizable delay between operations
- 📊 Progress tracking with detailed logs
- 🎨 Beautiful console interface with rich formatting

## Prerequisites

- Python 3.7 or higher
- Telegram API ID and API Hash
- A Telegram account with two-factor authentication (if enabled)

## Setup Instructions

### 1. Create a Virtual Environment

```bash
#  virtual environment
python -m venv venv
venv\Scripts\activate

```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```




### 3. Get Telegram API Credentials

1. Visit https://my.telegram.org/apps
2. Log in with your Telegram account
3. Create a new application to get your API ID and API Hash

### 4. Generate Session String

Run the script with the session generation flag:

```bash
python profile_music_adder.py --generate-session
```

![GET SESSION](https://files.imeow.ir/dl/default/photo_2025-09-06_04-15-10.jpg)


Follow the prompts to:
- Enter your API ID
- Enter your API Hash  
- Enter your phone number (with country code)
- Enter the confirmation code sent to your Telegram account
- Enter your 2FA password (if enabled)

The session string will be automatically saved to your configuration file.

### 5. Configure the Channel Settings

1. Find the channel containing the music you want to add to your profile
2. Get the channel's Chat ID (usually a negative number like -1001234567890)
3. Identify the message IDs that contain the audio files you want to add

Run the script without arguments to configure settings:

```bash
python profile_music_adder.py
```
![CUSTOMIZE](https://files.imeow.ir/dl/default/photo_2025-09-06_04-15-18.jpg)


You'll be prompted to:
- Customize settings (choose 'y')
- Enter the Chat ID of the channel
- Set the start message ID
- Set the end message ID  
- Set the delay between operations (in seconds)

### 6. Run the Script

After configuration, run the script again to start adding music:

```bash
python profile_music_adder.py
```



![ADD TRACKS](https://files.imeow.ir/dl/default/photo_2025-09-06_04-15-23.jpg)



The script will:
1. Connect to your Telegram account
2. Fetch messages from the specified channel and message range
3. Add each audio file to your profile's music section
4. Show progress with emoji indicators (✅ for success, ⚠️ for skipped)

## Important Notes

- Make sure the channel is accessible to your account
- Only messages with audio files will be processed
- Respect Telegram's limits and use appropriate delays
- The script skips non-audio messages automatically
- Your session string is stored in config.yml - keep this file secure

## Troubleshooting

- If you get "Cannot generate session automatically" error, run the script from command line (not IPython/Jupyter)
- For "Chat not found" errors, verify the Chat ID and your access permissions
- If messages are skipped, check if they contain audio files
- For login issues, verify your API credentials and 2FA password

