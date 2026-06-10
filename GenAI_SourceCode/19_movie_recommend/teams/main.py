import os
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import aiohttp
import uvicorn

# Create FastAPI app
app = FastAPI()

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get configuration from environment variables (with fallback to hardcoded values)
APP_ID = os.getenv("MicrosoftAppId", "")
APP_PASSWORD = os.getenv("MicrosoftAppPassword", "")

# Log configuration on startup (for debugging)
print("=" * 50)
print("Bot Configuration:")
print(f"- App ID: {APP_ID if APP_ID else '❌ NOT SET'}")
print(f"- App Password: {'✓ SET' if APP_PASSWORD else '❌ NOT SET'}")
print(f"- Password length: {len(APP_PASSWORD) if APP_PASSWORD else 0} characters")
print("=" * 50)

# Create adapter settings
SETTINGS = BotFrameworkAdapterSettings(app_id=APP_ID, app_password=APP_PASSWORD)
ADAPTER = BotFrameworkAdapter(SETTINGS)

# Define error handler
async def on_error(context: TurnContext, error: Exception):
    """Error handler for the bot."""
    print(f"\n [on_turn_error] unhandled error: {error}", flush=True)
    
    # Send a message to the user
    try:
        await context.send_activity("The bot encountered an error or bug.")
        
        # Send trace information only in emulator
        if context.activity.channel_id == "emulator":
            await context.send_activity(f"Error details: {str(error)}")
    except Exception as send_error:
        print(f"Error sending error message: {send_error}")

# Set the error handler on the adapter
ADAPTER.on_turn_error = on_error


async def get_movie_recommendations(user_query):
    """Get movie recommendations from the API."""
    api_url = "https://ats-movie-recommend-fancy-serval-ik.cfapps.us10-001.hana.ondemand.com/recommend"
    
    try:
        async with aiohttp.ClientSession() as session:
            headers = {"Content-Type": "application/json"}
            payload = {"query": user_query}
            
            async with session.post(api_url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"API response: {data}")
                    return data
                else:
                    error_text = await response.text()
                    print(f"API error: {response.status} - {error_text}")
                    return {"error": f"API request failed with status {response.status}"}
    except aiohttp.ClientError as e:
        print(f"API connection error: {e}")
        return {"error": f"Could not connect to recommendation service: {str(e)}"}
    except Exception as e:
        print(f"Unexpected error calling API: {e}")
        return {"error": f"Unexpected error: {str(e)}"}
            

async def on_members_added_activity(members_added, turn_context: TurnContext):
    """Handle members added to the conversation."""
    print("Members added activity detected.")
    for member in members_added:
        if member.id != turn_context.activity.recipient.id:
            welcome_message = (
                "Welcome to the Movie Recommendation Bot! 🎬\n\n"
                "Tell me what kind of movie you're looking for, and I'll suggest some options."
            )
            await turn_context.send_activity(welcome_message)


async def async_process_activity(turn_context: TurnContext):
    """Process the incoming activity."""
    print(f"Received activity of type: {turn_context.activity.type}")
    
    if turn_context.activity.type == "message":
        user_text = turn_context.activity.text
        print(f"User message: {user_text}")
        
        # Send typing indicator
        typing_activity = Activity(type="typing")
        await turn_context.send_activity(typing_activity)
        
        # Get movie recommendations
        recommendations = await get_movie_recommendations(user_text)
        
        # Format the response
        if "error" in recommendations:
            response_text = f"Sorry, there was an error: {recommendations['error']}"
        else:
            print(f"Recommendations: {recommendations}")
            
            movies = recommendations.get("recommendations", [])
            if movies:
                response_text = "🎬 Here are some movie recommendations for you:\n\n"
                for i, movie in enumerate(movies[:5], 1):  # Limit to top 5
                    name = movie.get('name', 'Unknown')
                    year = movie.get('year', 'N/A')
                    rating = movie.get('rating', 'N/A')
                    response_text += f"{i}. **{name}** ({year})"
                    if rating != 'N/A':
                        response_text += f" - Rating: {rating}"
                    response_text += "\n"
            else:
                response_text = "No recommendations found. Try describing the type of movie you'd like to watch."
        
        # Send response back to the user
        await turn_context.send_activity(response_text)
        
    elif turn_context.activity.type == "conversationUpdate":
        if turn_context.activity.members_added:
            await on_members_added_activity(turn_context.activity.members_added, turn_context)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "bot": "Movie Recommendation Bot",
        "appId": APP_ID if APP_ID else "not configured",
        "hasPassword": bool(APP_PASSWORD)
    }


@app.get("/api/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "appId": "configured" if APP_ID else "missing",
        "appPassword": "configured" if APP_PASSWORD else "missing",
        "adapter": "initialized"
    }


@app.post("/api/messages")
async def messages(request: Request):
    """Main bot message handler."""
    try:
        # Get the request body as JSON
        body = await request.json()
        print(f"Received request body: {body.get('type', 'unknown type')}")
        
        # Get the authorization header
        auth_header = request.headers.get("Authorization", "")
        


        if not auth_header:
            print("⚠️  WARNING: No Authorization header received")
        else:
            print(f"✓ Authorization header present (length: {len(auth_header)})")
        
        # Create an Activity object from the request body
        activity = Activity().deserialize(body)
        
        # Define the callback to send responses
        async def call_bot(context: TurnContext):
            await async_process_activity(context)
        
        # Process the activity using the adapter
        await ADAPTER.process_activity(activity, auth_header, call_bot)
        
        return Response(status_code=200)
        
    except PermissionError as e:
        # Authentication failed
        print(f"❌ Authentication error: {e}")
        return JSONResponse(
            content={"error": "Authentication failed. Check App ID and Password configuration."},
            status_code=401
        )
    except Exception as e:
        print(f"❌ Error processing activity: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )


if __name__ == "__main__":
    # Start the server
    port = int(os.getenv("PORT", 3978))
    host = os.getenv("HOST", "0.0.0.0")  # Use 0.0.0.0 for Cloud Foundry
    
    print(f"\n🚀 Starting bot on http://{host}:{port}")
    print(f"Messaging endpoint: http://{host}:{port}/api/messages\n")
    
    uvicorn.run(app, host=host, port=port)