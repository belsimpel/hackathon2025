# 📦 Gomibo Hackathon

This repository provides minimal **backend and frontend boilerplates** to help teams quickly start building their hackathon project.
Each stack is intentionally lightweight so you can add your own logic and structure during development.

You are free to pick **any stack** included here: PHP, Python, Vue, or React.

---

# 🗂 Project Structure

```
/
├── boilerplate/
│   ├── python/              # Python backend boilerplate (OOP + FastAPI skeleton)
│   ├── php/                 # PHP backend boilerplate (OOP + minimal router)
│   └── frontend/
│       ├── vue/             # Minimal Vue debug UI
│       └── react/           # Minimal React debug UI
└── README.md
```

---

# 🚀 Backend Setup

## 🐍 Python — `boilerplate/python/`

This folder contains:

* Empty classes (models, repositories, services)
* A minimal FastAPI router with placeholder controllers

### Run the Python backend

1. Go to the folder:

```bash
cd boilerplate/python
```

2. Install dependencies:

```bash
pip install fastapi uvicorn
```

3. Start the server:

```bash
uvicorn app:app --reload
```

4. Visit:

* API root: [http://localhost:8000](http://localhost:8000)
* Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)

You can now start implementing logic inside the class files and controllers.

---

## 🐘 PHP — `boilerplate/php/`

This folder contains:

* Empty classes (models, repositories, services)
* A minimal router in `public/index.php`
* Controllers returning simple placeholder responses

### Run the PHP backend

1. Go to the folder:

```bash
cd boilerplate/php
```

2. Start the built-in PHP server:

```bash
php -S localhost:8000 -t public
```

3. Visit:

* [http://localhost:8000/products](http://localhost:8000/products)
* [http://localhost:8000/cart](http://localhost:8000/cart)
* [http://localhost:8000/cart/add](http://localhost:8000/cart/add)
* [http://localhost:8000/checkout](http://localhost:8000/checkout)

You can now begin implementing the actual backend logic.

---

# 🌐 Frontend Setup

Both frontends are **pure HTML files** using CDN-based Vue/React, so no build tools are needed.

## 🟩 Vue — `boilerplate/frontend/vue/`

1. Open:

```
boilerplate/frontend/vue/index.html
```

2. If your backend runs on a different host/port, edit:

```js
const API_BASE = "http://localhost:8000";
```

This UI provides basic buttons to test your backend endpoints.

---

## 🟦 React — `boilerplate/frontend/react/`

1. Open:

```
boilerplate/frontend/react/index.html
```

2. Adjust the backend URL if needed:

```js
const API_BASE = "http://localhost:8000";
```

This UI is also a simple endpoint tester useful during development.

---

# 🧩 Next Steps

After setup, teams will typically:

* Fill in backend classes (models, repositories, services)
* Replace placeholder JSON in controllers
* Build out frontend pages based on the API

You can use the debug UIs during development or replace them with your final frontend.

---

# 🎉 Have fun building!

These boilerplates are here to help you move quickly — customize anything you like and build your own solution on top.
