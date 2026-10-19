ANIWAYS FLASK WEBSITE - SETUP GUIDE

1. Install Python 3.10+ from https://www.python.org/downloads/ and tick "Add Python to PATH".
2. Extract AniWays.zip to a folder, for example D:\AniWays.
3. Open that folder in VS Code (File > Open Folder).
4. Open Terminal > New Terminal.
5. Run: py -m venv .venv
6. Activate the environment in Windows CMD: .venv\Scripts\activate
   If using PowerShell: .venv\Scripts\Activate.ps1
7. Install Flask: py -m pip install flask
8. Run the site: py app.py
9. Open your browser at http://127.0.0.1:5000

FEATURES INCLUDED
- Home, Shop, product details, categories/search, product variants, Your Ani cart
- Signup/login demo, checkout with COD, PayMaya, GCash, MariBank, Banks (simulated only)
- Order tracking, notifications, printable parcel receipt, seller/admin status update
- About (What's AniWays?, Our Mission, AniVision, AniGoals), Contact, AniSays sample reviews

IMPORTANT LIMITATIONS
- This is a school-project/demo starter. Accounts, cart, and orders are stored in Flask session cookies and may be lost; this is not production storage or secure authentication.
- Google Sign-In is not connected.
- Payments are simulated; no money is collected and no payment provider is integrated.
- The Seller/Admin page has no admin authentication. Do not deploy publicly as-is.
- Product artwork currently uses emoji placeholders, not generated photographs. Add your own generated images in static/images and update templates to use them.
- Replace sample phone/email/Facebook contact details before publishing.
- Fertilizer and crop-protection products have generic descriptions; verify supplier, label, registration, and applicable rules before selling.
