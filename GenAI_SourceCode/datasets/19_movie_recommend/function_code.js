const { BotFrameworkAdapter } = require('botbuilder');
const axios = require('axios');

// Bot credentials from environment variables
const adapter = new BotFrameworkAdapter({
    appId: process.env.MicrosoftAppId,
    appPassword: process.env.MicrosoftAppPassword
});

// BTP endpoint
const BTP_ENDPOINT = 'https://ats-movie-recommend-fancy-serval-ik.cfapps.us10-001.hana.ondemand.com/recommend';

module.exports = async function (context, req) {
    // Process Bot Framework activity
    await adapter.processActivity(req, context.res, async (turnContext) => {
        if (turnContext.activity.type === 'message') {
            const userMessage = turnContext.activity.text;
            
            try {
                // Call BTP endpoint
                const response = await axios.post(BTP_ENDPOINT, {
                    query: userMessage,
                    user_id: turnContext.activity.from.id
                }, {
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    timeout: 30000
                });
                
                // Send response back to user
                const botReply = response.data.recommendation || response.data.response || 'No recommendation available';
                await turnContext.sendActivity(botReply);
                
            } catch (error) {
                console.error('BTP API Error:', error);
                await turnContext.sendActivity('Sorry, I encountered an error processing your request. Please try again.');
            }
        } else if (turnContext.activity.type === 'conversationUpdate') {
            // Welcome message when bot is added
            if (turnContext.activity.membersAdded) {
                for (const member of turnContext.activity.membersAdded) {
                    if (member.id !== turnContext.activity.recipient.id) {
                        await turnContext.sendActivity('Hello! I\'m your Gen AI recommendation bot. Ask me for movie recommendations!');
                    }
                }
            }
        }
    });
};