# Web Application Exercise

A little exercise to build a web application following an agile development process. See the [instructions](instructions.md) for more detail.

## Product vision statement

A streamlined mobile app that lets users log, rate, and track their seltzer consumption over time to discover personal favorites and monitor their bubbly habits.

## User stories

As a consumer of seltzer, I want to track how much I drink so that I can calculate how much I spend.

As a consumer of seltzer, I want to track the brands I drink so I can determine my favorite brand.

As a consumer of seltzer, I want to track the flavors I drink so I know which flavors I enjoy most and can predict what I’ll enjoy in the future.

As a consumer of seltzer, I want to share my preferences so producers can see the flavors and brands I enjoy and improve their quality.

As a consumer of seltzer, I want to share the flavors I enjoy most so my friends can try them.

As a consumer of seltzer, I want to create my own flavor ideas and recommend them so companies can see what customers are demanding.

As a consumer of seltzer, I want to rate the bubbliness (carbonation level) so I can determine how much carbonation I prefer.

As a seltzer connoisseur, I want to see other consumers’ preferences so I know which new seltzers I might enjoy.

As a producer of seltzer, I want to track flavor preferences so I can understand consumer preferences.

As a producer of seltzer, I want to see whether people drink more from bottles or cans so I can determine what consumers prefer.

As a producer of seltzer, I want to track purchases by location so I can see preferences across different areas of the world.

## Steps necessary to run the software

### Prerequisites
- Python 3.7 or higher
- pip3 (Python package manager)
- MongoDB (local installation or cloud service)

### Quick Setup (Automated)
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd 2-web-app-teamseltzer
   ```

2. Run the setup script:
   ```bash
   python3 setup.py
   ```

3. Update the `.env` file with your MongoDB credentials:
   ```bash
   # Edit .env file
   MONGODB_URI=mongodb://localhost:27017/seltzertracker
   MONGODB_DATABASE=seltzertracker
   ADMIN_PASSWORD=your_secure_admin_password_here
   SECRET_KEY=your_secret_key_here
   ```

4. Start MongoDB (if running locally):
   ```bash
   mongod
   ```

5. Run the application:
   ```bash
   python3 app.py
   ```

6. Open your browser to: http://localhost:5000

### Manual Setup
If the automated setup doesn't work, follow these manual steps:

1. Install Python dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

2. Create `.env` file from template:
   ```bash
   cp env.example .env
   ```

3. Edit `.env` file with your configuration

4. Start MongoDB and run the application as above

### Default Credentials
- **Admin Password**: `admin123` (change in .env file)
- **First User**: Register a new account through the web interface

### Features Available
- ✅ User registration and authentication
- ✅ Log seltzer consumption with ratings
- ✅ View consumption history with filtering
- ✅ Search seltzers by brand, flavor, or notes
- ✅ User statistics and profile
- ✅ Edit and delete seltzer entries
- ✅ Admin panel for managing brands and flavors
- ✅ Mobile-optimized responsive design

## Task boards
[Task Board 1](https://github.com/orgs/swe-students-fall2025/projects/23)
[Task Board 2](https://github.com/orgs/swe-students-fall2025/projects/73)
