# MarciaChart - AI Chat Application

A Django-based chat application that integrates with an AI API to provide ChatGPT-like functionality.

## Features

- User authentication (login/register)
- Chat history storage
- Real-time chat interface
- Modern and responsive UI
- SQLite database for data storage

## Local Development Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with the following content:
   ```
   API_KEY=your_api_key_here
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   ```

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

8. Access the application at `http://127.0.0.1:8000`

## Production Deployment

### Prerequisites
- Ubuntu server
- Nginx
- Python 3.10+
- Git

### Deployment Steps

1. Install system dependencies:
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-dev nginx git
   ```

2. Create project directory:
   ```bash
   sudo mkdir /var/www/marciachart
   sudo chown $USER:$USER /var/www/marciachart
   ```

3. Clone the repository:
   ```bash
   cd /var/www/marciachart
   git clone <repository-url> .
   ```

4. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

5. Install production dependencies:
   ```bash
   pip install -r requirements-prod.txt
   ```

6. Create production `.env` file:
   ```bash
   nano .env
   ```
   Add:
   ```
   DEBUG=False
   SECRET_KEY=your-secure-secret-key
   API_KEY=your-api-key
   ALLOWED_HOSTS=your-domain.com
   ```

7. Collect static files:
   ```bash
   python manage.py collectstatic
   ```

8. Configure Gunicorn:
   ```bash
   sudo cp gunicorn.service /etc/systemd/system/
   sudo systemctl start gunicorn
   sudo systemctl enable gunicorn
   ```

9. Configure Nginx:
   ```bash
   sudo cp marciachart.nginx.conf /etc/nginx/sites-available/marciachart
   sudo ln -s /etc/nginx/sites-available/marciachart /etc/nginx/sites-enabled
   sudo nginx -t
   sudo systemctl restart nginx
   ```

10. Set up SSL with Let's Encrypt:
    ```bash
    sudo apt install certbot python3-certbot-nginx
    sudo certbot --nginx -d your-domain.com
    ```

### Maintenance

- Check Gunicorn status:
  ```bash
  sudo systemctl status gunicorn
  ```

- Check Nginx status:
  ```bash
  sudo systemctl status nginx
  ```

- View logs:
  ```bash
  sudo journalctl -u gunicorn
  sudo tail -F /var/log/nginx/error.log
  ```

## Project Structure

- `marciachart/` - Main project configuration
- `chat/` - Chat application
  - `models.py` - Database models
  - `views.py` - View functions
  - `urls.py` - URL routing
- `templates/` - HTML templates
  - `base.html` - Base template
  - `chat/` - Chat-related templates
  - `registration/` - Authentication templates

## Security Notes

- Never commit your `.env` file
- Keep your API key secure
- Use strong passwords
- The application uses Django's built-in security features
- Enable HTTPS in production
- Regularly update dependencies
- Monitor server logs 