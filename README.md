# Line Art Animation Project

## Deployment on Render

This project is a Line Art Animation web application built with Flask and deployed on Render.

### Prerequisites

- Python 3.8+
- Flask
- OpenCV
- NumPy
- SciPy
- Pygame

### Local Development

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python app.py
   ```

### Deployment Steps

1. Create a Render account at [render.com](https://render.com)
2. Connect your GitHub repository
3. Create a new Web Service
4. Select Python as the runtime
5. Set the following build settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

### Troubleshooting

- Ensure all dependencies are in `requirements.txt`
- Use `opencv-python-headless` for deployment
- Check Render logs for any deployment issues

### License

[Add your license information here]
