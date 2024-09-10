# RadMap
![RadMap Dashboard](/images/dashboard.png)
 A web panel in Python that displays real-time radiation levels in mainland Portugal, Azores and Madeira. The dashboard features an interactive map and historical graphs to track radiation data over time for each location.

## Download Files
Clone the repository:
```sh
git clone https://github.com/vostpt/RadMap.git
```

## Configuration
Copy the `.env` file:
```sh
cp .env.example .env
```

**Update the .env and docker-compose.yml for yours credentials**

## Installation
In your folder run:
```sh
sudo docker-compose up --build
```

## Project Structure
```
.
├── app.py
├── assets
│   ├── favicon.ico
│   ├── RADNET_FONTE_LOGO.png
│   ├── style.css
│   └── VOSTPT_LOGO_2023_cores.svg
├── coordinates.py
├── data
│   └── dados.json
├── docker-compose.yml
├── Dockerfile
├── fetch.py
├── README.md
└── requirements.txt
```

## Dashboard
To view the dashboard, access your browser and type the corresponding URL:
```sh
http://<your_machine_ip>:8050/
```

![RadMap Dashboard](/images/dashboard.png)

## Credits
- [VOST Portugal](https://github.com/vostpt)