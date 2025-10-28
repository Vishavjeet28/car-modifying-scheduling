# 🌐 ngrok Setup Guide for CarModX

## Quick Start

### Step 1: Get Your ngrok Authtoken

1. Sign up for free at: https://dashboard.ngrok.com/signup
2. Get your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken
3. Copy the authtoken (looks like: `2abc123def456ghi789jkl012mno345_6pqrst7uvwx8yz`)

### Step 2: Authenticate ngrok

Run this command with YOUR authtoken:
```bash
cd "/Users/vishavjeetsingh/untitled folder/untitled folder/car-modification-scheduling "
./ngrok config add-authtoken YOUR_AUTHTOKEN_HERE
```

### Step 3: Start Your Django Server

Open a terminal and run:
```bash
cd "/Users/vishavjeetsingh/untitled folder/untitled folder/car-modification-scheduling "
source .venv/bin/activate
python manage.py runserver 8000
```

**Keep this terminal running!**

### Step 4: Start ngrok Tunnel

Open a NEW terminal and run:
```bash
cd "/Users/vishavjeetsingh/untitled folder/untitled folder/car-modification-scheduling "
./ngrok http 8000
```

### Step 5: Get Your Public URL

After running ngrok, you'll see output like:
```
Session Status                online
Account                       Your Name (Plan: Free)
Version                       3.32.0
Region                        United States (us)
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abcd-1234-5678.ngrok-free.app -> http://localhost:8000
```

**Your public URL is the one after "Forwarding"**: `https://abcd-1234-5678.ngrok-free.app`

## 🎯 Usage

### Share Your Project:
- Send the ngrok URL to anyone: `https://your-unique-url.ngrok-free.app`
- They can access your project from anywhere in the world
- No need for deployment!

### Monitor Traffic:
- Open: http://127.0.0.1:4040
- See all requests in real-time
- Replay requests
- Inspect request/response details

## ⚠️ Important Notes

1. **Free Plan Limitations:**
   - Random URL each time you restart ngrok
   - Session expires after 2 hours
   - Limited to 1 tunnel at a time
   - Shows ngrok warning page before accessing your site

2. **Security:**
   - Don't share sensitive data
   - Anyone with the URL can access your site
   - Stop ngrok when done: Press `Ctrl+C`

3. **Django Settings:**
   - Already configured ALLOWED_HOSTS for ngrok
   - No additional changes needed

## 🚀 Quick Commands

### Start Everything:
```bash
# Terminal 1: Django Server
cd "/Users/vishavjeetsingh/untitled folder/untitled folder/car-modification-scheduling "
source .venv/bin/activate
python manage.py runserver 8000

# Terminal 2: ngrok Tunnel
cd "/Users/vishavjeetsingh/untitled folder/untitled folder/car-modification-scheduling "
./ngrok http 8000
```

### Stop Everything:
- Terminal 1: Press `Ctrl+C` (stops Django)
- Terminal 2: Press `Ctrl+C` (stops ngrok)

## 🎨 Custom Domain (Optional - Paid)

For a custom domain like `myapp.ngrok.app`:
1. Upgrade to ngrok paid plan
2. Run: `./ngrok http 8000 --domain=myapp.ngrok.app`

## 🔧 Troubleshooting

### "ERR_NGROK_3200" or URL doesn't work:
- Check Django server is running on port 8000
- Verify ngrok is pointing to port 8000
- Check ALLOWED_HOSTS in settings.py

### "Invalid authtoken":
- Re-run: `./ngrok config add-authtoken YOUR_TOKEN`
- Make sure you copied the full token

### "Tunnel not found":
- Restart ngrok
- Check if another ngrok session is running

## 📱 Access Your Project

Once ngrok is running, access:
- **Home**: `https://your-url.ngrok-free.app/`
- **Admin Panel**: `https://your-url.ngrok-free.app/admin-panel/`
- **Login**: `https://your-url.ngrok-free.app/accounts/login/`
- **Services**: `https://your-url.ngrok-free.app/services/`

## 💡 Pro Tips

1. **Keep URLs organized**: Save your ngrok URL for the session
2. **Use ngrok inspect**: Monitor at http://127.0.0.1:4040
3. **Test on mobile**: Use the ngrok URL on your phone
4. **Share with clients**: Perfect for demos and reviews

---

**Created**: October 27, 2025
**Project**: CarModX
**ngrok Version**: 3.32.0
