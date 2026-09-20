# QueueKiller - Skip the line. Live your life. ⚡
**Built in:**  Kerala

### The Real Problem
Every day  we waste 20-30 mins standing in physical queues - canteen, xerox shop, clinic, fees office. In these days heat, you can't leave the line or you lose your spot. If you go to use the loo , your turn is gone.

QueueKiller converts physical queue to digital. Take a token Q001 from phone, see live board, know exactly how many are ahead and your wait time. Wait anywhere - shop will call you when it's your turn.

This is not another to-do app. This solves a real, physical, daily pain point for 1000s of students.

### Features
- 🎫 **Digital Token System** - Get Q001, Q002 instantly from phone
- 📺 **Live Board** - See who's being served NOW with pulsing animation
- ⏱️ **Wait Time Prediction** - 2 mins per person, know exact wait
- 📍 **Multi-location** - Canteen, Xerox, Clinic, Fees Office, Bus Counter
- 😎 **Mood Tags** - Chill, Normal, Urgent
- 🔧 **Owner Controls** - Call Next, Clear All, Add Demo data
- 💡 **Smart Tips** - If wait >6 mins, "Go grab tea, we'll hold spot"
- 🎨 **Cool UI** - Glassmorphism cards, gradients, Space Grotesk font

### Tech Stack
- Backend: Python Flask
- Frontend: HTML, CSS (Glassmorphism), JavaScript
- Hosting: Hack Club Nest (non-sleeping, always live) + GitHub Pages backup
- No database needed - in-memory queue (perfect for small shops)
- Zero cost, zero hardware

### How It Works
1. Student enters name + selects place (e.g., College Canteen)
2. Gets token Q001 instantly
3. Live board shows: NOW SERVING Q001, Q002 is next (3 mins)
4. Student waits anywhere, watches live board
5. Shop owner clicks "Call Next" - next token gets notified

### How to Run Locally
```bash
git clone https://github.com/Mireya-examclarity/queuekiller
cd queuekiller
pip install -r requirements.txt
python app.py
