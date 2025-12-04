from ai_career_advisor.app import create_app 
from ai_career_advisor.core.logger import logger


app = create_app()

@app.get('/health')
async def health_check():
    logger.info("health checking")
    return {
        "status": 'ok',
        "message": "Backend running succesfully ✅"
    }
