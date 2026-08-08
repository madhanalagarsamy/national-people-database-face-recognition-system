# National People Database & Face Recognition System

A desktop application built using **Python**, **Tkinter (ttk)**, **SQLite3**, **OpenCV**, and **Facial Recognition** techniques for managing citizen identity records, capturing biometric facial images, and verifying identity via webcam or uploaded images.

> 🔒 **Educational Project Notice**: This software is built solely for educational and college demonstration purposes. It uses fictional sample data and must not represent a real database.

---

## Key Features

- **Secure Login Authentication**: Password-protected access with default admin credentials pre-configured (`admin` / `admin123`).
- **Executive Dashboard**: System overview displaying metric summary cards (Total Citizens, Gender Breakdown, Biometric Recognition Attempts).
- **Citizen Registration**: Full profile registration with input validation (ID, Name, Age, Gender, DOB, Address, Phone, Email, National ID).
- **Facial Capture Engine**: Embedded camera feed inside Tkinter with real-time face detection bounding box, frame capture, preview, recapture, and file upload options.
- **Biometric Face Recognition**: Dual-engine recognition matching registered citizens against live camera frames or uploaded test photos with match confidence percentages.
- **Citizen Directory & Search**: Live multi-criteria filter by ID, Name, or National ID, with interactive Treeview table and complete profile detail cards.
- **Record Updates & Deletion**: Update contact information or replace photos; safely delete records with database and file cleanup.
- **Analytics & Audit Reports**: Reports module summarizing gender demographics, recognition accuracy percentages, and real-time audit logs.

---

## Technology Stack

- **Language**: Python 3.12+
- **GUI Framework**: Tkinter (ttk) with custom modern styling (Segoe UI, custom palette)
- **Database**: SQLite3 (`database/citizens.db`)
- **Computer Vision**: OpenCV (`opencv-python`)
- **Image Processing**: Pillow (PIL)
- **Numerical Processing**: NumPy

---

## Project Structure

```
NationalPeopleDatabase/
│── main.py              # Application entry point & launcher
│── database.py          # SQLite database connection & CRUD operations
│── config.py            # Global configuration, constants, and color palette
│
│── login.py             # User authentication window
│── dashboard.py         # Executive dashboard & navigation sidebar
│
│── register.py          # Citizen registration form
│── search.py            # Citizen search directory & profile viewer
│── update.py            # Profile update module
│── delete.py            # Record deletion & file cleanup module
│
│── capture_face.py      # Facial image capture module
│── recognize_face.py    # Biometric face recognition engine
│
│── reports.py           # Analytics dashboard & audit logs
│
│── utils/
│      └── face_utils.py # Face detection, encoding & distance utilities
│
│── database/
│      └── citizens.db   # SQLite database file (auto-created)
│
│── images/
│      └── citizen_photos/ # Facial image store (auto-created)
│
│── icons/              # Application icon assets
│
└── README.md            # Project documentation
```

---

## Database Design

### Table: `citizens`

| Column | Type | Constraints |
|--------|------|-------------|
| `citizen_id` | INTEGER | PRIMARY KEY |
| `name` | TEXT | NOT NULL |
| `age` | INTEGER | NOT NULL |
| `gender` | TEXT | NOT NULL |
| `dob` | TEXT | NOT NULL |
| `address` | TEXT | NOT NULL |
| `phone` | TEXT | NOT NULL |
| `national_id` | TEXT | UNIQUE, NOT NULL |
| `email` | TEXT | NOT NULL |
| `photo_path` | TEXT | NOT NULL |
| `created_at` | TEXT | NOT NULL |

---

## Installation & Running

1. **Install Dependencies**:
   ```bash
   pip install opencv-python pillow numpy
   ```

2. **Run Application**:
   ```bash
   python main.py
   ```

3. **Default Admin Login**:
   - **Username**: `admin`
   - **Password**: `admin123`
