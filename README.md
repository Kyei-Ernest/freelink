Freelink API
============

A REST API for a freelance job marketplace, built with **aDjango REST Framework**.  
It provides authentication, contracts, job management, messaging, payments, and more — making it easy to build Upwork/Fiverr-like platforms.

Table of Contents
--------------------
- [Overview]
- [Features]
- [Tech Stack]
- [Getting Started]
- [API Documentation]
- [Contributing]
- [License]


Overview
--------
Freelink is a backend system that powers freelance job marketplaces.  
It allows clients to post jobs, create contracts, and manage milestones, while **freelancers** can apply, communicate, and get paid securely.

This project is designed to be developer-friendly and can be integrated with any frontend framework (React, Vue, Angular, etc.).


Features
-----------
- Authentication & Authorization (JWT-based)  
- User Profiles (Clients & Freelancers)  
- Job Posting & Applications  
- Contracts & Milestones  
- Messaging System (Chat between users)  
- Wallet & Payments Integration  
- Audit Trail (Track contract and transaction history)  



Tech Stack
-------------
- Backend: Django, Django REST Framework  
- Database: SQLite for now  
- Authentication: JWT (via `djangorestframework-simplejwt`)  
- Payments: (Paystack)  


Getting Started
------------------

1. Clone the repository
```bash
git clone https://github.com/your-username/freelink-api.git
cd freelink-api
```

2. Set up environment  
  SECRET_KEY=your-secret-key
  DEBUG=True
  ALLOWED_HOSTS=127.0.0.1,localhost


3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Apply migrations
```bash
python manage.py migrate
```

5. Run server
```bash
python manage.py runserver
```


API Documentation
--------------------
Full API reference with endpoints, request/response examples, and error handling:  

[API Documentation](API.pdf)


Contributing
---------------
Contributions are welcome! To get started:

1. Fork the repo  
2. Create your feature branch (`git checkout -b feature-name`)  
3. Commit your changes (`git commit -m "Add feature"`)  
4. Push to the branch (`git push origin feature-name`)  
5. Open a Pull Request  


License
----------
This project is licensed under the MIT License.  
Feel free to use, modify, and distribute it.

---
