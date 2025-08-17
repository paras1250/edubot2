# EduBot Vercel Deployment Guide

## Prerequisites

1. **Database Setup**: You'll need a cloud database service since Vercel doesn't support persistent MySQL connections. Recommended options:
   - **PlanetScale** (MySQL-compatible, serverless)
   - **Railway** (MySQL/PostgreSQL)
   - **Supabase** (PostgreSQL)
   - **Neon** (PostgreSQL)

2. **Environment Variables**: You'll need to set these in your Vercel project settings.

## Step-by-Step Deployment

### 1. Database Setup
Choose one of the database services above and create a new database. Get your connection string.

### 2. Vercel Project Setup
1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "New Project"
3. Import your GitHub repository
4. Configure the project settings:
   - **Framework Preset**: Other
   - **Root Directory**: `./` (leave empty)
   - **Build Command**: Leave empty (Vercel will auto-detect)
   - **Output Directory**: Leave empty

### 3. Environment Variables
In your Vercel project settings, add these environment variables:

```
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=your-database-connection-string
GOOGLE_API_KEY=your-gemini-api-key
```

### 4. Database Migration
After deployment, you'll need to run database migrations. You can do this by:
1. Adding a temporary route to run migrations
2. Or using a database management tool to run the SQL scripts

### 5. Deploy
Click "Deploy" and wait for the build to complete.

## Important Notes

### SocketIO Limitation
- The current deployment uses regular HTTP requests instead of SocketIO
- Real-time features will work with polling instead of WebSocket connections
- This is necessary because Vercel's serverless functions don't support persistent WebSocket connections

### Database Connection
- Use connection pooling optimized for serverless environments
- The configuration has been updated to work with cloud databases
- Make sure your database service supports the connection limits

### File Uploads
- File uploads will work but files won't persist between function invocations
- Consider using cloud storage (AWS S3, Cloudinary) for file uploads

## Troubleshooting

### Common Issues

1. **Build Fails**: Check the build logs in Vercel dashboard
2. **Database Connection**: Ensure your DATABASE_URL is correct and accessible
3. **Environment Variables**: Make sure all required variables are set
4. **Memory/Timeout**: The configuration includes increased limits for serverless functions

### Debugging
- Check Vercel function logs in the dashboard
- Use the "Functions" tab to see individual function performance
- Monitor database connection errors

## Post-Deployment

1. **Test the Application**: Visit your deployed URL and test all features
2. **Monitor Performance**: Use Vercel analytics to monitor function performance
3. **Set up Custom Domain**: Configure your custom domain in Vercel settings
4. **Database Backup**: Set up regular backups for your cloud database

## Files Modified for Deployment

- `vercel.json`: Vercel configuration
- `vercel_app.py`: WSGI entry point for Vercel
- `config/config.py`: Updated production configuration
- `.vercelignore`: Excludes unnecessary files
- `runtime.txt`: Specifies Python version
