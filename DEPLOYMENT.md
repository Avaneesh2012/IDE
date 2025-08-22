# Deploying FuturIDE on Render

This guide will help you deploy your FuturIDE application on Render.

## 🚀 Quick Deploy (Recommended)

### Option 1: Deploy with render.yaml (Easiest)

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Add Render deployment configuration"
   git push origin main
   ```

2. **Connect to Render**
   - Go to [render.com](https://render.com) and sign up/login
   - Click "New +" and select "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` file and configure everything

3. **Deploy**
   - Click "Apply" and Render will deploy your application
   - Your app will be available at `https://your-app-name.onrender.com`

### Option 2: Manual Deploy

1. **Create a new Web Service**
   - Go to [render.com](https://render.com) and sign up/login
   - Click "New +" and select "Web Service"
   - Connect your GitHub repository

2. **Configure the service**
   - **Name**: `futuride` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --config gunicorn.conf.py`

3. **Set Environment Variables**
   - `SECRET_KEY`: Generate a secure random key
   - `FLASK_ENV`: `production`
   - `LOG_LEVEL`: `INFO`

4. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy your application

## ⚙️ Environment Variables

Set these in your Render dashboard:

| Variable | Value | Description |
|----------|-------|-------------|
| `SECRET_KEY` | `your-secret-key` | Secret key for Flask sessions |
| `FLASK_ENV` | `production` | Environment mode |
| `LOG_LEVEL` | `INFO` | Logging level |
| `PORT` | `8000` | Port (Render sets this automatically) |

## 🔧 Configuration Files

### render.yaml
This file tells Render how to deploy your application:
```yaml
services:
  - type: web
    name: futuride
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.16
      - key: SECRET_KEY
        generateValue: true
      - key: FLASK_ENV
        value: production
```

### gunicorn.conf.py
Production WSGI server configuration optimized for Render.

### Procfile
Alternative deployment method for platforms that support it.

### runtime.txt
Specifies the Python version for deployment.

## 🌐 Custom Domain (Optional)

1. **Add Custom Domain**
   - Go to your service settings in Render
   - Click "Custom Domains"
   - Add your domain (e.g., `futuride.yourdomain.com`)

2. **Configure DNS**
   - Add a CNAME record pointing to your Render URL
   - Wait for DNS propagation (can take up to 24 hours)

## 📊 Monitoring

### Health Checks
- Render automatically checks your app at the root path (`/`)
- If the health check fails, Render will restart your service

### Logs
- View logs in the Render dashboard
- Logs are also available via the Render CLI

### Metrics
- Monitor CPU, memory, and request metrics
- Set up alerts for performance issues

## 🔒 Security Considerations

### Production Settings
- `SESSION_COOKIE_SECURE = True` (HTTPS only)
- `SESSION_COOKIE_HTTPONLY = True` (XSS protection)
- `SESSION_COOKIE_SAMESITE = 'Lax'` (CSRF protection)

### Environment Variables
- Never commit secrets to your repository
- Use Render's environment variable system
- Generate a strong `SECRET_KEY`

## 🚨 Troubleshooting

### Common Issues

1. **Build Fails**
   - Check that all dependencies are in `requirements.txt`
   - Verify Python version compatibility
   - Check build logs for specific errors

2. **App Won't Start**
   - Verify the start command is correct
   - Check that the app listens on the correct port
   - Review application logs

3. **500 Errors**
   - Check application logs
   - Verify environment variables are set
   - Test locally with production settings

### Debug Commands

```bash
# Test locally with production settings
export FLASK_ENV=production
export SECRET_KEY=your-test-key
python app.py

# Test with Gunicorn locally
gunicorn app:app --config gunicorn.conf.py
```

## 📈 Scaling

### Free Tier Limitations
- Sleeps after 15 minutes of inactivity
- Limited to 750 hours per month
- 512MB RAM, 0.1 CPU

### Paid Plans
- Always-on service
- More resources and bandwidth
- Custom domains with SSL
- Team collaboration features

## 🔄 Continuous Deployment

Render automatically deploys when you push to your main branch. To disable:

1. Go to your service settings
2. Toggle "Auto-Deploy" off
3. Deploy manually when needed

## 📞 Support

- **Render Documentation**: [docs.render.com](https://docs.render.com)
- **Render Support**: Available in the dashboard
- **Community**: [Render Community](https://community.render.com)

---

Your FuturIDE will be live at `https://your-app-name.onrender.com` once deployed! 🎉 